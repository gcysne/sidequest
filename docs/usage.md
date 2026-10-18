# Using claude-deck

Everything you can do in Game Mode, button by button. New here? Start with [First run](first-run.md).

## The panel at a glance

```
 ┌──────────────── Steam status bar ───────── ✳  🔔  📶  🔋  18:04 ┐
 │                                     ┌──────────────────────────┐ │
 │   your library / game page          │ ✳ Claude  session running│ │
 │   (dimmed)                          │ ┌──────────────────────┐ │ │
 │                                     │ │                      │ │ │
 │                                     │ │  Claude Code         │ │ │
 │                                     │ │  (your live session) │ │ │
 │                                     │ │                      │ │ │
 │                                     │ │ ❯ _                  │ │ │
 │                                     │ └──────────────────────┘ │ │
 │                                     └──────────────────────────┘ │
 └── Steam footer: (A) Enter  (Y) Keyboard  (B) Back ───────────────┘
```

- The panel slides in on the right, between Steam's status bar and footer. Width and font size are
  [settings](#settings).
- It shows your **live Claude Code session**, the same one you see in Desktop Mode or on your phone.
- **Closing the panel doesn't stop Claude.** It keeps working, and a toast tells you when it needs you.

## Opening and closing

| To… | Do this |
|---|---|
| **Open the panel** | Select the **✳ icon** in the status bar (D-pad up to the bar, then <kbd>A</kbd>, or tap it). Or <kbd>…</kbd> Quick Access menu > **Claude Deck** > **Open Claude panel**. |
| **Close the panel** | <kbd>B</kbd>, or tap **B Close** in the panel's header. |
| **Start Claude** (no session running) | <kbd>…</kbd> > **Claude Deck** > **Start Claude** (continues your last conversation) or **Start a new conversation**. The panel opens by itself. |
| **New conversation** | <kbd>…</kbd> > **Claude Deck** > **New conversation**. Claude restarts empty. Your previous conversation stays available through `/resume`. Asks first, because it interrupts Claude. |
| **Stop Claude** | <kbd>…</kbd> > **Claude Deck** > **Stop session**. Asks first. **Start** later continues the last conversation. |

The ✳ icon is only in the status bar while a session is running.

## Buttons in the panel

Focus always stays on the terminal, so every button always does the same thing.

| Button | Does | Why it's useful |
|---|---|---|
| <kbd>A</kbd> | **Enter** | Send your message; confirm the highlighted choice in Claude's menus and permission prompts |
| <kbd>B</kbd> | **Close the panel** | Claude keeps running |
| <kbd>X</kbd> | **Shift+Tab** | Switch Claude's mode (normal / auto-accept edits / plan mode) |
| <kbd>Y</kbd> | **Open Steam's keyboard** | Type straight into Claude's prompt; see [Typing](#typing) |
| <kbd>D-pad</kbd> / left stick | **Arrow keys** | Move through Claude's menus and permission prompts; ↑/↓ on an empty prompt browse your previous messages; ←/→ move the cursor while editing |
| <kbd>LT</kbd> | **Esc** | Interrupt Claude while it works, or close a menu. Press twice on an empty prompt to **rewind** to an earlier message |
| <kbd>RT</kbd> (hold) | **Space, held** | Push-to-talk in Claude Code's `/voice` hold mode |
| <kbd>LB</kbd> / <kbd>RB</kbd> | **Page Up / Page Down** | Scroll long output |
| <kbd>☰</kbd> Menu | **`/`** | Start a slash command (`/clear`, `/resume`, `/model`, `/voice`, …), then <kbd>Y</kbd> to type the rest |
| <kbd>⧉</kbd> View | **Tab** | Autocomplete commands and file names |

Not used by the panel: the back buttons (Steam's UI doesn't receive them), the right stick, and the trackpads.
Steam's own buttons (<kbd>STEAM</kbd>, <kbd>…</kbd>) keep working as usual.

## Typing

1. Press <kbd>Y</kbd>. Steam's on-screen keyboard opens, and what you type goes **straight into Claude's prompt**.
2. Edit with the keyboard's Backspace and the <kbd>D-pad</kbd> ←/→.
3. Send with the keyboard's **Enter**, or close the keyboard and press <kbd>A</kbd>.

A USB or Bluetooth keyboard also works while the panel is open.

**Voice:** dictated text from Claude Code's `/voice` lands in the same prompt, so you can fix it the same way before
sending. Hold <kbd>RT</kbd> to talk in `/voice` hold mode.

## Touchscreen

| Gesture | Does |
|---|---|
| **Drag up / down** on the terminal | Scroll (one step per text row) |
| **Tap** | A mouse click in the terminal (the touchscreen acts as a mouse) |
| **Tap the ✳ icon** | Open the panel |
| **Tap "B Close"** | Close the panel |

## Notifications

When the panel is closed, a **Steam toast** pops up when:

- Claude needs your **permission** (run a command, edit a file), or is **waiting for your answer**;
- Claude **finished** a task while you were elsewhere in Game Mode.

Open the panel to respond. In Desktop Mode the same events become desktop notifications.

## Links and login

When Claude opens a link (the sign-in page, docs), it opens in **Steam's built-in browser**. Press <kbd>B</kbd> to
come back, then reopen the panel. Every link is also printed in the panel.

## Desktop Mode and your phone

- **Desktop Mode:** run `claude-session` in a terminal (Konsole). It joins the same session; don't run plain
  `claude`, which starts a separate one.
- **Phone / claude.ai:** set `REMOTE_CONTROL_NAME` in the settings to use Claude Code Remote Control with the same
  session.

## Settings

File: `~/.config/claude-deck/config` (plain text, shell syntax). The installer creates it and adds new settings on
updates without touching your values.

| Setting | Default | What it does | Applies |
|---|---|---|---|
| `PANEL_WIDTH` | `70` | Panel width, percent of the screen (30–100) | next time the panel opens |
| `PANEL_FONT_SIZE` | `15` | Terminal font size in pixels (8–40) | next time the panel opens |
| `PROJECT_DIR` | `"$HOME/Claude"` | Folder Claude works in (its project and its `.claude/settings.json`) | after Stop + Start |
| `REMOTE_CONTROL_NAME` | `""` (off) | Name for Claude Code Remote Control | after Stop + Start |

Example: a wider panel with bigger text:

```bash
PANEL_WIDTH=85
PANEL_FONT_SIZE=18
```

The optional Steam library shortcut has its own look in `~/.config/claude-deck/gamemode.conf`.

## Troubleshooting

| Problem | Try |
|---|---|
| No ✳ icon | Is a session running? <kbd>…</kbd> > **Claude Deck** shows the status and a **Start** button. The Quick Access menu entry still works if a Steam update breaks the icon. |
| Panel says "Session detached or ended" | Claude exited. Close the panel, then <kbd>…</kbd> > **Claude Deck** > **Start Claude**. |
| Claude Deck missing from the Quick Access menu | Decky Loader isn't running (SteamOS updates can remove it): reinstall Decky from decky.xyz in Desktop Mode, then re-run `./install.sh`. |
| No toasts | `~/.local/state/claude-deck/notify.log` shows where each notification went. |
| Anything else | Logs: `~/.local/state/claude-deck/`, and `journalctl -u plugin_loader` for the plugin. |
