# Sidequest for Claude Code

**Claude Code on SteamOS handhelds, in Game Mode.** One persistent Claude Code session that you open as a side
panel from the Steam status bar, drive with the controller and the touchscreen, and also reach from Desktop Mode
and your phone.

> **Alpha.** Built and tested on a Lenovo Legion Go with SteamOS 3.9.5 and Decky Loader 3.3.0. It should work on
> other SteamOS devices (Steam Deck, Legion Go S, ROG Ally on SteamOS) but hasn't been tested there yet.
> [Device reports](../../issues/new?template=device_report.md) welcome.
>
> Sidequest is a community project. It is **not affiliated with or endorsed by Anthropic** or Valve.
> "Claude" and "Claude Code" are trademarks of Anthropic.

## What you get

- **Game Mode panel**: a ✳ icon in Steam's status bar opens your Claude session as a right-side panel (a Decky
  Loader plugin). B closes it; Claude keeps working.
- **Controller-first input**: Y opens Steam's keyboard straight into Claude's prompt, the D-pad navigates Claude's
  menus, touch-drag scrolls. Full mapping below.
- **Start / new conversation / stop** from the Quick Access menu (… button > Sidequest).
- **Login from Game Mode**: Claude's sign-in page opens in Steam's built-in browser; no Desktop Mode needed.
- **One session everywhere**: the same conversation in Game Mode, in a Desktop Mode terminal (`claude-session`),
  and, optionally, on your phone or claude.ai via Claude Code Remote Control.
- **Notifications**: a Steam toast when Claude needs your permission or input (desktop notification in Desktop Mode).
- **Voice (optional, recommended)**: answers read aloud, offline, with Piper ([docs/voice.md](docs/voice.md)).
- **About page**: the cog in the plugin's title bar (Quick Access > Sidequest) shows the version, the controls and
  the credits.

## Screenshots

<img src="docs/images/sidequest-panel.png" width="250" alt="Quick Access panel: open the Claude panel, new conversation, stop session">

The ⚙ cog opens the About page:

| About | Controls | Credits |
|---|---|---|
| <img src="docs/images/sidequest-about.png" alt="About: version, update check, project links"> | <img src="docs/images/sidequest-controls.png" alt="Controller mapping in the Claude panel"> | <img src="docs/images/sidequest-credits.png" alt="Credits: creator Gabriel Cysne"> |

## The companion agent

Sidequest isn't only a terminal: the Claude session it runs is set up as a **companion for your handheld**.

- **Roles:** install games (Steam, emulated, native ports), debug launches and controllers, profile and benchmark,
  optimize settings and power for your exact device, check everything after SteamOS updates.
- **Notebook:** it keeps `notes/` in the session folder: a hardware profile it discovers itself, a changelog of every
  change it makes (with how to undo it), what's in progress, and one page per game. New sessions read it first.
- **Skills:** step-by-step workflows in `skills/` (game install, Steam artwork, performance, power and thermals,
  controllers, Decky plugins...), linked into the session's `.claude/skills/`.
- **Knows your device:** `devices/<vendor>/<model>/` holds what only applies to some handhelds (quirks, display
  modes, power and fan behaviour, device-specific services); `os/` and `stacks/` do the same for the OS and for
  emulation suites like EmuDeck. The hardware profile picks the right folders.
- **Grows with its users:** when a session solves something other owners of that device will hit, the agent offers
  to turn it into a pull request from your own GitHub account, after you've seen the change.
- **Stays current:** at session start it checks for a new Sidequest release (once a day) and asks before updating.

Your own instructions for it go in `CLAUDE.local.md` in the session folder. The agent's rules are in
[agent/AGENT.md](agent/AGENT.md).

## Requirements

- SteamOS 3.7+ (or another Linux with Steam's Game Mode / gamescope session and systemd).
- [Decky Loader](https://decky.xyz) for the Game Mode panel.
- A Claude subscription (Pro, Max, Team, Enterprise) or an Anthropic Console account. Claude Code's
  [usage terms](https://www.anthropic.com/legal) apply.
- Installed for you if missing: [Claude Code](https://docs.claude.com/en/docs/claude-code/setup) (official
  installer) and, only to build the plugin, Node.js (official build from nodejs.org, checksum-verified, kept in
  `~/.cache/sidequest/node`). `tmux`, `python3` and `curl` ship with SteamOS.

## Install

In **Desktop Mode**, open Konsole and run:

```bash
curl -fsSL https://raw.githubusercontent.com/gcysne/sidequest/main/get.sh | bash
```

It clones Sidequest into `~/sidequest` and runs its installer. Prefer to read before running? Same thing by hand:

```bash
git clone https://github.com/gcysne/sidequest.git ~/sidequest
cd ~/sidequest
./install.sh
```

**Or let Claude do it.** If you already use Claude Code (or Claude with access to a terminal on the device), give it
this prompt:

> Install this for me: https://github.com/gcysne/sidequest

> **Note for AI agents installing Sidequest:** read this README first. Run it in Desktop Mode: clone the repository
> into `~/sidequest` and run `./install.sh` there (it asks the user about text-to-speech; pass `--voice` or
> `--no-voice` once the user has answered). The only root step is copying the Decky plugin into `~/homebrew/plugins`:
> explain it and let the user enter the password (`sudo -A` with a graphical askpass, e.g. `SUDO_ASKPASS=/usr/bin/ksshaskpass`).
> Decky Loader must be installed first (decky.xyz). Afterwards, point the user to [First run](docs/first-run.md).

The installer explains each step. It **offers text-to-speech** (recommended, see [voice](docs/voice.md)); the choice
is yours. It asks for your password once, to copy the plugin into Decky's folder (`~/homebrew/plugins` belongs to
root). Everything else stays in your home folder. Re-run it to update
(`cd ~/sidequest && git pull && ./install.sh`, or the one-liner again).

Then switch to Game Mode and follow **[First run](docs/first-run.md)**: start Claude from the Quick Access menu,
pick a theme, and sign in. It takes about two minutes.

Options: `--voice` / `--no-voice` (answer the voice question up front), `--no-plugin`, `--no-claude`. Remove with `./uninstall.sh`.

## Using it

> **Full guide with every button, gesture and setting: [docs/usage.md](docs/usage.md).**

**Open** the panel with the **✳ icon** in Steam's status bar, or <kbd>…</kbd> Quick Access menu > **Sidequest**.
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

**Quick Access menu > Sidequest:** **Start Claude** (continue) · **Start a new conversation** ·
**New conversation** · **Stop session** · **Open Claude panel**.

**Desktop Mode:** run `claude-session` in a terminal to join the same session (not plain `claude`, which would start
a separate one). `claude-session --help` lists the other commands.

### Settings

`~/.config/sidequest/config`:

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
 │ Decky plugin "Sidequest" │◄────────────► │ tmux -L claude  (claude-session.service)  │
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
  `~/.local/state/sidequest/`. The plugin turns them into Steam's browser and Steam toasts.

| Installed piece | Where |
|---|---|
| Scripts (`claude-session`, `claude-open-url`, `claude-notify`, `claude-tts`) | `~/.local/lib/sidequest`, linked in `~/.local/bin` |
| Session service | `~/.config/systemd/user/claude-session.service` |
| Settings | `~/.config/sidequest/` |
| Companion agent | `<project folder>/CLAUDE.md` (imports the agent), `.claude/skills/`, `notes/` (your notebook) |
| Knowledge base (agent, skills, devices, os, stacks) | `~/.local/lib/sidequest/` |
| Claude Code hooks (notifications, voice) | `<project folder>/.claude/settings.json` (merged; your hooks are kept) |
| Decky plugin | `~/homebrew/plugins/sidequest` |
| Logs | `~/.local/state/sidequest/*.log`, Decky: `journalctl -u plugin_loader` |

## Optional extras

- **Voice** (recommended; the installer offers it): Claude reads the start of each answer aloud, offline with Piper.
  `./install.sh --voice` adds it later. Using it, other voices, removing it: **[docs/voice.md](docs/voice.md)**.

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
CI (`.github/workflows/build.yml`) lints the scripts, builds the plugin and attaches `sidequest.zip` to tagged releases.
See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## Credits

Created by **Gabriel Cysne** ([@gcysne](https://github.com/gcysne)), who had the idea, leads the project and tests every build.
The code is written by Claude (Anthropic's Claude Code), working with Gabriel Cysne. Licensed under the [MIT License](LICENSE);
bundled third-party code: [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).

## License

See [LICENSE](LICENSE).
