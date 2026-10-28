---
name: screen-control
description: See and control the Desktop Mode screen (KDE Plasma, Wayland) with screenshots and injected mouse/keyboard input, for GUI-only tasks. Always asks the user first. Use only when no command-line route exists.
---

# Screen control (Desktop Mode)

Slow and imprecise: a fallback. Before every use ask: "This step needs the GUI. Do you want me to try it with screen
control, or should I give you the exact steps?" Proceed only after a yes, for that step only. Game Mode is out of
scope (gamescope): give the user exact instructions there.

## Setup (once; show the plan, explain each sudo step, log everything)

1. Environment: `echo $XDG_SESSION_TYPE` (wayland), `plasmashell --version`, `kscreen-doctor -o` (outputs,
   resolution, rotation, scale). Record in `notes/hardware.md` Observations.
2. Screenshots: `spectacle -b -n -f -p -o FILE` (background, no notification, full screen, with pointer); read it.
3. Input: `ydotool` via kernel uinput (Wayland blocks X11 tools). Home-folder build or a Distrobox package; `ydotoold`
   as a **user** service with a fixed socket (`YDOTOOL_SOCKET`). Access to `/dev/uinput` needs a udev rule (sudo;
   check it survives OS updates). Set a flat pointer-acceleration profile for the virtual device, then calibrate:
   move to known points, screenshot with `-p`, check the cursor lands right. Record the scale factors.
4. Test with the user watching: open a harmless app, click a known button, confirm with a screenshot. Log
   "screen control set up" in `notes/CHANGELOG.md`.

## Rules

- Screenshot before and after every action; never click from a stale screenshot.
- Convert image coordinates with the recorded scale factors (screenshots may be downscaled); say which factor you used.
- Prefer keyboard shortcuts and typed input over clicking small targets.
- Never click through confirmations for purchases, account changes, deletions, firmware updates or anything that
  sends data out; never type passwords (hand the keyboard back).
- Two misses on the same action: stop and give instructions instead.
