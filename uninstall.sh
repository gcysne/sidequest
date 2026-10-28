#!/usr/bin/env bash
# Remove Sidequest. Keeps your settings (~/.config/sidequest), your project folder and notebook, Claude Code itself
# and your Claude login.
#   ./uninstall.sh            remove scripts, service, hooks and the Decky plugin (asks for sudo)
#   ./uninstall.sh --keep-plugin
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
LIB="$HOME/.local/lib/sidequest"
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
for l in "$PROJECT_DIR"/.claude/skills/*; do             # skill links into the installed copy
    [[ -L "$l" && "$(readlink "$l")" == "$LIB/skills/"* ]] && rm -f "$l"
done
if [[ -f "$PROJECT_DIR/CLAUDE.md" ]]; then                  # the agent import block; the rest of the file stays
    sed -i '/<!-- sidequest:agent/,/<!-- \/sidequest:agent -->/d' "$PROJECT_DIR/CLAUDE.md"
    [[ -s "$PROJECT_DIR/CLAUDE.md" ]] || rm -f "$PROJECT_DIR/CLAUDE.md"
fi
rm -rf "$LIB"
rm -f "$HOME/.local/share/applications/claude-code.desktop"
rm -rf "$SIDEQUEST_STATE/open-url" "$SIDEQUEST_STATE/toasts"

if [[ -f "$PROJECT_DIR/.claude/settings.json" ]]; then
    python3 -I - "$PROJECT_DIR/.claude/settings.json" <<'EOF'
import json, sys
from pathlib import Path
p = Path(sys.argv[1]); cfg = json.loads(p.read_text())
mine = ("/.local/bin/claude-tts", "/.local/bin/claude-notify", "/.local/bin/sidequest-update-check")
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
    echo "- removed sidequest hooks from $PROJECT_DIR/.claude/settings.json"
fi

if (( ! KEEP_PLUGIN )) && [[ -d "$HOME/homebrew/plugins/sidequest" || -d "$HOME/homebrew/plugins/claude-deck" ]]; then
    echo "- removing the Decky plugin needs your password (Decky owns ~/homebrew/plugins)"
    sudo ${SUDO_ASKPASS:+-A} -p "[sudo] password to remove the sidequest Decky plugin: " \
        sh -c 'rm -rf "$1" "$2" && { systemctl restart plugin_loader 2>/dev/null || true; }' _ "$HOME/homebrew/plugins/sidequest" "$HOME/homebrew/plugins/claude-deck"
fi
echo "Removed. Kept: ~/.config/sidequest, $PROJECT_DIR (with your notebook in notes/), Claude Code and your login."
