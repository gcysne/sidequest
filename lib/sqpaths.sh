# shellcheck shell=bash
# Shared paths for Sidequest's shell tools: . "<repo or install>/lib/sqpaths.sh"
SQ_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/sidequest/config"
SQ_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/sidequest"
SQ_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_DIR="$HOME/Claude"
# shellcheck source=/dev/null
[[ -f "$SQ_CONFIG" ]] && . "$SQ_CONFIG"
SQ_NOTES="${SIDEQUEST_PROJECT:-$PROJECT_DIR}/notes"
# Run a JS file in Steam's SharedJSContext (Steam's client API); prints the result.
sq_steam_js() { "$("$SQ_LIB/steam-cdp/node.sh")" "$SQ_LIB/steam-cdp/cdp.mjs" SharedJSContext "$1"; }
export SQ_CONFIG SQ_STATE SQ_LIB SQ_NOTES
