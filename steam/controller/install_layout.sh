#!/usr/bin/env bash
# Install the Claude Code controller layout into Steam. Steam must be closed,
# otherwise it keeps its in-memory copy and overwrites this file.
#   ./install_layout.sh        (from Desktop Mode: steam -shutdown first)
set -euo pipefail
cd "$(dirname "$0")"
if pgrep -x steam >/dev/null; then
    echo "Steam is running. Close it first (steam -shutdown), then re-run." >&2; exit 1
fi
# Legion Go only for now (Steam controller type "controller_legion_go"). The Decky panel needs no layout.
for d in "$HOME"/.local/share/Steam/steamapps/common/"Steam Controller Configs"/*/config; do
    account="$(basename "$(dirname "$d")")"
    python3 -I make_layout.py "$account" > controller_legion_go.vdf
    dst="$d/claude code/controller_legion_go.vdf"
    mkdir -p "$(dirname "$dst")"
    if [[ -f "$dst" ]]; then
        bk="$HOME/.local/state/claude-deck/backup/controller_legion_go.$(date +%Y%m%d-%H%M%S).vdf"
        mkdir -p "$(dirname "$bk")"; cp "$dst" "$bk"; echo "backup: $bk"
    fi
    cp controller_legion_go.vdf "$dst"
    echo "installed: $dst"
done
