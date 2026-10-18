#!/usr/bin/env bash
# Build the Decky plugin and copy it to ~/homebrew/plugins/claude-deck.
# Needs Decky Loader installed and Node.js >= 20 (PATH or ~/.local/opt/node/bin).
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
PLUGINS="$HOME/homebrew/plugins"
DEST="$PLUGINS/claude-deck"

[[ -d "$PLUGINS" ]] || { echo "Decky Loader not found ($PLUGINS missing); skipping plugin." >&2; exit 0; }
[[ -d "$HOME/.local/opt/node/bin" ]] && export PATH="$HOME/.local/opt/node/bin:$PATH"
command -v node >/dev/null || { echo "Node.js not found; cannot build the plugin." >&2; exit 1; }
export COREPACK_ENABLE_DOWNLOAD_PROMPT=0

cd "$SRC"
corepack pnpm install --frozen-lockfile --silent
corepack pnpm run --silent typecheck
corepack pnpm run --silent build

# Stage the plugin, then copy it into place. Decky makes ~/homebrew/plugins
# root-owned, so the copy usually needs sudo (only this step runs as root).
STAGE="$SRC/build/claude-deck"
rm -rf "$STAGE"
mkdir -p "$STAGE/dist"
cp plugin.json package.json main.py "$STAGE/"
cp dist/index.js "$STAGE/dist/"

# Copy next to (not inside) the watched plugins folder, swap it in with one
# rename, then restart Decky: its hot reload trips over half-copied folders.
TMP="$HOME/homebrew/.claude-deck.tmp"
COPY=(sh -c 'rm -rf "$3" && cp -r "$2" "$3" && rm -rf "$1" && mv "$3" "$1" && { systemctl restart plugin_loader 2>/dev/null || true; }' _ "$DEST" "$STAGE" "$TMP")
if [[ -w "$PLUGINS" ]]; then
    "${COPY[@]}"
elif [[ -t 0 || -n "${SUDO_ASKPASS:-}" ]]; then
    echo "Installing into $PLUGINS and restarting Decky needs root (Decky owns that folder):"
    sudo ${SUDO_ASKPASS:+-A -p "Install the claude-deck Decky plugin and restart Decky"} "${COPY[@]}"
else
    echo "Built and staged at $STAGE. To install, run decky-plugin/install.sh in a terminal (asks for sudo)." >&2
    exit 2
fi
echo "Plugin installed to $DEST and Decky restarted."
