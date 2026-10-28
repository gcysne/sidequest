# Contributing

Thanks for helping. Sidequest is an alpha, so reports from new devices are the most useful contribution.

## Reporting a problem

Open an issue with: device (e.g. Steam Deck OLED), SteamOS version and channel (Settings > System), Decky Loader
version, what you did and what happened. Logs help:

- `~/.local/state/sidequest/*.log`
- Decky: `journalctl -u plugin_loader -b` and `~/homebrew/logs/sidequest/`
- Session service: `journalctl --user -u claude-session -b`

## Changing code

- Keep it **device-agnostic**: no hard-coded model, resolution or button names. Device-specific values go in
  `~/.config/sidequest/config`.
- Keep everything in the user's home folder. Only the plugin copy into `~/homebrew/plugins` uses sudo.
- Plugin: `cd decky-plugin && corepack pnpm install && corepack pnpm run typecheck && corepack pnpm run build`,
  then `./install.sh` (Desktop Mode).
- Shell scripts must pass `shellcheck -S warning`; CI runs the same checks as `.github/workflows/build.yml`.
- Test in Game Mode before opening a pull request, and say in the PR which device and SteamOS version you used.

## Use of AI

Most of this project was written by Claude (Anthropic's Claude Code), directed and tested by its creator. AI-assisted
contributions are welcome; you are responsible for having read and tested what you submit.
