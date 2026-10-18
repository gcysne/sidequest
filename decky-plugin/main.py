"""Decky backend for claude-deck. Runs as the normal user (no "root" flag in plugin.json).

Only reports whether the persistent Claude session (tmux socket "claude") is running.
"""

import os
import subprocess

import decky


def _env():
    uid = os.getuid()
    return dict(os.environ, HOME=decky.DECKY_USER_HOME, XDG_RUNTIME_DIR=f"/run/user/{uid}")


class Plugin:
    async def session_status(self) -> dict:
        try:
            r = subprocess.run(["tmux", "-L", "claude", "has-session"], env=_env(),
                               capture_output=True, timeout=5)
            running = r.returncode == 0
        except Exception as e:  # tmux missing, timeout...
            decky.logger.warning("session_status: %s", e)
            running = False
        return {"running": running}

    async def _main(self):
        decky.logger.info("claude-deck backend started")

    async def _unload(self):
        decky.logger.info("claude-deck backend stopped")
