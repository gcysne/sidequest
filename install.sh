#!/usr/bin/env bash
# Install or update sidequest. Safe to re-run. Run it in Desktop Mode, from a terminal (Konsole).
#
#   ./install.sh                  install/update everything
#   ./install.sh --no-plugin      skip the Decky plugin (Game Mode panel)
#   ./install.sh --no-claude      don't install Claude Code even if it's missing
#   ./install.sh --voice          install text-to-speech without asking (--no-voice: skip without asking)
#
# Everything goes into your home folder. Only copying the Decky plugin into ~/homebrew/plugins needs sudo,
# because Decky Loader owns that folder.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
LIB="$HOME/.local/lib/sidequest"
BIN="$HOME/.local/bin"
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/sidequest"
CONF="$CONF_DIR/config"
PLUGIN=1 CLAUDE=1 VOICE_CHOICE=ask
for a in "$@"; do
    case "$a" in
        --no-plugin)    PLUGIN=0 ;;
        --no-claude)    CLAUDE=0 ;;
        --voice)        VOICE_CHOICE=yes ;;
        --no-voice)     VOICE_CHOICE=no ;;
        -h|--help)      awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"; exit 0 ;;
        *)              echo "unknown option: $a (see --help)" >&2; exit 2 ;;
    esac
done

say()  { printf '\033[1m- %s\033[0m\n' "$*"; }
warn() { printf '\033[33m! %s\033[0m\n' "$*" >&2; }
die()  { printf '\033[31mx %s\033[0m\n' "$*" >&2; exit 1; }

# 0. Requirements that ship with SteamOS (and most desktop Linux distributions)
for c in tmux python3 curl systemctl; do
    command -v "$c" >/dev/null || die "$c is required but not installed."
done
systemctl --user show-environment >/dev/null 2>&1 || die "No systemd user session found (systemctl --user)."

# 0b. Older versions were called claude-deck: move their settings and state, drop their scripts folder
OLD_CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/claude-deck"
OLD_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/claude-deck"
NEW_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/sidequest"
if [[ -d "$OLD_CONF_DIR" && ! -e "$CONF_DIR" ]]; then
    mv "$OLD_CONF_DIR" "$CONF_DIR" && say "settings moved from $OLD_CONF_DIR to $CONF_DIR"
fi
[[ -d "$OLD_STATE" && ! -e "$NEW_STATE" ]] && mv "$OLD_STATE" "$NEW_STATE"
rm -rf "$HOME/.local/lib/claude-deck" "$HOME/.cache/claude-deck"

# 1. Settings (created once; yours to edit)
mkdir -p "$CONF_DIR"
if [[ ! -f "$CONF" ]]; then
    cat > "$CONF" <<EOF
# sidequest settings (shell syntax). Session settings apply after Stop + Start (Quick Access menu > Sidequest);
# panel settings apply the next time the panel opens.

# Folder the persistent Claude Code session works in (its project). Created if missing.
PROJECT_DIR="${CLAUDE_DECK_PROJECT:-\$HOME/Claude}"

# Name for Claude Code Remote Control (continue the session from claude.ai or the Claude app).
# Empty = Remote Control off.
REMOTE_CONTROL_NAME=""
EOF
    say "settings: $CONF"
else
    say "settings: keeping $CONF"
fi
# Settings added in later versions: append the ones an existing file doesn't have yet.
add_setting() { # KEY VALUE COMMENT
    grep -qE "^[[:space:]]*$1=" "$CONF" && return
    printf '\n# %s\n%s=%s\n' "$3" "$1" "$2" >> "$CONF"
    say "settings: added $1=$2"
}
add_setting PANEL_WIDTH 70 "Game Mode panel width, percent of the screen (30-100). Applies the next time the panel opens."
add_setting PANEL_FONT_SIZE 15 "Game Mode panel font size in pixels (8-40). Applies the next time the panel opens."
# shellcheck source=lib/common.sh
. "$SRC/lib/common.sh"
mkdir -p "$PROJECT_DIR"

# 2. Claude Code (official native installer from claude.ai, installs into ~/.local)
if command -v claude >/dev/null || [[ -x "$BIN/claude" ]]; then
    say "Claude Code: $("$BIN/claude" --version 2>/dev/null || claude --version 2>/dev/null || echo installed)"
elif (( CLAUDE )); then
    say "Claude Code not found; installing it with the official installer (https://claude.ai/install.sh)"
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' EXIT
    curl -fsSL https://claude.ai/install.sh -o "$tmp/install.sh"
    echo "  installer sha256: $(sha256sum "$tmp/install.sh" | cut -d' ' -f1)"
    bash "$tmp/install.sh"
    [[ -x "$BIN/claude" ]] || command -v claude >/dev/null || die "Claude Code install failed; see https://docs.claude.com/en/docs/claude-code/setup"
else
    warn "Claude Code is not installed (--no-claude). The session won't start until it is."
fi

# 3. Scripts: copy to ~/.local/lib/sidequest, link into ~/.local/bin
mkdir -p "$LIB/bin" "$LIB/lib" "$LIB/tmux" "$BIN"
cp "$SRC"/bin/* "$LIB/bin/"
cp "$SRC"/lib/*.sh "$LIB/lib/"
cp "$SRC"/tmux/*.conf "$LIB/tmux/"
chmod +x "$LIB"/bin/*
for f in "$SRC"/bin/*; do
    n="$(basename "$f")"
    [[ "$n" == claude-session-inner ]] && continue   # only run by the service
    ln -sfn "$LIB/bin/$n" "$BIN/$n"
done
rm -f "$BIN/claude-session-inner"
say "scripts in $LIB, commands linked in $BIN"
case ":$PATH:" in *":$BIN:"*) ;; *) warn "$BIN is not in your PATH; add it to use claude-session from a terminal." ;; esac

# 3b. Text-to-speech (optional, recommended): Claude's answers read aloud with Piper, offline
voice_installed() { [[ -x "$BIN/piper" && -f "$HOME/.local/share/piper-voices/en_GB-alan-medium.onnx" ]]; }
if voice_installed; then
    say "text-to-speech: installed (claude-tts on|off)"
else
    if [[ "$VOICE_CHOICE" == ask ]]; then
        if [[ -t 0 ]]; then
            echo
            printf '\033[1mText-to-speech (recommended)\033[0m\n'
            echo "  Claude reads the start of each answer aloud, so you can follow along without reading the"
            echo "  screen: handy in Game Mode, with the panel closed, or across the room. It runs offline on this"
            echo "  device (Piper) and can be turned off any time with 'claude-tts off'."
            echo "  Installs into your home folder, no sudo: uv (Python tool manager), Python 3.12 managed by uv,"
            echo "  Piper and one English voice. About 150 MB to download."
            read -r -p "  Install text-to-speech? [Y/n] " ans
            [[ "${ans,,}" =~ ^(n|no)$ ]] && VOICE_CHOICE=no || VOICE_CHOICE=yes
        else
            VOICE_CHOICE=no
        fi
    fi
    if [[ "$VOICE_CHOICE" == yes ]]; then
        "$SRC/voice/install-voice.sh" || warn "text-to-speech install failed; the rest of sidequest works without it"
    else
        say "text-to-speech skipped. Add it later: ./install.sh --voice (see docs/voice.md)"
    fi
fi

# 4. Persistent session: user service, kept alive across Desktop/Game Mode switches (linger)
mkdir -p "$HOME/.config/systemd/user"
cp "$SRC/systemd/claude-session.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
if [[ "$(loginctl show-user "$USER" -p Linger --value 2>/dev/null)" != yes ]]; then
    if loginctl enable-linger "$USER" 2>/dev/null; then
        say "enabled linger: your user services keep running when you switch modes"
    else
        warn "could not enable linger; the session may stop when you switch between Desktop and Game Mode"
    fi
fi
say "claude-session.service installed (if it was running: claude-session --stop to pick up changes)"

# 5. Leftovers of the Steam library shortcut (removed in the alpha; the Decky panel replaces it)
[[ -L "$BIN/claude-gamemode" ]] && rm -f "$BIN/claude-gamemode"
rm -f "$LIB/bin/claude-gamemode" "$HOME/.local/share/applications/claude-code.desktop"

# 6. Claude Code hooks for the project: notifications, plus voice when Piper is installed
mkdir -p "$PROJECT_DIR/.claude"
VOICE=0; [[ -x "$BIN/piper" ]] && VOICE=1
python3 -I - "$SRC/claude-hooks/hooks.json" "$PROJECT_DIR/.claude/settings.json" "$HOME" "$VOICE" <<'EOF'
import json, sys
from pathlib import Path
src, dst, home, voice = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4] == "1"
ours = json.loads(src.read_text().replace("@HOME@", home))
mine = ("/.local/bin/claude-tts", "/.local/bin/claude-notify")
if not voice:
    for groups in ours.values():
        for g in groups:
            g["hooks"] = [h for h in g["hooks"] if not h["command"].endswith("/claude-tts")]
try:
    cfg = json.loads(dst.read_text())
except FileNotFoundError:
    cfg = {}
hooks = cfg.setdefault("hooks", {})
for event, groups in ours.items():
    kept = []
    for g in hooks.get(event, []):          # drop earlier sidequest entries, keep everything else
        g["hooks"] = [h for h in g.get("hooks", []) if not str(h.get("command", "")).endswith(mine)]
        if g["hooks"]:
            kept.append(g)
    hooks[event] = kept + [g for g in groups if g["hooks"]]
dst.write_text(json.dumps(cfg, indent=2) + "\n")
EOF
say "hooks in $PROJECT_DIR/.claude/settings.json (notifications$( ((VOICE)) && echo ', voice'))"

# 7. Decky plugin: the Game Mode panel
if (( PLUGIN )); then
    if [[ -d "$HOME/homebrew/plugins" ]]; then
        "$SRC/decky-plugin/install.sh"
    else
        warn "Decky Loader not found, so the Game Mode panel was skipped. Install Decky from https://decky.xyz"
        warn "(Desktop Mode), then run ./install.sh again."
    fi
fi

echo
say "Done. Next:"
echo "  * First run (login): see docs/first-run.md. In Game Mode: Quick Access menu (…) > Sidequest > Start."
echo "  * Desktop Mode: run 'claude-session' in a terminal to join the same session."
