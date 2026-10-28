---
name: controllers
description: Fix controller problems on the handheld - built-in or external controllers not detected, wrong buttons or stuck inputs, wrong player order in emulators, Steam's mapping for unknown Bluetooth/USB controllers. Use when a controller doesn't work, buttons are wrong or stuck, or players are in the wrong order.
---

# Controllers

## How input reaches games (SteamOS Game Mode)

Physical controller → (device driver / InputPlumber for built-in controls) → **Steam Input** → one Steam virtual pad
per controller (`28de:11ff`, kernel name "Microsoft X-Box 360 pad N") → the game. Player order = Steam's slot order,
listed in `~/.local/share/Steam/config/virtualgamepadinfo.txt`. Games and emulators should bind players to those
virtual pads **by index**.

## Diagnose (read-only first)

- What's connected: `cat /proc/bus/input/devices` (names, vendor:product, bus 0003 USB / 0005 Bluetooth),
  `lsusb`, the hardware profile's Controllers section, `journalctl -b | grep -i -E 'hid|input|xpad'`.
- Built-in controls: the device folder (`devices/<vendor>/<model>/controllers/`, README) says which daemon handles them
  (e.g. InputPlumber: `journalctl -b -u inputplumber`, `busctl --system tree org.shadowblip.InputPlumber`).
- Live values: read a virtual pad's axes/buttons with `EVIOCGABS` ioctls on `/dev/input/eventN` (no root needed
  for the user's devices) while the user presses buttons.

## Stuck or inverted inputs from an unknown controller

Steam doesn't know many third-party pads (e.g. Bluetooth "Xbox Wireless Controller" clones with their own vendor id)
and uses an SDL mapping, possibly one the user created with "Setup Device Inputs". Saved mappings are the
`SDL_GamepadBind` lines in `~/.local/share/Steam/config/config.vdf` (`steam:2` = user-made). Check the trigger and
axis entries against the device's real axes (`EVIOCGABS` ranges): e.g. `lefttrigger:-a2` (negative half of an axis
that rests at 0) reads as **fully pressed** at rest once the axis has moved: a "held" button after the first press.

Fix options:
1. The user redoes Steam > Settings > Controller > the controller > Setup Device Inputs (press triggers fully).
2. Edit the line: Steam overwrites `config.vdf` on exit, so back it up, start a watcher that waits for the Steam client
   process to exit and then edits the file, and restart Steam with `SteamClient.User.StartRestart(false)` (keeps the
   Game Mode session). Verify with `SteamClient.Input.GetControllerMappingString(<index>)`.

## Emulators

- Bind players 1-4 to Steam pads 0-3 by index. Emulator-specific settings and pitfalls (e.g. EmuDeck's AutoMap hiding
  Steam's pads): stack folder.
- Emulators that bind by **name** (Dolphin: `SDL/<n>/<name>`) break whenever the set of controllers changes:
  `controller-sync/controller-sync --install` keeps Dolphin's GCPad/Wiimote devices in step with Steam's slots
  (user service, re-syncs whenever the slots file changes; `--status` shows the mapping).
- Some games only accept certain controller types (e.g. a Switch game that wants Handheld or single Joy-Con): the
  emulator log says which; fix with a per-game emulator config.

Log every change; back up configs before editing.
