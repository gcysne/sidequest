# SteamOS

## Ground rules

- **The root filesystem is read-only and replaced on every update.** Anything installed with `pacman` or written
  under `/usr`, `/opt` and most of `/etc` is lost. Prefer, in order: Flatpak (`flatpak install --user`), the home
  folder (`~/.local`, `~/Applications`, AppImages), Distrobox containers, and only as a last resort root-filesystem
  changes, with explicit approval, logged in `notes/CHANGELOG.md` so they can be redone after updates.
- Never run `steamos-readonly disable` without asking; re-enable it afterwards and log it.
- `/etc/udev/rules.d/` and a few `/etc` files survive updates; verify after each update (post-update-check).
- User services (`~/.config/systemd/user/`) and `loginctl enable-linger` survive updates: prefer them for background jobs.
- Game Mode = gamescope session with Steam's UI; Desktop Mode = KDE Plasma (Wayland). Some tasks only work in one;
  sudo with a password dialog only in Desktop Mode (`sudo -A`, `SUDO_ASKPASS=/usr/bin/ksshaskpass`).

## Useful interfaces

- **SteamOS Manager** (`busctl --user tree com.steampowered.SteamOSManager1`): `PerformanceProfile1`
  (`PerformanceProfile`, `AvailablePerformanceProfiles`), `TdpLimit1` (only in the "custom" profile), `CpuBoost1`,
  `GpuPerformanceLevel1`, `FanControl1` (Steam Deck). The QAM sliders use these; user-writable, no root.
- **Steam's client API** over CEF devtools (`lib/steam-cdp/`), enabled by Decky Loader: shortcuts, artwork,
  collections, launch options, controller mappings, `SteamClient.User.StartRestart(false)` (restart Steam keeping
  the Game Mode session).
- **Steam controller mappings** for controllers Steam doesn't know are stored as `SDL_GamepadBind` lines in
  `~/.local/share/Steam/config/config.vdf`; Steam overwrites that file on exit (controllers skill).
- Logs: `~/.local/share/Steam/logs/`, `journalctl --user -b`, `journalctl -b -k` (amdgpu hangs, OOM kills),
  Proton: `PROTON_LOG=1 %command%` → `~/steam-<appid>.log`.

## Paths

| What | Where |
|---|---|
| Steam root | `~/.local/share/Steam` |
| Games, manifests | `steamapps/common/`, `steamapps/appmanifest_<appid>.acf`; other libraries in `steamapps/libraryfolders.vdf` |
| Proton prefixes, shader cache | `steamapps/compatdata/<appid>/pfx/`, `steamapps/shadercache/<appid>/` |
| Extra Proton versions | `~/.local/share/Steam/compatibilitytools.d/` |
| Artwork of shortcuts | `~/.local/share/Steam/userdata/<id>/config/grid/` |
| SD cards, USB drives | `/run/media/<user>/<label>` |
| Decky Loader | `~/homebrew/` (plugins in `~/homebrew/plugins/`, owned by root) |

## After an update

Decky Loader may need reinstalling; Steam's internal APIs may change; Decky's bundled Python can lose modules
(3.3.0 shipped without `termios`). Run the post-update-check skill.
