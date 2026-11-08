# Contributing

Thanks for helping. Sidequest is an alpha, so reports from new devices are the most useful contribution.

> [!IMPORTANT]
> **IF YOU OPEN AN ISSUE, ASK CLAUDE TO FIX IT, VALIDATE IT AND OPEN A PULL REQUEST TOO.**
>
> This project is written with [Claude Code](https://claude.com/claude-code), and you can use it the same way. In
> your clone, give Claude the issue and ask it to:
>
> 1. **Fix it**: find the cause and make the smallest change that solves it.
> 2. **Validate it**: run the checks in [Changing code](#changing-code), then test the fix on your device.
> 3. **Open a pull request** against `main` that links the issue (`Fixes #123`) and says which device and SteamOS
>    version you tested on.
>
> Read the change before you submit it: you're responsible for what you send. Every pull request goes through the
> automatic security checks and the maintainer's review ([Pull request checks](#pull-request-checks)).
>
> On a handheld with Sidequest, just tell the companion "fix this issue and open a pull request": its `contribute`
> skill removes personal data and shows you the change before anything is sent.

## Reporting a problem

Open an issue with: device (e.g. Steam Deck OLED), SteamOS version and channel (Settings > System), Decky Loader
version, what you did and what happened. Logs help:

- `~/.local/state/sidequest/*.log`
- Decky: `journalctl -u plugin_loader -b` and `~/homebrew/logs/sidequest/`
- Session service: `journalctl --user -u claude-session -b`

## Where things go

| Folder | What |
|---|---|
| `agent/` | The companion agent's instructions (`AGENT.md`) and notebook templates |
| `skills/<name>/` | One workflow per skill (`SKILL.md` + tools only that skill uses) |
| `knowledge/devices/<vendor>/<model>/` | Device-specific knowledge, scripts and services (`device.yaml` + `README.md`); `<vendor>/_common/` and `_common/` for shared ones. See [knowledge/devices/README.md](knowledge/devices/README.md) |
| `knowledge/os/<id>/`, `knowledge/stacks/<name>/` | OS-specific and emulation-suite-specific knowledge |
| `lib/` | Code shared by several skills (Steam client API bridge, paths, notifier) |
| `bin/`, `decky-plugin/`, `systemd/`, `tmux/`, `voice/` | The session, panel and voice |

Split a device folder only when settings, controls or quirks differ; otherwise add `match` rules. State only facts
you verified on the device, with the OS version.

## Commits

Subject `topic: message`, where the topic is the module: `plugin`, `session`, `voice`, `agent`, `skill`, `device`,
`os`, `stack`, `docs`, `ci`, `repo`. Example: `device: legion-go: performance profile on AC fixes throttling`.

## Branches and reviews

Work on a branch and open a pull request against `main`; the code owners in `.github/CODEOWNERS` review it. Code
owners (maintainers) push their own changes directly. Device maintainers can be added as code owners of their device
folder.

## Changing code

- Keep it **device-agnostic**: no hard-coded model, resolution or button names. Device-specific values go in
  `~/.config/sidequest/config`.
- Keep everything in the user's home folder. Only the plugin copy into `~/homebrew/plugins` uses sudo.
- Plugin: `cd decky-plugin && corepack pnpm install && corepack pnpm run typecheck && corepack pnpm run build`,
  then `./install.sh` (Desktop Mode).
- Shell scripts must pass `shellcheck -S warning`; `python3 ci/check-devices.py` must pass; CI runs the same checks
  (`.github/workflows/build.yml`).
- Tools use `lib/sqpaths.*` for paths (no hard-coded home folders or device paths); services install as user units
  with `--install` / `--uninstall`.
- Test in Game Mode before opening a pull request, and say in the PR which device and SteamOS version you used.

## Use of AI

Most of this project was written by Claude (Anthropic's Claude Code), directed and tested by its creator. AI-assisted
contributions are welcome; you are responsible for having read and tested what you submit.

## Pull request checks

Only the maintainer pushes to `main`; every other change comes as a pull request, reviewed by the code owner
(`.github/CODEOWNERS`). Each pull request gets two automatic security checks:

- **PR security scan** (required, `.github/security/pr_scan.py`): reads what the pull request adds and **rejects it
  upfront** (closes it) on binaries or archives, prompt injection or hidden Unicode, obfuscated, encoded or minified
  code, long numeric or encoded arrays, downloads or installs from sources not listed in
  `.github/security/allowed-sources.txt`, piping downloads into a shell, reverse shells, miners, exfiltration
  endpoints, sudoers or setuid changes, destructive commands on `/` or `~`, package install hooks, and changes to
  `.github/` or `CODEOWNERS`. Risky commands such as `rm -rf`, `sudo`, process kills or credential paths are
  reported as warnings in a review for the maintainer to check.
- **AI security review** (advisory, `.github/security/ai_review.py`): Claude reads the diff as text, with no tools,
  and comments on anything malicious or unsafe the pattern scan can't see. It runs once when a pull request is
  opened (not on every push, and not when the scan already rejected it); the maintainer requests another review with
  the `ai-review` label. Limits: 3 per pull request, 10 per repository per day (`.github/security/ai_budget.py`).

Needs a tool from a new source? Say so in the pull request: the maintainer decides whether it goes on the allowed
list. False positive? Explain it in a comment; the maintainer can add the `security-reviewed` label.
