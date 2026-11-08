# Changelog

## Unreleased

- Fixed: the session-start update check missed updates that only change the pre-release label
  (`0.2.0-alpha` → `0.2.0-beta.1`, `-alpha` → `-alpha.2`); it now orders versions like the plugin does.

## 0.1.0-alpha (2026-11-03)

First public alpha.

- Game Mode panel (Decky plugin): ✳ status-bar icon and Quick Access entry open the persistent Claude Code session
  as a right-side panel; controller mapping, Steam keyboard input, touch scrolling.
- Start / new conversation / stop from the Quick Access menu; Claude's login opens in Steam's browser.
- About page (cog in the plugin's title bar): project info, controls, credits, and an update notice ("New version
  available" when GitHub has a newer release, with the update command, a copy button, and "ask Claude to update").
- `save-sync` skill: backs up and syncs emulator saves with Extra Life (installed from its official release).
- Device, OS and emulation-stack knowledge moved under `knowledge/`; README sections for it and for every skill.
- Pull requests: automatic security scan (rejects binaries, prompt injection, obfuscated code, unofficial
  downloads...; warns on risky commands), advisory AI security review, code owner and a branch ruleset for `main`.
- Fixed: Steam's on-screen keyboard covered the bottom of the Claude panel (and the prompt). The panel now ends
  at the keyboard's edge while it shows, and the terminal re-fits (it never re-fitted after opening before).
- Persistent session in tmux under a systemd user service, shared with Desktop Mode (`claude-session`).
- Steam toasts / desktop notifications when Claude needs you.
- Optional offline voice (Piper): answers read aloud; a second language is optional and off by default.
- Works with Decky Loader 3.3.0 (no `termios` in its Python; `LD_LIBRARY_PATH` cleaned for child processes).
- Companion agent: `agent/AGENT.md` (roles, ground rules, notebook), 15 skills, hardware self-discovery
  (`hardware-profile`), device/OS/stack knowledge folders (`knowledge/devices/lenovo/legion-go` first), contribute-back
  workflow (pull requests from the user's account), daily update check at session start.
- Tested on a Lenovo Legion Go, SteamOS 3.9.5.
