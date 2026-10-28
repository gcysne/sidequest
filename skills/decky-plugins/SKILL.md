---
name: decky-plugins
description: Install, update, troubleshoot and remove Decky Loader and its plugins on the handheld, from the official store or established community repos. Use when the user wants a Decky plugin, Decky disappeared after an update, or a plugin fails.
---

# Decky Loader and plugins

- **Decky Loader** itself: only from the official project (decky.xyz / SteamDeckHomebrew on GitHub). Its installer
  needs sudo: Desktop Mode, download it, read it, summarize it, then run it. SteamOS updates can remove Decky:
  re-running the installer is the usual fix. Version: `~/homebrew/services/.loader.version`.
- **Store plugins:** `decky-store-install "<exact store name>" [version]` downloads the plugin from the official
  store (plugins.deckbrew.xyz), checks its sha256 against the listing, and swaps it into `~/homebrew/plugins` (root
  owns that folder: sudo, Desktop Mode). In Game Mode the user can install from the store UI instead
  (QAM > Decky > store icon).
- **Third-party plugins** (outside the store): fine when they're the established community option; say they're
  unofficial, check the repo's activity and support for this OS/device (device folder), read install scripts first.
- **Check before recommending:** what the plugin needs (e.g. kernel drivers or modules that this OS doesn't ship:
  compare with `notes/hardware.md`) and whether it would fight something already running (Steam's own sliders,
  Sidequest services, controller daemons).
- **Troubleshoot:** `journalctl -u plugin_loader -b`, `~/homebrew/logs/<plugin>/` (newest file): tracebacks,
  missing Python modules (Decky bundles its own Python, which has lost modules in updates), environment problems
  (Decky is a PyInstaller bundle: child processes may inherit its `LD_LIBRARY_PATH`).
- Log installs/removals in `notes/CHANGELOG.md`.
