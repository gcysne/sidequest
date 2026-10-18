# Game Mode panel: UX backlog

Feedback from the owner's Game Mode test on 2026-10-18 (Legion Go). Nothing here is implemented yet.

## 1. D-pad moves focus between the text box and the terminal

**Problem:** with focus in the text box, D-pad up moves focus to the terminal. The natural reflex is D-pad down to go
back, but in the terminal D-pad down sends an arrow key to Claude Code instead. The same button means two
different things depending on where focus is, and focus is hard to see.

**Options:**
- **A. One focus spot, recommended.** Focus stays in the text box. D-pad up/down there sends ↑/↓ to Claude Code
  (menus, permission prompts, prompt history); left/right move the cursor inside the text box. The terminal never
  takes focus with the D-pad, so there's no trap. Close stays on B, so the header button doesn't need focus.
  Implementation: capture `vgp_ondirection` in the text box, like A/Y.
- **B. Explicit mode switch.** Keep two focus spots, but enter the terminal only with a dedicated button (e.g. L3)
  and leave it with the same button. Show a clear "Terminal control" badge and footer hint while in it.
- **C. Clearer focus only.** Keep today's behaviour with a strong highlight and footer legend. Cheapest, but
  doesn't remove the mixed meaning of D-pad down.

## 2. Touchscreen doesn't scroll the terminal

**Cause:** xterm.js doesn't turn a touch drag into scrolling. Its own scrollback is nearly empty anyway, because
tmux redraws the whole screen. The tmux touch-scroll bindings only apply to the Claude Code shortcut's terminal.

**Fix:** handle `touchstart`/`touchmove` on the terminal element and convert each row of finger movement into an
SGR mouse-wheel event sent to the pty (`\e[<64;x;yM` up, `\e[<65;x;yM` down). tmux has `mouse on`, so it passes
these to Claude Code's full-screen view or scrolls its own history, the same path as
`tmux/touch-scroll.conf`. Also set `touch-action: none` on the terminal, so Steam doesn't take the gesture.
Taps stay clicks.

## 3. Voice input lands in Claude Code's prompt, not in the panel's text box

**Problem:** Claude Code's `/voice` dictation writes into its own prompt inside the terminal. The panel's text box
never sees it, so dictated text can't be edited with the Steam keyboard.

**Options:**
- **A. Edit Claude Code's prompt directly, quick.** Add edit actions that send terminal keys: Backspace, Ctrl+W
  (delete word), Ctrl+U (clear line), ←/→. These go on buttons or a small toolbar next to Send. They work for typed
  and dictated text alike.
- **B. "Pull into text box", recommended next step.** One button reads Claude Code's current prompt line
  (`tmux capture-pane -p`, the text after the `❯` prompt marker), puts it in the panel's text box, and clears
  Claude's prompt with Ctrl+U. The user edits with the Steam keyboard and sends it back with A. Depends on
  parsing Claude Code's screen, so it needs a test against multi-line prompts.
- **C. Dictation inside the panel.** The panel records the microphone and transcribes locally, e.g.
  whisper.cpp in the backend, straight into the text box. Best experience, but the biggest piece of work
  (model download, CPU use, mic access from the Decky backend).

## Spike 2026-10-18 18:00: type straight into the terminal (no text box)

**Works.** Y focused xterm's hidden `.xterm-helper-textarea` and opened Steam's keyboard with
`VirtualKeyboardManager.CreateVirtualKeyboardRef({}).ShowVirtualKeyboard()`. The owner typed "abc" + Enter, and it
reached Claude Code through xterm's `onData`. The keystrokes didn't show up as `keydown`/`input` events on the
textarea, so Steam delivers them some other way, but xterm handled them. This makes removing the text box possible
and solves items 1 (D-pad trap) and 3 (voice text not editable) together.
