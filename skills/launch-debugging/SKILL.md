---
name: launch-debugging
description: Diagnose and fix PC games (Steam/Proton or non-Steam) that fail to launch, crash, hang, or misbehave on the handheld - Proton versions, logs, anti-cheat, launchers, prefixes, shader cache, display and controller issues. Use when a game doesn't start or crashes.
---

# Launch debugging

1. **Identify the game:** name → appid via `steamapps/appmanifest_*.acf` (all libraries in `libraryfolders.vdf`).
2. **Research first:** ProtonDB (`https://www.protondb.com/api/v1/reports/summaries/<appid>.json`), the Steam Deck
   compatibility report (`https://store.steampowered.com/saleaction/ajaxgetdeckappcompatibilityreport?nAppID=<appid>`),
   the game's known issues, required launch options or Proton versions. Deck reports apply loosely to other
   handhelds (resolution, GPU, controller differ: check the device folder).
3. **Evidence before changes:**
   - Ask the user to set launch options `PROTON_LOG=1 %command%` and launch once → `~/steam-<appid>.log`.
   - `~/.local/share/Steam/logs/` (`console_log.txt`, `content_log.txt`) and `journalctl --user -b` around the launch.
   - GPU hangs / OOM kills: `journalctl -b -k | grep -i -E 'amdgpu|oom|killed process'`.
4. **Common causes, roughly in order:** wrong/old Proton (try Experimental, the latest stable, GE-Proton), anti-cheat
   without Linux support (EAC/BattlEye: check the game's status; nothing to fix locally), launchers (EA app, Ubisoft
   Connect, Rockstar: may need touch/mouse, an update, or a clean prefix), corrupt prefix or shader cache, display
   resolution/refresh, controller detection, too little RAM/swap for the game (device folder: memory notes).
5. **Change one thing at a time**, reversible first (launch options, Proton version). Back up
   `compatdata/<appid>/pfx` (saves can live there) before deleting or recreating a prefix.
6. **Report:** root cause, what changed, how to revert. Record the working setup in `notes/games/<game>.md` and the
   change in `notes/CHANGELOG.md`. A fix that will help others on this device → offer to contribute it.
