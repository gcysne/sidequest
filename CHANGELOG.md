# Changelog

## 0.1.0-alpha (unreleased)

First public alpha.

- Game Mode panel (Decky plugin): ✳ status-bar icon and Quick Access entry open the persistent Claude Code session
  as a right-side panel; controller mapping, Steam keyboard input, touch scrolling.
- Start / new conversation / stop from the Quick Access menu; Claude's login opens in Steam's browser.
- About page (cog in the plugin's title bar): project info, controls, credits.
- Persistent session in tmux under a systemd user service, shared with Desktop Mode (`claude-session`).
- Steam toasts / desktop notifications when Claude needs you.
- Optional offline voice (Piper): answers read aloud; a second language is optional and off by default.
- Works with Decky Loader 3.3.0 (no `termios` in its Python; `LD_LIBRARY_PATH` cleaned for child processes).
- Tested on a Lenovo Legion Go, SteamOS 3.9.5.
