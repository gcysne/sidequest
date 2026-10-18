# Voice: Claude reads its answers aloud

**Optional, recommended.** When Claude finishes an answer, claude-deck reads the start of it aloud. You can follow
what Claude is doing without reading the screen: with the panel closed, while something else is on screen, or from
across the room.

- Speech is generated **offline, on your device**, by [Piper](https://github.com/OHF-Voice/piper1-gpl). No text is
  sent anywhere for speech.
- Only the **first paragraph** of a long answer is read (short answers are read in full). Code blocks, tables and
  long paths are skipped.
- A new answer cuts off the one still being read.

This is about Claude **speaking**. For **talking to Claude**, use Claude Code's own `/voice` dictation: in the panel,
type `/voice` (<kbd>☰</kbd> Menu types `/`) and hold <kbd>RT</kbd> to talk in hold mode.

## Install

The installer offers it:

```text
Text-to-speech (recommended)
  ...
  Install text-to-speech? [Y/n]
```

Or any time later:

```bash
./install.sh --voice           # from the claude-deck folder, Desktop Mode
```

It installs into your home folder, with no sudo, about 150 MB:

| Piece | Source | Where |
|---|---|---|
| uv (Python tool manager) | official release from github.com/astral-sh/uv, checksum-verified | `~/.local/bin/uv`, `uvx` |
| Python 3.12 (managed by uv; SteamOS's own Python isn't touched) | python-build-standalone via uv | `~/.local/share/uv/python` |
| Piper 1.8.0 | `piper-tts` from PyPI | `~/.local/share/uv/tools/piper-tts`, `~/.local/bin/piper` |
| Voice `en_GB-alan-medium` (British English, male) | rhasspy/piper-voices on Hugging Face, pinned revision, SHA-256 verified | `~/.local/share/piper-voices` |

The installer plays a test sentence at the end. Re-running skips what's already installed.

## Everyday use

| Command | Does |
|---|---|
| `claude-tts off` | Stop reading answers (stays off until `on`) |
| `claude-tts on` | Read answers again |
| `claude-tts stop` | Cut off what's playing now |
| `claude-tts say "Hello"` | Speak a test sentence |
| `claude-tts voices` | List installed voices and the current settings |
| `claude-tts voice NAME [SPEAKER]` | Switch voice, e.g. `claude-tts voice en_GB-cori-high` |
| `claude-tts speed 1.2` | Speak faster (1.0 = normal) |

Run these in a terminal, or ask Claude in the panel to run them for you ("turn the voice off").
Settings are kept in `~/.config/claude-tts/config.json`.

## More voices and languages

Listen to the voices at <https://rhasspy.github.io/piper-samples/>. Then download a voice's two files, `NAME.onnx`
and `NAME.onnx.json`, from <https://huggingface.co/rhasspy/piper-voices> into `~/.local/share/piper-voices`.
Switch with `claude-tts voice NAME`.

Example: a British female voice:

```bash
cd ~/.local/share/piper-voices
base=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high
curl -LO "$base/en_GB-cori-high.onnx" -LO "$base/en_GB-cori-high.onnx.json"
claude-tts voice en_GB-cori-high
```

Some voices have several speakers (`claude-tts voices` lists them); pick one with `claude-tts voice NAME SPEAKER`.

**Portuguese answers** are detected and read with a second voice, if you add one:
`claude-tts voice-pt NAME`. Check each voice's license on its Hugging Face page; some are non-commercial.

## Remove

```bash
claude-tts off                                  # or remove it completely:
uv tool uninstall piper-tts
rm -rf ~/.local/share/piper-voices ~/.config/claude-tts
rm -f ~/.local/bin/uv ~/.local/bin/uvx          # only if nothing else uses uv
./install.sh                                    # re-run: drops the voice hook now that Piper is gone
```

## Troubleshooting

| Problem | Try |
|---|---|
| Silence | `claude-tts say test`. If that's silent too, check the volume and that `pw-play` exists (PipeWire, standard on SteamOS). `claude-tts voices` must list the voice that's set. |
| Answers aren't read, but `say` works | `claude-tts on`; re-run `./install.sh` so the voice hook is added to your project's `.claude/settings.json`. |
| Reads the wrong language | Portuguese detection is simple; set the voices with `claude-tts voice` / `voice-pt`. |
