---
name: hardware-profile
description: Discover this handheld's hardware and software (model, CPU/GPU, memory, display modes, storage, controllers, power/TDP/fan interfaces, OS, Decky, emulation stack), match it to Sidequest's device/OS/stack folders and write notes/hardware.md. Use in the first session, after updates, or when device-specific advice is needed and the profile is missing or stale.
---

# Hardware profile

1. Run `python3 .claude/skills/hardware-profile/discover.py --write notes` (read-only, no root). It writes
   `notes/hardware.md` (keeps everything under `## Observations`) and `notes/hardware.json`.
2. Read the result and the matched folders it lists (`knowledge/devices/<vendor>/<model>`, `knowledge/devices/<vendor>/_common`,
   `knowledge/devices/_common`, `knowledge/os/<id>`, `knowledge/stacks/<name>` under `~/.local/lib/sidequest/`).
3. Tell the user, briefly: which device it is, anything notable (e.g. GPU memory carve-out, no fan control, battery
   health, unknown device).
4. Facts the script can't see go under `## Observations` in `notes/hardware.md`, dated: things you measured or the
   user told you (BIOS settings like the GPU carve-out size, panel quirks, controller behaviour).

**No matching device folder:** say so, and offer to create one for this model with the contribute skill: the
discovery output has the DMI fields for `match` and the facts for `device.yaml` (see `knowledge/devices/README.md`). Only
put verified facts in it.

Re-run after SteamOS, BIOS or Decky updates (post-update-check does it), and when hardware changes (new SD card,
BIOS settings).
