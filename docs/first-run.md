# First run

After `./install.sh` (Desktop Mode), everything else can be done in **Game Mode** with the controller.

## 1. Start the session

Press the **…** (Quick Access) button > **Claude Deck** > **Start Claude**. The panel opens on the right.

The ✳ icon appears in the status bar while a session is running. Later you can open the panel from there.

## 2. Claude Code's first-run screens

Claude Code shows a few setup screens, all inside the panel:

| Screen | What to press |
|---|---|
| Text style (theme) | D-pad to pick, **A** to confirm |
| Login method | **A** on "Claude account with subscription", or pick "Anthropic Console account" for API billing |
| Sign-in page | Opens by itself in **Steam's built-in browser** (see below) |
| "Do you trust the files in this folder?" | **A** on "Yes": this is your claude-deck project folder (`~/Claude` by default) |

### Signing in from Game Mode

When you choose a login method, Claude Code asks the browser to open Anthropic's sign-in page. claude-deck sends
that link to Steam's built-in browser.

1. Sign in with your Claude account. Email sign-in works well. **Y** or the touchscreen brings up the keyboard.
   Google sign-in may refuse embedded browsers; if it does, use email.
2. After you approve, the page goes to `localhost`. That's Claude Code on your device receiving the login, and it
   completes on its own; there's no code to copy.
3. Press **B** to leave the browser, then open the panel again (✳ icon). Claude is signed in and ready.

**Fallback:** the panel also prints the sign-in link. If the browser route doesn't work, sign in once in Desktop
Mode: run `claude-session` in Konsole, follow the link in your desktop browser, then switch back. The login is
stored in `~/.claude` and shared by the Game Mode session.

## 3. Use it

Type with **Y** (Steam keyboard), send with **A** or the keyboard's Enter. See the button table in the
[README](../README.md#using-it).

## Starting over

- **New conversation**: Quick Access menu > Claude Deck > **New conversation**. Claude restarts with an empty
  conversation; the old one stays available through `/resume`.
- **Stop**: Quick Access menu > Claude Deck > **Stop session**. **Start** later continues the last conversation.
- In the panel you can also type Claude Code commands such as `/clear` (Menu button types `/`).
- **Sign out / switch account**: type `/logout` in the panel, then **Stop** and **Start** the session.
- **Completely fresh** (for testing): `./uninstall.sh`, remove `~/.config/claude-deck`, and to drop the login too,
  `~/.claude` and `~/.claude.json`. Then `./install.sh`.
