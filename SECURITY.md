# Security

Sidequest gives an AI coding agent (Claude Code) a terminal on your device. Know what that means:

- Claude Code can run commands as **your user** (`deck`). It asks before running tools unless you change its
  permission mode; Sidequest doesn't change it. Read prompts before approving them with A.
- Sidequest never stores your password and never configures passwordless sudo. Commands that need root still
  ask for your password.
- The Decky plugin's backend runs as your user (no `root` flag). It only starts/stops the tmux session, bridges the
  panel's terminal, and forwards files from `~/.local/state/sidequest/` (links to open, toasts to show).
- Links Claude asks to open go to Steam's built-in browser; login callbacks go to `localhost` on the device.
- Claude Code Remote Control (optional, off by default) lets your Claude account reach the session from other
  devices. Turn it on only if you want that.
- Content Claude reads (web pages, files, game folders) can contain prompt-injection attempts. Treat unexpected
  requests from Claude with suspicion.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting (Security tab > Report a vulnerability) instead of a public
issue. You'll get an answer within a week.
