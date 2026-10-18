"""Decky backend for claude-deck. Runs as the normal user (no "root" flag in plugin.json).

- session_status(): is the persistent Claude session (tmux socket "claude") running? Is Claude Code installed?
- session_start(new) / session_new() / session_stop(): control the session from Game Mode (claude-session).
- spools: claude-open-url and claude-notify drop files in ~/.local/state/claude-deck/{open-url,toasts}; the
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
import pty
import signal
import struct
import subprocess
import termios
import time
from pathlib import Path

import decky

TMUX_SOCKET = "claude"
HOME = Path(decky.DECKY_USER_HOME)
STATE = HOME / ".local/state/claude-deck"
URL_SPOOL = STATE / "open-url"
TOAST_SPOOL = STATE / "toasts"
ALIVE = STATE / "decky-alive"
SESSION_CMD = str(HOME / ".local/bin/claude-session")
SPOOL_SECONDS = 0.5
FLUSH_SECONDS = 0.015   # batch output into ~60 events/s at most
MAX_CHUNK = 64 * 1024


def _env():
    uid = os.getuid()
    env = dict(os.environ, HOME=decky.DECKY_USER_HOME, XDG_RUNTIME_DIR=f"/run/user/{uid}",
               DBUS_SESSION_BUS_ADDRESS=f"unix:path=/run/user/{uid}/bus",
               TERM="xterm-256color", COLORTERM="truecolor", LANG=os.environ.get("LANG", "C.UTF-8"))
    env["PATH"] = f"{decky.DECKY_USER_HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin"
    env.pop("TMUX", None)
    return env


def _tmux(*args, timeout=5):
    return subprocess.run(["tmux", "-L", TMUX_SOCKET, *args], env=_env(),
                          capture_output=True, text=True, timeout=timeout)


def _set_winsize(fd, cols, rows):
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", int(rows), int(cols), 0, 0))


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
        pid, fd = pty.fork()
        if pid == 0:  # child: become the tmux client
            try:
                os.execvpe("tmux", ["tmux", "-L", TMUX_SOCKET, "attach-session", "-t", session], _env())
            finally:
                os._exit(127)
        self.pid, self.fd = pid, fd
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


TERM = Terminal()


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


class Plugin:
    async def session_status(self) -> dict:
        try:
            r = _tmux("list-sessions", "-F", "#{session_name}")
            names = r.stdout.split() if r.returncode == 0 else []
        except Exception as e:  # tmux missing, timeout...
            decky.logger.warning("session_status: %s", e)
            names = []
        return {"running": bool(names), "session": names[0] if names else None,
                "claude_installed": _claude_installed(), "scripts_installed": Path(SESSION_CMD).exists()}

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
        decky.logger.info("claude-deck backend started")

    async def _unload(self):
        if SPOOL_TASK:
            SPOOL_TASK.cancel()
        ALIVE.unlink(missing_ok=True)
        TERM.close()
        decky.logger.info("claude-deck backend stopped")
