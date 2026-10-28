# Contributing

Thanks for helping. Sidequest is an alpha, so reports from new devices are the most useful contribution.

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
| `devices/<vendor>/<model>/` | Device-specific knowledge, scripts and services (`device.yaml` + `README.md`); `<vendor>/_common/` and `_common/` for shared ones. See [devices/README.md](devices/README.md) |
| `os/<id>/`, `stacks/<name>/` | OS-specific and emulation-suite-specific knowledge |
| `lib/` | Code shared by several skills (Steam client API bridge, paths, notifier) |
| `bin/`, `decky-plugin/`, `systemd/`, `tmux/`, `voice/` | The session, panel and voice |

Split a device folder only when settings, controls or quirks differ; otherwise add `match` rules. State only facts
you verified on the device, with the OS version.

## Commits

Subject `topic: message`, where the topic is the module: `plugin`, `session`, `voice`, `agent`, `skill`, `device`,
`os`, `stack`, `docs`, `ci`, `repo`. Example: `device: legion-go: performance profile on AC fixes throttling`.

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
