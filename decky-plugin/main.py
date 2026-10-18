"""Decky backend for claude-deck. Runs as the normal user (no "root" flag in plugin.json).

- session_status(): is the persistent Claude session (tmux socket "claude") running?
- term_*(): a terminal bridge for the panel. term_open() attaches a *new* tmux client to the
  existing session inside a pseudo-terminal; its output is pushed to the frontend with
  decky.emit("term_output", <base64>), keys come back through term_input(). Closing the panel
  only detaches this client: the session keeps running.
"""

import asyncio
import base64
import fcntl
import os
import pty
import signal
import struct
import subprocess
import termios

import decky

TMUX_SOCKET = "claude"
FLUSH_SECONDS = 0.015   # batch output into ~60 events/s at most
MAX_CHUNK = 64 * 1024


def _env():
    uid = os.getuid()
    env = dict(os.environ, HOME=decky.DECKY_USER_HOME, XDG_RUNTIME_DIR=f"/run/user/{uid}",
               TERM="xterm-256color", COLORTERM="truecolor", LANG=os.environ.get("LANG", "C.UTF-8"))
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


class Plugin:
    async def session_status(self) -> dict:
        try:
            r = _tmux("list-sessions", "-F", "#{session_name}")
            names = r.stdout.split() if r.returncode == 0 else []
        except Exception as e:  # tmux missing, timeout...
            decky.logger.warning("session_status: %s", e)
            names = []
        return {"running": bool(names), "session": names[0] if names else None}

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
        decky.logger.info("claude-deck backend started")

    async def _unload(self):
        TERM.close()
        decky.logger.info("claude-deck backend stopped")
