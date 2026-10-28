"""Shared paths for Sidequest's Python tools: import with sys.path.insert(0, <repo or install>/lib)."""
import os, re
from pathlib import Path

HOME = Path.home()
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "sidequest/config"
STATE = Path(os.environ.get("XDG_STATE_HOME", HOME / ".local/state")) / "sidequest"
LIB = Path(__file__).resolve().parent


def setting(name, default=""):
    """A value from ~/.config/sidequest/config (shell syntax; $HOME expanded)."""
    try:
        m = re.search(rf'^\s*{name}="?([^"\n]*)"?', CONFIG.read_text(), re.M)
    except OSError:
        m = None
    return os.path.expandvars(m.group(1)) if m else default


def project_dir():
    return Path(os.environ.get("SIDEQUEST_PROJECT") or setting("PROJECT_DIR", str(HOME / "Claude")))


def notes_dir():
    return project_dir() / "notes"
