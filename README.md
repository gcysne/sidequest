# claude-deck

**Claude Code on SteamOS handhelds, in Game Mode.** One persistent Claude Code session that you open as a side
panel from the Steam status bar, drive with the controller and the touchscreen, and also reach from Desktop Mode
and your phone.

> **Alpha.** Built and tested on a Lenovo Legion Go with SteamOS 3.8. It should work on other SteamOS devices
> (Steam Deck, Legion Go S, ROG Ally on SteamOS) but hasn't been tested there yet. Reports welcome.
>
> claude-deck is a community project. It is **not affiliated with or endorsed by Anthropic** or Valve.
> "Claude" and "Claude Code" are trademarks of Anthropic.

## What you get

- **Game Mode panel**: a ✳ icon in Steam's status bar opens your Claude session as a right-side panel (a Decky
  Loader plugin). B closes it; Claude keeps working.
- **Controller-first input**: Y opens Steam's keyboard straight into Claude's prompt, the D-pad navigates Claude's
  menus, touch-drag scrolls. Full mapping below.
- **Start / new conversation / stop** from the Quick Access menu (… button > Claude Deck).
- **Login from Game Mode**: Claude's sign-in page opens in Steam's built-in browser; no Desktop Mode needed.
- **One session everywhere**: the same conversation in Game Mode, in a Desktop Mode terminal (`claude-session`),
  and, optionally, on your phone or claude.ai via Claude Code Remote Control.
- **Notifications**: a Steam toast when Claude needs your permission or input (desktop notification in Desktop Mode).
- **Optional**: answers read aloud with [Piper](https://github.com/rhasspy/piper); a "Claude Code" Steam library
  shortcut with its own controller layout.

## Requirements

- SteamOS 3.7+ (or another Linux with Steam's Game Mode / gamescope session and systemd).
- [Decky Loader](https://decky.xyz) for the Game Mode panel.
- A Claude subscription (Pro, Max, Team, Enterprise) or an Anthropic Console account. Claude Code's
  [usage terms](https://www.anthropic.com/legal) apply.
- Installed for you if missing: [Claude Code](https://docs.claude.com/en/docs/claude-code/setup) (official
  installer) and, only to build the plugin, Node.js (official build from nodejs.org, checksum-verified, kept in
  `~/.cache/claude-deck/node`). `tmux`, `xterm`, `python3` and `curl` ship with SteamOS.

## Install

In **Desktop Mode**, open Konsole:

```bash
git clone https://github.com/gcysne/claude-deck.git
cd claude-deck
./install.sh
```

The installer explains each step. It asks for your password once, to copy the plugin into Decky's folder
(`~/homebrew/plugins` belongs to root). Everything else stays in your home folder. Re-run it to update
(`git pull && ./install.sh`).

Then switch to Game Mode and follow **[First run](docs/first-run.md)**: start Claude from the Quick Access menu,
pick a theme, and sign in. It takes about two minutes.

Options: `--add-to-steam` (library shortcut), `--no-plugin`, `--no-claude`. Remove with `./uninstall.sh`.

## Using it

> **Full guide with every button, gesture and setting: [docs/usage.md](docs/usage.md).**

**Open** the panel with the **✳ icon** in Steam's status bar, or <kbd>…</kbd> Quick Access menu > **Claude Deck**.
**Close** it with <kbd>B</kbd>: Claude keeps working and sends a Steam toast when it needs you.

| Button | In the panel |
|---|---|
| <kbd>A</kbd> | **Enter**: send, confirm a choice |
| <kbd>B</kbd> | **Close the panel** (Claude keeps running) |
| <kbd>X</kbd> | **Shift+Tab**: switch Claude's mode |
| <kbd>Y</kbd> | **Steam keyboard**, typing straight into Claude's prompt |
| <kbd>D-pad</kbd> / left stick | **Arrow keys**: menus, prompts, message history, cursor |
| <kbd>LT</kbd> | **Esc**: interrupt Claude; twice on an empty prompt = rewind |
| <kbd>RT</kbd> hold | **Space, held**: push-to-talk in `/voice` hold mode |
| <kbd>LB</kbd> / <kbd>RB</kbd> | **Page Up / Page Down** |
| <kbd>☰</kbd> Menu | **`/`**: start a slash command |
| <kbd>⧉</kbd> View | **Tab**: autocomplete |
| Touchscreen | **drag** to scroll, **tap** to click |

**Quick Access menu > Claude Deck:** **Start Claude** (continue) · **Start a new conversation** ·
**New conversation** · **Stop session** · **Open Claude panel**.

**Desktop Mode:** run `claude-session` in a terminal to join the same session (not plain `claude`, which would start
a separate one). `claude-session --help` lists the other commands.

### Settings

`~/.config/claude-deck/config`:

| Setting | Default | |
|---|---|---|
| `PANEL_WIDTH` | `70` | Panel width, % of the screen (30–100). Next panel open. |
| `PANEL_FONT_SIZE` | `15` | Terminal font size, px (8–40). Next panel open. |
| `PROJECT_DIR` | `"$HOME/Claude"` | Folder Claude works in. After Stop + Start. |
| `REMOTE_CONTROL_NAME` | `""` (off) | Claude Code Remote Control name. After Stop + Start. |

## How it works

```
 Game Mode (Steam UI)                         your home folder
 ┌────────────────────────────┐   pty bridge  ┌──────────────────────────────────────────┐
 │ Decky plugin "Claude Deck" │◄────────────► │ tmux -L claude  (claude-session.service)  │
 │  status-bar icon, panel,   │               │   └─ claude (Claude Code) in PROJECT_DIR │
 │  xterm.js terminal         │◄── spool ──── │ claude-open-url / claude-notify (hooks)  │
 └────────────────────────────┘               └──────────────────────────────────────────┘
        Desktop Mode terminal ── claude-session ──► same tmux session
```

- The session runs in tmux under a systemd **user** service with linger, so it survives switching between Desktop
  and Game Mode.
- The panel attaches a new tmux client inside a pseudo-terminal in the plugin's Python backend and streams it to
  xterm.js. Closing the panel only detaches.
- Claude's browser requests (`BROWSER=claude-open-url`) and notification hooks drop small files in
  `~/.local/state/claude-deck/`. The plugin turns them into Steam's browser and Steam toasts.

| Installed piece | Where |
|---|---|
| Scripts (`claude-session`, `claude-open-url`, `claude-notify`, `claude-tts`, `claude-gamemode`) | `~/.local/lib/claude-deck`, linked in `~/.local/bin` |
| Session service | `~/.config/systemd/user/claude-session.service` |
| Settings | `~/.config/claude-deck/` |
| Claude Code hooks (notifications, voice) | `<project folder>/.claude/settings.json` (merged; your hooks are kept) |
| Decky plugin | `~/homebrew/plugins/claude-deck` |
| Logs | `~/.local/state/claude-deck/*.log`, Decky: `journalctl -u plugin_loader` |

## Optional extras

- **Voice**: install Piper (`uv tool install piper-tts`) and a voice in `~/.local/share/piper-voices`, then re-run
  `./install.sh`. `claude-tts --help` for voices and on/off.
- **Steam library shortcut** (`./install.sh --add-to-steam`): a full-screen terminal "game" for the same session.
  Art: `steam/artwork/make_artwork.sh <appid>`. A Legion Go controller layout for it:
  `steam/controller/install_layout.sh` (Steam must be closed).

## Known limitations (alpha)

- Device back buttons (e.g. Legion Go Y1–Y3/M3) don't reach Steam's UI, so the panel can't use them.
- The left stick can't be told apart from the D-pad in Steam's UI; both send arrows.
- Touch scrolling moves in steps (one wheel event per text row).
- Google sign-in may refuse Steam's built-in browser; use email sign-in, or sign in once in Desktop Mode.
- The status-bar icon hooks into Steam's UI internals; a Steam client update can break it. The Quick Access menu
  entry keeps working when that happens.
- Running a game while the panel is open isn't handled yet.

## Development

`decky-plugin/` is a standard Decky plugin (TypeScript + rollup, Python backend). `corepack pnpm install`,
`corepack pnpm run build`, then `decky-plugin/install.sh`. Design notes: `docs/spikes/`, `docs/panel-backlog.md`.

## License

See [LICENSE](LICENSE).
