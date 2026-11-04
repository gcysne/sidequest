---
name: save-sync
description: Back up and sync emulator save games with Extra Life (open-source companion project) - install it from its official release, connect where saves go (Google Drive, Dropbox, OneDrive, Box, pCloud, an SD card or USB folder, a NAS over SSH), run the first sync, restore older versions, resolve conflicts, move saves to a new device. Use when the user wants to back up, protect, sync or restore their game saves, asks what happens to saves if the device breaks, or asks about backing up ROMs.
---

# Back up and sync saves (Extra Life)

[Extra Life](https://github.com/gcysne/extra-life) keeps emulator save games safe and the same on every device: after
each play session it uploads the saves that changed to every connected provider and brings in what other devices
changed. Older versions are kept, and a save changed on two devices is never overwritten (it becomes a conflict for
the user to decide). 20 emulators out of the box (EmuDeck, Flatpak and native layouts). It's a separate project from
the same creator, with a command (`extralife`), a background service and a Decky plugin.

## 0. What the user actually wants

- **Saves** (in-game progress, memory cards, Switch saves): this skill.
- **Save states**: Extra Life can include them (`sync.include_states`, off by default: large and tied to the
  emulator version). Ask before turning it on.
- **ROMs, disc images, BIOS, firmware, keys**: Extra Life never uploads them. For a ROM backup, copy the library to
  another disk or a NAS (rom-library skill for the folders; rsync with `--dry-run` first), and keep the dumps the
  user owns. Never upload games, BIOS, firmware or keys to cloud storage for them.

## 1. Already installed?

```bash
command -v extralife && extralife --version && extralife status
```

Installed: go to step 3 (and `extralife update-check`: if a newer release exists, step 2 updates it).

## 2. Install (official release only)

Needs **Desktop Mode** (the Decky plugin copy asks for the password; in Game Mode there's no password dialog: offer
`--no-plugin` now and the plugin later, or ask the user to switch). The installer only writes to the home folder,
so it survives SteamOS updates. Follow the ground rules: download, read, summarize, then run; never pipe it into a
shell.

```bash
tmp="$(mktemp -d)"
curl -fsSL -o "$tmp/get-release.sh" https://github.com/gcysne/extra-life/releases/latest/download/get-release.sh
less "$tmp/get-release.sh"        # read it: it downloads extra-life.tar.gz + SHA256SUMS from the same release,
                                  # checks the checksum, unpacks to a temp folder and runs its install.sh
SUDO_ASKPASS=/usr/bin/ksshaskpass bash "$tmp/get-release.sh"      # add --no-plugin to skip the Decky plugin
```

If the download answers 404, the project has no public release yet: tell the user, don't look for copies elsewhere.
What it installs: program `~/.local/lib/extra-life/`, command `~/.local/bin/extralife`, user units
`extralife-sync.{service,timer}` (the 30-minute timer stays **off** unless the user wants it), plugin
`~/homebrew/plugins/extra-life/`. rclone (for cloud providers) is downloaded from rclone's official site with a
checksum check the first time a cloud provider is connected.

## 3. Choose where saves go

Recommend at least one copy **off the device** (a cloud service or a NAS); a folder on the same SD card as the games
doesn't survive losing that card. Several providers can be connected; every sync keeps all of them the same.

- **Easiest, in Game Mode:** Quick Access (…) → Extra Life → ⚙ → **Providers** → Connect. Cloud sign-in opens in
  Steam's browser; the user signs in, allows access, presses B to come back.
- **From a terminal:** `extralife provider connect gdrive` (or `dropbox`, `onedrive`, `box`, `pcloud`: opens the
  browser), `extralife provider connect local --path /run/media/<user>/<drive>/ExtraLife`,
  `extralife provider connect ssh --host <host> --path <folder>` (SSH key login and rsync on the host), or
  `extralife provider connect rclone --remote <name>` for a remote set up with `rclone config`.
- Sign-ins are stored by Extra Life (`~/.config/extra-life/rclone.conf`); **never copy tokens or config contents
  into the notebook**.

## 4. Check what syncs, then sync

```bash
extralife profiles          # emulators found on this device and whether they sync
extralife sync              # first sync; skips emulators that are running (close the game first)
extralife status            # last sync per provider, skipped folders, conflicts
```

- An emulator missing from `profiles` but installed: check its save folder (and `[vars]` in
  `~/.config/extra-life/config.toml` for unusual layouts); `docs/profiles.md` in the project explains new profiles.
- From then on it syncs when a game closes (the Decky plugin starts it). The ♥ icon in Steam's status bar shows the
  progress.

## 5. Second device, restore, conflicts

- **New or second device:** install, connect the **same** provider, then `extralife pull --provider <id>` (local
  files that differ are backed up first) or a normal `extralife sync`.
- **Bring back an older save:** `extralife history --provider <id>`, then
  `extralife restore <snapshot> <profile/set> <file> --provider <id>` (or the History tab in the plugin). The
  current version is kept in history and in the local backup.
- **Conflicts** (changed on two devices): `extralife conflicts`, then `extralife resolve --keep local|cloud --set
  <key> --file <path> --provider <id>` (or the Conflicts tab). Ask the user which copy to keep; never pick for them.

## 6. Troubleshoot

- `extralife doctor` (providers reachable, save folders found), `extralife progress`, plugin log
  `~/homebrew/logs/extra-life/` (newest file), service log `journalctl --user -u extralife-sync`.
- Cloud sign-in refused in Steam's browser: connect from Desktop Mode (`extralife provider connect <id>`).
- Remove: `~/.local/lib/extra-life/uninstall.sh` (`--purge` also deletes settings, sign-ins and local backups). Saves
  and what's already in the providers are never touched.

## 7. Log it

`notes/CHANGELOG.md`: version installed, providers connected (names only, no tokens or account details), timer on or
off, how to undo. A game note in `notes/games/` when a specific game's saves needed special handling.
