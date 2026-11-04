---
name: contribute
description: Turn something from this session that solved a real problem (a device quirk and fix, tuned settings, a script or service, a new device/OS/stack folder, a better workflow) into a pull request to the Sidequest project from the user's own GitHub account, with personal data removed and the user's approval. Use when you offer to contribute, or the user asks to share or submit a fix.
---

# Contribute back

Only for things that **worked** and would help others on the same device, OS or stack. Always the user's choice:
offer once, briefly ("This fixed X; other <device> owners will hit it too. Want me to prepare a pull request?").

## 1. Decide where it goes

| It is... | Folder |
|---|---|
| True for one model | `knowledge/devices/<vendor>/<model>/` (README "quirks"/"known-good settings", or `<skill>/` for scripts/services) |
| True for a vendor's models | `knowledge/devices/<vendor>/_common/` |
| True for any handheld | `knowledge/devices/_common/` or the skill itself |
| About the OS (SteamOS, Bazzite...) | `knowledge/os/<id>/` |
| About an emulation suite/frontend | `knowledge/stacks/<name>/` |
| A better workflow | `skills/<skill>/SKILL.md` |
| A new device | new `knowledge/devices/<vendor>/<model>/` with `device.yaml` + `README.md` (see `knowledge/devices/README.md`) |

Prefer extending an existing file over adding a new one. Scripts follow the repo's style (header comment with usage,
no hard-coded user paths: use `lib/sqpaths.*`; services install as user units with `--install`/`--uninstall`).

## 2. Generalize and scrub

Remove everything personal: user names, home paths beyond `~`, IPs, hostnames, SSIDs, serial numbers, MAC
addresses, game library contents, account names, notebook excerpts. State facts with their evidence (device, OS
version, before/after numbers). Mark anything not verified as unverified.

## 3. Prepare the change in the user's clone

- The clone: `SIDEQUEST_SRC` in `~/.config/sidequest/config`. GitHub CLI: `gh` (install it in the home folder if
  missing, from the official releases; check `gh auth status`; the user logs in with `gh auth login` themselves).
- `gh repo fork --remote --remote-name fork` (once), then a branch from the latest `origin/main`:
  `git switch -c <topic>-<short-name> origin/main`.
- Make the change. Commit subject format `topic: message` (topic = module: `device`, `skill`, `os`, `stack`,
  `agent`, `plugin`, `docs`...), e.g. `device: legion-go: performance profile on AC fixes Ryujinx throttling`.
- Run the CI checks locally: `python3 ci/check-devices.py`, `shellcheck -S warning` on changed shell scripts,
  `python3 -m py_compile` on changed Python files.

## 4. Show, then submit

Show the user the full diff and the pull request text: what problem it solves, the evidence (device, OS version,
numbers/logs), how it was tested. Only after an explicit yes:
`git push -u fork HEAD` and `gh pr create --repo <upstream> --title "<subject>" --body-file <file>`. Give the user the
link. Note it in `notes/CHANGELOG.md` ("contributed: <link>").

Never push to someone else's repository, never submit without the yes, never include the notebook.
