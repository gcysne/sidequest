"""Decky backend for sidequest. Runs as the normal user (no "root" flag in plugin.json).

- session_status(): is the persistent Claude session (tmux socket "claude") running? Is Claude Code installed?
- session_start(new) / session_new() / session_stop(): control the session from Game Mode (claude-session).
- spools: claude-open-url and claude-notify drop files in ~/.local/state/sidequest/{open-url,toasts}; the
  backend forwards them to the frontend ("open_url" opens Steam's browser, "toast" shows a Steam toast) and
  touches decky-alive so the scripts know the plugin is listening.
- term_*(): a terminal bridge for the panel. term_open() attaches a *new* tmux client to the
  existing session inside a pseudo-terminal; its output is pushed to the frontend with
  decky.emit("term_output", <base64>), keys come back through term_input(). Closing the panel
  only detaches this client: the session keeps running.
"""

import asyncio
import base64
import json
import fcntl
import os
import re
import signal
import struct
import subprocess
import time
from pathlib import Path

import decky

# Decky's bundled Python may lack termios (v3.3.0 ships 3.14 without it), and the pty module imports it.
# Use os.forkpty() (core posix module) and fall back to Linux's TIOCSWINSZ value.
try:
    from termios import TIOCSWINSZ
except ImportError:
    TIOCSWINSZ = 0x5414

TMUX_SOCKET = "claude"
HOME = Path(decky.DECKY_USER_HOME)
STATE = HOME / ".local/state/sidequest"
URL_SPOOL = STATE / "open-url"
TOAST_SPOOL = STATE / "toasts"
ALIVE = STATE / "decky-alive"
SESSION_CMD = str(HOME / ".local/bin/claude-session")
PANEL_OPEN = Path(f"/run/user/{os.getuid()}/sidequest/panel-open")  # claude-notify: skip "finished" toasts
SPOOL_SECONDS = 0.5
CONFIG = HOME / ".config/sidequest/config"
# Panel settings in the config file: (default, min, max)
PANEL_SETTINGS = {"PANEL_WIDTH": (70, 30, 100), "PANEL_FONT_SIZE": (15, 8, 40)}
FLUSH_SECONDS = 0.015   # batch output into ~60 events/s at most
MAX_CHUNK = 64 * 1024


def _env():
    uid = os.getuid()
    env = dict(os.environ, HOME=decky.DECKY_USER_HOME, XDG_RUNTIME_DIR=f"/run/user/{uid}",
               DBUS_SESSION_BUS_ADDRESS=f"unix:path=/run/user/{uid}/bus",
               TERM="xterm-256color", COLORTERM="truecolor", LANG=os.environ.get("LANG", "C.UTF-8"))
    env["PATH"] = f"{decky.DECKY_USER_HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin"
    env.pop("TMUX", None)
    # Decky is a PyInstaller bundle: it points LD_LIBRARY_PATH at its own unpacked libs, which break system
    # programs (v3.3.0's libtinfo needs a newer glibc, so bash fails). Restore the original value, if any.
    orig = env.pop("LD_LIBRARY_PATH_ORIG", None)
    if orig:
        env["LD_LIBRARY_PATH"] = orig
    else:
        env.pop("LD_LIBRARY_PATH", None)
    return env


def _tmux(*args, timeout=5):
    return subprocess.run(["tmux", "-L", TMUX_SOCKET, *args], env=_env(),
                          capture_output=True, text=True, timeout=timeout)


def _set_winsize(fd, cols, rows):
    fcntl.ioctl(fd, TIOCSWINSZ, struct.pack("HHHH", int(rows), int(cols), 0, 0))


class Terminal:
    def __init__(self):
        self.pid = None
        self.fd = None
        self.buf = bytearray()
        self.flush_task = None

    @property
    def alive(self):
        return self.fd is not None

    def open(self, session, cols, rows):
        pid, fd = os.forkpty()
        if pid == 0:  # child: become the tmux client
            try:
                os.execvpe("tmux", ["tmux", "-L", TMUX_SOCKET, "attach-session", "-t", session], _env())
            finally:
                os._exit(127)
        self.pid, self.fd = pid, fd
        try:
            PANEL_OPEN.parent.mkdir(parents=True, exist_ok=True)
            PANEL_OPEN.touch()
        except OSError:
            pass
        _set_winsize(fd, cols, rows)
        os.set_blocking(fd, False)
        asyncio.get_running_loop().add_reader(fd, self._on_readable)

    def _on_readable(self):
        try:
            data = os.read(self.fd, MAX_CHUNK)
        except (BlockingIOError, InterruptedError):
            return
        except OSError:
            data = b""
        if not data:  # client exited (detached, session killed...)
            self.close()
            asyncio.get_running_loop().create_task(decky.emit("term_exit"))
            return
        self.buf += data
        if self.flush_task is None:
            self.flush_task = asyncio.get_running_loop().create_task(self._flush())

    async def _flush(self):
        await asyncio.sleep(FLUSH_SECONDS)
        data, self.buf = bytes(self.buf), bytearray()
        self.flush_task = None
        if data:
            await decky.emit("term_output", base64.b64encode(data).decode())

    def write(self, data: str):
        if self.fd is not None:
            os.write(self.fd, data.encode())

    def resize(self, cols, rows):
        if self.fd is not None:
            _set_winsize(self.fd, cols, rows)
            os.kill(self.pid, signal.SIGWINCH)

    def close(self):
        if self.fd is None:
            return
        try:
            asyncio.get_running_loop().remove_reader(self.fd)
        except Exception:
            pass
        try:
            os.close(self.fd)
        except OSError:
            pass
        try:
            os.kill(self.pid, signal.SIGHUP)
            os.waitpid(self.pid, os.WNOHANG)
        except (ProcessLookupError, ChildProcessError):
            pass
        self.pid = self.fd = None
        PANEL_OPEN.unlink(missing_ok=True)


TERM = Terminal()


def _read_panel_settings():
    """PANEL_* values from ~/.config/sidequest/config (shell syntax; only plain numbers are read)."""
    values = {k: d for k, (d, _, _) in PANEL_SETTINGS.items()}
    try:
        lines = CONFIG.read_text().splitlines()
    except OSError:
        lines = []
    for line in lines:
        m = re.match(r"""\s*(PANEL_[A-Z_]+)\s*=\s*["']?(\d+)%?["']?\s*(#.*)?$""", line)
        if m and m.group(1) in PANEL_SETTINGS:
            _, lo, hi = PANEL_SETTINGS[m.group(1)]
            values[m.group(1)] = min(hi, max(lo, int(m.group(2))))
    return values


def _claude_installed():
    return (HOME / ".local/bin/claude").exists() or any(
        Path(d, "claude").exists() for d in ("/usr/local/bin", "/usr/bin"))


async def _session_cmd(*args, new=False, timeout=30):
    env = _env()
    if new:
        env["CLAUDE_SESSION_NEW"] = "1"
    proc = await asyncio.create_subprocess_exec(SESSION_CMD, *args, env=env,
                                                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return {"ok": False, "error": f"claude-session {' '.join(args)} timed out"}
    if proc.returncode != 0:
        decky.logger.warning("claude-session %s: %s", args, out.decode(errors="replace"))
        return {"ok": False, "error": out.decode(errors="replace").strip()[-300:] or "failed"}
    return {"ok": True}


async def _spool_loop():
    """Forward URLs and toasts dropped by the session's scripts; keep the heartbeat fresh."""
    last_beat = 0.0
    while True:
        try:
            now = time.time()
            if now - last_beat > 5:
                STATE.mkdir(parents=True, exist_ok=True)
                ALIVE.touch()
                last_beat = now
            for f in sorted(URL_SPOOL.glob("*.url")) if URL_SPOOL.is_dir() else []:
                url = f.read_text().strip()
                f.unlink(missing_ok=True)
                if url.startswith(("https://", "http://")):
                    decky.logger.info("open_url %s", url.split("?")[0])
                    await decky.emit("open_url", url)
            for f in sorted(TOAST_SPOOL.glob("*.json")) if TOAST_SPOOL.is_dir() else []:
                try:
                    toast = json.loads(f.read_text())
                except ValueError:
                    toast = None
                f.unlink(missing_ok=True)
                if isinstance(toast, dict):
                    await decky.emit("toast", toast)
        except asyncio.CancelledError:
            raise
        except Exception as e:  # never let the loop die
            decky.logger.warning("spool loop: %s", e)
        await asyncio.sleep(SPOOL_SECONDS)


SPOOL_TASK = None


REPO = "gcysne/sidequest"
UPDATE_COMMAND = f"curl -fsSL https://raw.githubusercontent.com/{REPO}/main/get.sh | bash"
# Same cache as the session-start hook (bin/sidequest-update-check): GitHub is asked at most once a day.
UPDATE_CACHE = Path(decky.DECKY_USER_HOME) / ".local/state/sidequest/update-check.json"
INSTALLED_VERSION = Path(decky.DECKY_USER_HOME) / ".local/lib/sidequest/VERSION"


def _version_key(text: str):
    """Semver order (a release sorts after its pre-releases)."""
    main, _, pre = str(text or "").strip().lstrip("vV").partition("-")
    nums = [int(m.group()) if (m := re.match(r"\d+", x)) else 0 for x in main.split(".")]
    nums = (nums + [0, 0, 0])[:3]
    if not pre:
        return (*nums, 1, ())
    return (*nums, 0, tuple((0, int(x), "") if x.isdigit() else (1, 0, x) for x in pre.split(".")))


def _check_release(force: bool) -> dict:
    """Newest GitHub release, pre-releases included (Sidequest's alpha releases are marked as pre-releases, which
    GitHub's releases/latest ignores)."""
    import urllib.error
    import urllib.request
    try:
        current = INSTALLED_VERSION.read_text().strip() or _version()
    except OSError:
        current = _version()
    try:
        cache = json.loads(UPDATE_CACHE.read_text())
    except (OSError, ValueError):
        cache = {}
    if force or time.time() - cache.get("checked", 0) > 86400 or "url" not in cache:
        cache = {"checked": time.time()}
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases?per_page=10",
                                         headers={"Accept": "application/vnd.github+json", "User-Agent": "sidequest"})
            with urllib.request.urlopen(req, timeout=15) as r:
                rels = [x for x in json.load(r) if not x.get("draft")]
            if rels:
                best = max(rels, key=lambda x: _version_key(x.get("tag_name", "")))
                cache.update(latest=best["tag_name"].lstrip("vV"), url=best.get("html_url", ""),
                             notes=(best.get("body") or "")[:1500])
            else:
                cache.update(url="", error="no release published yet")
        except urllib.error.HTTPError as e:
            cache.update(url="", error="no release published yet" if e.code == 404 else f"GitHub answered {e.code}")
        except (urllib.error.URLError, OSError, ValueError) as e:
            cache.update(url="", error=f"couldn't reach GitHub ({getattr(e, 'reason', e)})")
        try:
            UPDATE_CACHE.parent.mkdir(parents=True, exist_ok=True)
            UPDATE_CACHE.write_text(json.dumps(cache))
        except OSError:
            pass
    out = {k: cache.get(k) for k in ("latest", "url", "notes", "error") if cache.get(k)}
    out.update(current=current, command=UPDATE_COMMAND)
    out["newer"] = bool(out.get("latest")) and _version_key(out["latest"]) > _version_key(current)
    return out


def _version() -> str:
    v = getattr(decky, "DECKY_PLUGIN_VERSION", "")
    if not v:
        try:
            v = json.loads((Path(decky.DECKY_PLUGIN_DIR) / "package.json").read_text()).get("version", "")
        except (OSError, ValueError, AttributeError):
            v = ""
    return v


class Plugin:
    async def plugin_info(self) -> dict:
        return {"version": _version()}

    async def update_check(self, force: bool = False) -> dict:
        return await asyncio.get_running_loop().run_in_executor(None, _check_release, bool(force))

    async def session_status(self) -> dict:
        try:
            r = _tmux("list-sessions", "-F", "#{session_name}")
            names = r.stdout.split() if r.returncode == 0 else []
        except Exception as e:  # tmux missing, timeout...
            decky.logger.warning("session_status: %s", e)
            names = []
        return {"running": bool(names), "session": names[0] if names else None,
                "claude_installed": _claude_installed(), "scripts_installed": Path(SESSION_CMD).exists()}

    async def get_settings(self) -> dict:
        v = _read_panel_settings()
        return {"panel_width": v["PANEL_WIDTH"], "font_size": v["PANEL_FONT_SIZE"]}

    async def session_start(self, new: bool = False) -> dict:
        return await _session_cmd("--ensure", new=new)

    async def session_new(self) -> dict:
        TERM.close()
        return await _session_cmd("--restart-new")

    async def session_stop(self) -> dict:
        TERM.close()
        return await _session_cmd("--stop")

    async def term_open(self, cols: int, rows: int) -> dict:
        status = await self.session_status()
        if not status["running"]:
            return {"ok": False, "error": "no Claude session running"}
        if TERM.alive:
            TERM.resize(cols, rows)
            # make tmux repaint the whole screen for the (new) frontend
            _tmux("refresh-client", "-S")
            return {"ok": True, "reused": True}
        TERM.open(status["session"], cols, rows)
        decky.logger.info("terminal opened (%sx%s) on session %s", cols, rows, status["session"])
        return {"ok": True}

    async def term_input(self, data: str) -> None:
        TERM.write(data)

    async def term_resize(self, cols: int, rows: int) -> None:
        TERM.resize(cols, rows)

    async def term_close(self) -> None:
        TERM.close()
        decky.logger.info("terminal closed")

    async def _main(self):
        global SPOOL_TASK
        SPOOL_TASK = asyncio.get_running_loop().create_task(_spool_loop())
        decky.logger.info("sidequest backend started")

    async def _unload(self):
        if SPOOL_TASK:
            SPOOL_TASK.cancel()
        ALIVE.unlink(missing_ok=True)
        TERM.close()
        decky.logger.info("sidequest backend stopped")
