# claude-deck

Claude Code as a first-class citizen on a SteamOS handheld (Lenovo Legion Go):
one persistent Claude session that you can reach from Desktop Mode, from Game Mode
(as a "game" in the Steam library) and from your phone (Remote Control), with
answers read aloud and notifications when Claude needs you.

Status: stage 1 (Steam shortcut + notifications). Stage 2, a Decky plugin with a
chat panel in the Quick Access Menu, will live in `decky-plugin/`.

## What it installs (home folder only, no sudo)

| Piece | Where | What it does |
|---|---|---|
| `claude-session` | `~/.local/bin` | Start/attach the persistent session (tmux `-L claude`, user service) |
| `claude-session-inner` | `~/.local/lib/claude-deck/bin` | Runs `claude --continue --remote-control "Legion Go"` in the project folder |
| `claude-gamemode` | `~/.local/bin` | Steam shortcut target: full-screen xterm joined to the session |
| `claude-notify` | `~/.local/bin` | Hook: KDE notification (Desktop) or Steam toast (Game Mode) |
| `claude-tts` | `~/.local/bin` | Hook: reads answers aloud with Piper |
| `claude-session.service` | `~/.config/systemd/user` | Keeps the tmux session alive across mode switches (needs `loginctl enable-linger`) |
| `gamemode.conf` | `~/.config/claude-deck` | Font, size and colors of the Game Mode terminal (created once, yours to edit) |
| `claude-code.desktop` | `~/.local/share/applications` | App entry; the Steam shortcut is created from it |
| hooks | `<project>/.claude/settings.json` | Stop → voice + notify, Notification → notify (merged, other hooks kept) |

The project folder is `~/deck-agent` (override with `CLAUDE_DECK_PROJECT=...`).

## Requirements

- Claude Code (`claude`) in `~/.local/bin`, tmux, xterm (all present on SteamOS 3.8 + Claude Code installer).
  xterm is used in Game Mode because Konsole always keeps a toolbar there and xterm is a plain X11 app, which gamescope runs natively.
- Voice: `piper-tts` (`uv tool install piper-tts`) and voices in `~/.local/share/piper-voices`.
- Game Mode toasts: the [legion-go-guards](https://github.com/gcysne/legion-go-guards) Decky plugin
  (its toast spool `~/.local/state/legion-go-guards/toasts/`). Without it, Game Mode notifications are skipped.

## Install / update / remove

```bash
git pull && ./install.sh                 # install or update
./install.sh --add-to-steam              # first time: also add "Claude Code" to the Steam library
./uninstall.sh                           # remove (Steam shortcut: remove it in Steam)
```

## Using it

- **Desktop Mode:** run `claude-session` in Konsole (not plain `claude`), so Desktop and Game Mode share one conversation.
- **Game Mode:** launch "Claude Code" from the library. Steam+X opens the keyboard.
  Push-to-talk: in `/voice` hold mode, hold Space. Map a back button to Space in the
  shortcut's controller layout (a copy of the working layout is kept in `steam/controller/`).
- Closing the "game" only detaches; Claude keeps working and will toast you when it needs you.

Logs: `~/.local/state/claude-deck/{gamemode,notify}.log`.
