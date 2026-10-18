#!/usr/bin/env bash
# Install or update claude-deck. Home folder only, no sudo, safe to re-run.
#   ./install.sh                 install/update files, hooks, systemd unit
#   ./install.sh --add-to-steam  also add the "Claude Code" shortcut to Steam (once)
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
LIB="$HOME/.local/lib/claude-deck"
BIN="$HOME/.local/bin"
PROJECT="${CLAUDE_DECK_PROJECT:-$HOME/deck-agent}"   # where Claude Code runs
ADD_TO_STEAM=0
[[ "${1:-}" == "--add-to-steam" ]] && ADD_TO_STEAM=1

say() { printf '%s\n' "- $*"; }

# 1. Scripts: copy to ~/.local/lib/claude-deck, link into ~/.local/bin
mkdir -p "$LIB/bin" "$BIN"
cp "$SRC"/bin/* "$LIB/bin/"
chmod +x "$LIB"/bin/*
for f in "$SRC"/bin/*; do
    ln -sfn "$LIB/bin/$(basename "$f")" "$BIN/$(basename "$f")"
done
say "scripts in $LIB/bin, linked in $BIN"

# 2. Persistent session (user service; started on demand, not at boot)
mkdir -p "$HOME/.config/systemd/user"
cp "$SRC/systemd/claude-session.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
say "claude-session.service installed (restart it to pick up changes: claude-session --stop)"

# 3. Terminal look for Game Mode (only created once; edit it freely)
mkdir -p "$HOME/.config/claude-deck"
[[ -f "$HOME/.config/claude-deck/gamemode.conf" ]] || cat > "$HOME/.config/claude-deck/gamemode.conf" <<'EOC'
# Game Mode terminal (xterm) settings, read by claude-gamemode
FONT="Hack"
FONT_SIZE=13
BG="#232627"
FG="#fcfcfc"
EOC
say "terminal settings ~/.config/claude-deck/gamemode.conf"

# 4. App entry (also what Steam's shortcut is created from)
mkdir -p "$HOME/.local/share/applications"
sed "s|@HOME@|$HOME|g" "$SRC/steam/claude-code.desktop" > "$HOME/.local/share/applications/claude-code.desktop"
say "app entry ~/.local/share/applications/claude-code.desktop"

# 5. Claude Code hooks (voice + notifications) in the project's settings
mkdir -p "$PROJECT/.claude"
python3 -I - "$SRC/claude-hooks/hooks.json" "$PROJECT/.claude/settings.json" "$HOME" <<'EOF'
import json, sys
from pathlib import Path
src, dst, home = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
ours = json.loads(src.read_text().replace("@HOME@", home))
try:
    cfg = json.loads(dst.read_text())
except FileNotFoundError:
    cfg = {}
hooks = cfg.setdefault("hooks", {})
mine = ("/.local/bin/claude-tts", "/.local/bin/claude-notify")
for event, groups in ours.items():
    kept = []
    for g in hooks.get(event, []):          # drop earlier claude-deck entries, keep the rest
        g["hooks"] = [h for h in g.get("hooks", []) if not str(h.get("command", "")).endswith(mine)]
        if g["hooks"]:
            kept.append(g)
    hooks[event] = kept + groups
dst.write_text(json.dumps(cfg, indent=2) + "\n")
EOF
say "hooks merged into $PROJECT/.claude/settings.json (Stop: voice + notify, Notification: notify)"

# 6. Steam shortcut (only when asked; Steam must be running)
if (( ADD_TO_STEAM )); then
    if grep -qs "claude-gamemode" "$HOME"/.local/share/Steam/userdata/*/config/shortcuts.vdf; then
        say "Steam already has a Claude Code shortcut; skipped"
    else
        steamos-add-to-steam "$HOME/.local/share/applications/claude-code.desktop"
        say "asked Steam to add the Claude Code shortcut"
    fi
fi
echo "Done."
