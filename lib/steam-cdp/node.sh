#!/usr/bin/env bash
# Print the path of a Node.js >= 20 binary (PATH, Sidequest's build cache, ~/.local/opt/node*), or fail.
# Steam's client API scripts run with it: "$(lib/steam-cdp/node.sh)" lib/steam-cdp/cdp.mjs SharedJSContext file.js
set -euo pipefail
ok() { [[ -x "$1" ]] && [[ "$("$1" -p 'process.versions.node.split(".")[0]')" -ge 20 ]]; }
for n in "$(command -v node 2>/dev/null || true)" "$HOME/.cache/sidequest/node/bin/node" "$HOME"/.local/opt/node*/bin/node; do
    [[ -n "$n" ]] && ok "$n" && { echo "$n"; exit 0; }
done
echo "Node.js >= 20 not found; run Sidequest's install.sh (it fetches Node.js for the plugin build)." >&2
exit 1
