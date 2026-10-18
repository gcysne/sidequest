# Shared settings for the claude-deck scripts (sourced, not run).
# User settings live in ~/.config/claude-deck/config (shell syntax, created by install.sh).
CLAUDE_DECK_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/claude-deck/config"
PROJECT_DIR="$HOME/Claude"        # where the persistent Claude Code session runs
REMOTE_CONTROL_NAME=""            # set a name to enable Claude Code Remote Control (e.g. "Steam Deck")
# shellcheck source=/dev/null
[[ -f "$CLAUDE_DECK_CONFIG" ]] && . "$CLAUDE_DECK_CONFIG"
PROJECT_DIR="${CLAUDE_DECK_PROJECT:-$PROJECT_DIR}"   # environment override, kept for older installs
CLAUDE_DECK_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/claude-deck"
CLAUDE_DECK_LIB="$HOME/.local/lib/claude-deck"
export PATH="$HOME/.local/bin:$PATH"
