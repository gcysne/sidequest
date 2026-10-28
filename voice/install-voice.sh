#!/usr/bin/env bash
# Install text-to-speech for Sidequest: Claude's answers read aloud with Piper (offline, on this device).
# Everything goes into your home folder; no sudo. Safe to re-run: finished steps are skipped.
#
#   1. uv        Python package/tool manager (official release from GitHub, checksum-verified) -> ~/.local/bin
#   2. Piper     piper-tts from PyPI, in its own Python 3.12 managed by uv (SteamOS's Python is left alone)
#   3. a voice   en_GB-alan-medium from rhasspy/piper-voices (pinned revision, checksum-verified)
#                -> ~/.local/share/piper-voices
#
# See docs/voice.md for using it, other voices and removing it.
set -euo pipefail

BIN="$HOME/.local/bin"
VOICES="$HOME/.local/share/piper-voices"
PIPER_VERSION="1.8.0"
PYTHON_VERSION="3.12"
# Default voice, pinned to a piper-voices revision so the checksums below stay valid.
VOICE="en_GB-alan-medium"
VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/c10ece1aade47bb51c153c893d14e5bf8e5b7117/en/en_GB/alan/medium"
VOICE_SHA256_ONNX="0a309668932205e762801f1efc2736cd4b0120329622adf62be09e56339d3330"
VOICE_SHA256_JSON="c0f0d124e5895c00e7c03b35dcc8287f319a6998a365b182deb5c8e752ee8c1e"

say()  { printf '\033[1m- %s\033[0m\n' "$*"; }
die()  { printf '\033[31mx %s\033[0m\n' "$*" >&2; exit 1; }
export PATH="$BIN:$PATH"
mkdir -p "$BIN"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1. uv
if command -v uv >/dev/null; then
    say "uv: $(uv --version)"
else
    case "$(uname -m)" in
        x86_64)  target=x86_64-unknown-linux-gnu ;;
        aarch64) target=aarch64-unknown-linux-gnu ;;
        *) die "no uv build for $(uname -m); install uv yourself (https://docs.astral.sh/uv/) and re-run" ;;
    esac
    say "installing uv (github.com/astral-sh/uv, latest release)"
    base="https://github.com/astral-sh/uv/releases/latest/download"
    curl -fsSL "$base/uv-$target.tar.gz" -o "$tmp/uv.tar.gz"
    curl -fsSL "$base/uv-$target.tar.gz.sha256" -o "$tmp/uv.sha256"
    [[ "$(sha256sum "$tmp/uv.tar.gz" | cut -d' ' -f1)" == "$(cut -d' ' -f1 "$tmp/uv.sha256")" ]] \
        || die "uv checksum mismatch"
    tar -xzf "$tmp/uv.tar.gz" -C "$tmp"
    install -m 755 "$tmp/uv-$target/uv" "$tmp/uv-$target/uvx" "$BIN/"
    say "uv $("$BIN/uv" --version | cut -d' ' -f2) installed in $BIN"
fi

# 2. Piper
if [[ -x "$BIN/piper" ]]; then
    say "Piper: installed ($BIN/piper)"
else
    say "installing Piper $PIPER_VERSION with Python $PYTHON_VERSION (uv downloads that Python once, ~30 MB)"
    UV_TOOL_BIN_DIR="$BIN" uv tool install --python "$PYTHON_VERSION" "piper-tts==$PIPER_VERSION"
    [[ -x "$BIN/piper" ]] || die "Piper install failed"
fi

# 3. Default voice
mkdir -p "$VOICES"
fetch() { # file sha256 -> 0 if downloaded, 1 if already there
    local f="$VOICES/$1"
    [[ -f "$f" && "$(sha256sum "$f" | cut -d' ' -f1)" == "$2" ]] && return 1
    curl -fsSL "$VOICE_URL/$1" -o "$tmp/$1"
    [[ "$(sha256sum "$tmp/$1" | cut -d' ' -f1)" == "$2" ]] || die "checksum mismatch for $1"
    mv "$tmp/$1" "$f"
}
[[ -f "$VOICES/$VOICE.onnx" ]] || say "downloading voice $VOICE (~60 MB)"
got=0
fetch "$VOICE.onnx" "$VOICE_SHA256_ONNX" && got=1
fetch "$VOICE.onnx.json" "$VOICE_SHA256_JSON" && got=1
if (( got )); then say "voice $VOICE installed in $VOICES"; else say "voice: $VOICE already installed"; fi

if command -v pw-play >/dev/null && [[ -x "$BIN/claude-tts" ]]; then
    say "test: you should hear a short sentence"
    "$BIN/claude-tts" say "Voice is ready. Claude will read its answers aloud." || true
fi
