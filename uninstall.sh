#!/usr/bin/env bash
# Remove claude-deck. Keeps your settings (~/.config/claude-deck), your project folder, Claude Code itself
# and your Claude login.
#   ./uninstall.sh            remove scripts, service, hooks and the Decky plugin (asks for sudo)
#   ./uninstall.sh --keep-plugin
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
LIB="$HOME/.local/lib/claude-deck"
KEEP_PLUGIN=0; [[ "${1:-}" == "--keep-plugin" ]] && KEEP_PLUGIN=1
# shellcheck source=lib/common.sh
. "$SRC/lib/common.sh"

systemctl --user stop claude-session.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/claude-session.service"
systemctl --user daemon-reload
for f in "$SRC"/bin/* claude-gamemode; do   # claude-gamemode: from older installs
    l="$HOME/.local/bin/$(basename "$f")"
    [[ -L "$l" && "$(readlink "$l")" == "$LIB"/* ]] && rm -f "$l"
done
rm -rf "$LIB"
rm -f "$HOME/.local/share/applications/claude-code.desktop"
rm -rf "$CLAUDE_DECK_STATE/open-url" "$CLAUDE_DECK_STATE/toasts"

if [[ -f "$PROJECT_DIR/.claude/settings.json" ]]; then
    python3 -I - "$PROJECT_DIR/.claude/settings.json" <<'EOF'
import json, sys
from pathlib import Path
p = Path(sys.argv[1]); cfg = json.loads(p.read_text())
mine = ("/.local/bin/claude-tts", "/.local/bin/claude-notify")
for event in list(cfg.get("hooks", {})):
    groups = []
    for g in cfg["hooks"][event]:
        g["hooks"] = [h for h in g.get("hooks", []) if not str(h.get("command", "")).endswith(mine)]
        if g["hooks"]:
            groups.append(g)
    if groups: cfg["hooks"][event] = groups
    else: del cfg["hooks"][event]
p.write_text(json.dumps(cfg, indent=2) + "\n")
EOF
    echo "- removed claude-deck hooks from $PROJECT_DIR/.claude/settings.json"
fi

if (( ! KEEP_PLUGIN )) && [[ -d "$HOME/homebrew/plugins/claude-deck" ]]; then
    echo "- removing the Decky plugin needs your password (Decky owns ~/homebrew/plugins)"
    sudo ${SUDO_ASKPASS:+-A} -p "[sudo] password to remove the claude-deck Decky plugin: " \
        sh -c 'rm -rf "$1" && { systemctl restart plugin_loader 2>/dev/null || true; }' _ "$HOME/homebrew/plugins/claude-deck"
fi
echo "Removed. Kept: ~/.config/claude-deck, $PROJECT_DIR, Claude Code and your login."
