#!/usr/bin/env bash
# One-line installer for Sidequest for Claude Code: clone (or update) the repository, then run its install.sh.
#
#   curl -fsSL https://raw.githubusercontent.com/gcysne/sidequest/main/get.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/gcysne/sidequest/main/get.sh | bash -s -- --voice   # install.sh options
#
# The clone goes to ~/sidequest (set SIDEQUEST_DIR to change it) and stays there: updates and contributions use it.
set -euo pipefail
REPO="${SIDEQUEST_REPO:-https://github.com/gcysne/sidequest.git}"
DIR="${SIDEQUEST_DIR:-$HOME/sidequest}"

command -v git >/dev/null || { echo "git is required (it ships with SteamOS)." >&2; exit 1; }
if [[ -d "$DIR/.git" ]]; then
    echo "- updating $DIR"
    git -C "$DIR" pull --ff-only
elif [[ -e "$DIR" ]]; then
    echo "$DIR exists and isn't a Sidequest clone; set SIDEQUEST_DIR to another folder." >&2; exit 1
else
    echo "- cloning $REPO into $DIR"
    git clone --depth 1 "$REPO" "$DIR"
fi
cd "$DIR"
# Piped from curl, stdin is the script itself: give install.sh the terminal so it can ask its questions.
if [[ ! -t 0 ]] && { : </dev/tty; } 2>/dev/null; then
    exec ./install.sh "$@" </dev/tty
fi
exec ./install.sh "$@"
