# shellcheck shell=bash disable=SC2034  # sourced by the other scripts; variables are used there
# Shared settings for the sidequest scripts (sourced, not run).
# User settings live in ~/.config/sidequest/config (shell syntax, created by install.sh).
SIDEQUEST_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/sidequest/config"
PROJECT_DIR="$HOME/Claude"        # where the persistent Claude Code session runs
REMOTE_CONTROL_NAME=""            # set a name to enable Claude Code Remote Control (e.g. "Steam Deck")
# shellcheck source=/dev/null
[[ -f "$SIDEQUEST_CONFIG" ]] && . "$SIDEQUEST_CONFIG"
PROJECT_DIR="${CLAUDE_DECK_PROJECT:-$PROJECT_DIR}"   # environment override, kept for older installs
SIDEQUEST_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/sidequest"
SIDEQUEST_LIB="$HOME/.local/lib/sidequest"
export PATH="$HOME/.local/bin:$PATH"
