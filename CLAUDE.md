# Developing Sidequest for Claude Code

Instructions for an AI coding agent working **on this repository** (developing or maintaining Sidequest). They
complement [CONTRIBUTING.md](CONTRIBUTING.md); read it too. Personal or machine-specific rules go in
`CLAUDE.local.md` next to this file (ignored by git).

Not to be confused with `agent/AGENT.md`: that is the companion agent Sidequest installs on users' handhelds.

## What this repo is

| Part | Where |
|---|---|
| Persistent Claude Code session (tmux + systemd user service), notifications, voice | `bin/`, `systemd/`, `tmux/`, `voice/`, `lib/common.sh` |
| Game Mode panel (Decky plugin: React frontend, Python backend) | `decky-plugin/` |
| Companion agent installed on users' devices | `agent/` (AGENT.md, notebook templates) |
| Workflows for the companion | `skills/<name>/` (SKILL.md + tools only that skill uses) |
| Knowledge for some setups only (devices, OSes, emulation stacks) | `knowledge/` ([knowledge/README.md](knowledge/README.md)) |
| Code shared by several skills | `lib/` (`steam-cdp/`, `sqpaths.*`, `notify`) |
| Install / update / remove | `get.sh`, `install.sh`, `uninstall.sh` |
| Checks | `ci/`, `.github/workflows/build.yml` |

## Rules

- **Device-agnostic.** No hard-coded model, resolution, button names, user names or paths in generic code. What
  only applies to some devices goes in `knowledge/` (devices, OSes, emulation stacks); skills point there. Tools use
  `lib/sqpaths.*`.
- **Privacy.** Never commit anything from a user's notebook, real IPs, hostnames, serials, MAC addresses, game
  libraries or personal paths. Examples use neutral values (`~/Claude`, `nas`).
- **State facts with evidence.** Device knowledge says what was verified, on which OS version; mark the rest unverified.
- **Users' files are theirs.** `install.sh` only creates missing notebook files, never overwrites `CLAUDE.local.md` or
  notes, and only manages the marked block in the project's `CLAUDE.md`. Keep `uninstall.sh` symmetric.
- **Services** install as systemd **user** units with `--install` / `--uninstall`, restore what they changed when they
  stop, and log to `~/.local/state/sidequest/`. Only the Decky plugin copy uses sudo.
- **Never test against the real session.** `systemctl --user` reaches the live user manager even with a fake HOME:
  a real `systemctl --user stop claude-session` stops the session you are running in. Use `ci/test-install.sh`
  (it stubs systemctl, loginctl and sudo) or the same stubbing in your own tests.
- **Skills:** front matter `name` (= folder) and a `description` that says when to use it; workflow first, tools in a
  table; keep `agent/AGENT.md`'s skill table in sync when adding or renaming one.
- **Decky plugin:** Decky's bundled Python can lack modules (no `termios` in 3.3.0) and leaks `LD_LIBRARY_PATH` to
  child processes: keep the backend to the standard library and use `_env()` for subprocesses.
- Keep docs in English and short: README for users, CONTRIBUTING for contributors, CHANGELOG for every change users
  would notice.

## Before committing

```bash
python3 ci/check-devices.py
shellcheck -S warning get.sh install.sh uninstall.sh lib/*.sh voice/install-voice.sh decky-plugin/install.sh \
  bin/claude-session bin/claude-session-inner bin/claude-open-url \
  $(grep -rlE '^#!/usr/bin/env bash|^#!/bin/bash' skills knowledge lib)
for f in decky-plugin/main.py bin/claude-notify bin/claude-tts bin/sidequest-update-check \
  $(grep -rlE '^#!/usr/bin/env python3' skills knowledge lib); do python3 -m py_compile "$f"; done
ci/test-install.sh
(cd decky-plugin && corepack pnpm run typecheck && corepack pnpm run build)
```

Clean up `__pycache__` folders afterwards. Test plugin and session changes in Game Mode before calling them done.

## Commits and branches

- Subject `topic: message`; topic = module: `plugin`, `session`, `voice`, `agent`, `skill`, `device`, `os`, `stack`,
  `lib`, `install`, `docs`, `ci`, `repo`. Example: `skill: performance: add frame-time percentiles`.
- One logical change per commit; one commit per skill when adding several.
- Contributors work on branches and open pull requests; code owners (`.github/CODEOWNERS`) review them.
- Never rewrite published history or force-push unless the maintainer explicitly asks for it.
- Releases: bump `decky-plugin/package.json` (`0.x.y-alpha`), update `CHANGELOG.md`, tag `v<version>`; CI attaches
  `sidequest.zip` to the release.
