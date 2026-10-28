#!/usr/bin/env bash
# Install, re-install and uninstall Sidequest into a throwaway home folder and check the results.
# systemctl, loginctl and sudo are replaced by no-op stand-ins, so the test never touches the real user session
# (a real `systemctl --user stop claude-session` would stop the running Claude session).
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/shim" "$T/home/Claude"
for c in systemctl loginctl sudo; do printf '#!/bin/sh\nexit 0\n' > "$T/shim/$c"; chmod +x "$T/shim/$c"; done
printf '# My rules\nBe brief.\n' > "$T/home/Claude/CLAUDE.md"
export PATH="$T/shim:$PATH" HOME="$T/home" XDG_CONFIG_HOME="$T/home/.config" XDG_STATE_HOME="$T/home/.local/state"
fail() { echo "FAIL: $*" >&2; exit 1; }
P="$HOME/Claude"

"$SRC/install.sh" --no-plugin --no-claude --no-voice >/dev/null
"$SRC/install.sh" --no-plugin --no-claude --no-voice >/dev/null      # re-run must be idempotent
[[ "$(grep -c 'sidequest/agent/AGENT.md' "$P/CLAUDE.md")" == 1 ]] || fail "agent import missing or duplicated"
grep -q 'Be brief.' "$P/CLAUDE.md" || fail "user's CLAUDE.md content lost"
n="$(find "$SRC/skills" -mindepth 1 -maxdepth 1 -type d | wc -l)"
[[ "$(find "$P/.claude/skills" -mindepth 1 -maxdepth 1 -type l | wc -l)" == "$n" ]] || fail "skill links"
for f in README.md CHANGELOG.md RESUME.md hardware.md games/README.md; do [[ -f "$P/notes/$f" ]] || fail "notes/$f"; done
grep -q SessionStart "$P/.claude/settings.json" || fail "update-check hook"
[[ -s "$HOME/.local/lib/sidequest/VERSION" ]] || fail "VERSION"
python3 "$P/.claude/skills/hardware-profile/discover.py" --json >/dev/null || fail "discover.py via skill link"
echo "edited" >> "$P/notes/RESUME.md"
"$SRC/install.sh" --no-plugin --no-claude --no-voice >/dev/null
grep -q edited "$P/notes/RESUME.md" || fail "install overwrote the notebook"

"$SRC/uninstall.sh" --keep-plugin >/dev/null
[[ -z "$(ls -A "$P/.claude/skills")" ]] || fail "skill links left after uninstall"
grep -q 'sidequest/agent' "$P/CLAUDE.md" && fail "agent import left after uninstall"
grep -q 'Be brief.' "$P/CLAUDE.md" || fail "uninstall removed the user's rules"
[[ -f "$P/notes/RESUME.md" ]] || fail "uninstall removed the notebook"
[[ ! -e "$HOME/.local/lib/sidequest" ]] || fail "installed files left after uninstall"
echo "install test OK"
