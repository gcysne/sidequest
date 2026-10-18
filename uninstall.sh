#!/usr/bin/env bash
# Remove claude-deck's installed files. The Steam shortcut has to be removed
# from Steam itself (library > Claude Code > Manage > Remove non-Steam game).
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
LIB="$HOME/.local/lib/claude-deck"
PROJECT="${CLAUDE_DECK_PROJECT:-$HOME/deck-agent}"

systemctl --user stop claude-session.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/claude-session.service"
systemctl --user daemon-reload
for f in "$SRC"/bin/*; do
    l="$HOME/.local/bin/$(basename "$f")"
    [[ -L "$l" && "$(readlink "$l")" == "$LIB"/* ]] && rm -f "$l"
done
rm -rf "$LIB"
rm -f "$HOME/.local/share/applications/claude-code.desktop"
echo "Kept ~/.config/claude-deck (your terminal settings)."
if [[ -f "$PROJECT/.claude/settings.json" ]]; then
    python3 -I - "$PROJECT/.claude/settings.json" <<'EOF'
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
fi
echo "Removed. Voices and Piper (~/.local/share/piper-voices, uv tool piper-tts) were left in place."
