---
name: post-update-check
description: After a SteamOS, Steam client, BIOS or Decky Loader update (or when notes/hardware.md versions differ from the live system), check that everything Sidequest, the notebook and the user's setup rely on still works, fix what broke and log it. Use when an update is detected or the user says they updated.
---

# Post-update check

1. Refresh the profile: hardware-profile skill. Compare with the previous `notes/hardware.md` (versions, kernel,
   interfaces that appeared or vanished, e.g. a new fan driver or a SteamOS Manager interface).
2. Read `notes/CHANGELOG.md` for everything marked as "redo after updates" (root-fs changes, udev rules, sysctl,
   packages) and check each one.
3. Check, and fix what broke (one at a time, logging each fix):
   - **Decky Loader** loads and its plugins start: `cat ~/homebrew/services/.loader.version`; newest log in
     `~/homebrew/logs/<plugin>/` for tracebacks / ImportError (Decky's Python has lost modules before). Reinstall Decky
     from decky.xyz (Desktop Mode) if it's gone.
   - **Sidequest's panel** in Game Mode (user checks): opens, terminal attaches, Start/Stop/New session work.
   - **Steam's devtools** (`curl -s 127.0.0.1:8080/json | head`), needed by the steam-library tools: test a read-only
     call, e.g. `.claude/skills/steam-library/launch-options.sh "<a collection>"`.
   - **User services** from `notes/CHANGELOG.md`: `systemctl --user --failed`, plus `is-active` for each one listed.
   - **Controllers** (`notes/hardware.md` Controllers section; InputPlumber active?) and anything the device folder
     says to verify after updates.
   - **sshd** or other system services the user enabled (CHANGELOG).
4. Log a dated "post-update check" entry in `notes/CHANGELOG.md`: versions before → after, what was OK, what was fixed.
5. If the update changed something other users of this device or OS will hit, offer to contribute the finding.
