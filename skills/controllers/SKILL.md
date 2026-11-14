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
- Built-in controls: the device folder (`knowledge/devices/<vendor>/<model>/controllers/`, README) says which daemon handles them
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

## No rumble from a Bluetooth "Xbox Wireless Controller" clone

Third-party pads in Xbox/Bluetooth mode often copy the Xbox One S/Series HID descriptor but keep their own vendor id,
so the kernel binds `hid-generic` instead of `hid-microsoft`: the pad's input device has no force feedback, and
Steam's virtual pad accepts a game's rumble but has nothing to send it to.

Find the layer that loses it, with `rumble-test/rumble-test` (no root):
1. `--list`: driver and `rumble=yes/no` per controller and per Steam virtual pad (slot N = "Microsoft X-Box 360 pad N").
2. Hardware: if the pad's HID descriptor (`/sys/class/hidraw/hidrawN/device/report_descriptor`) has a Physical Interface
   (usage page `0x0F`) output report 3, `--xbox-bt-raw /dev/hidrawN` should buzz. No buzz: firmware/mode limit;
   try the pad's 2.4 GHz dongle or wired mode instead.
3. Kernel: `--evdev` on the pad's own `/dev/input/eventN`. Steam: `--evdev` on its virtual pad.

Fix when 2 works and 1 says `rumble=no` (verified: Machenike G5 Pro, BT Xbox mode, `0005:1949:040a`, on a Legion Go,
SteamOS 3.9.5, kernel 7.2.7-valve2): give `hid-microsoft` the id with its force-feedback quirk. The quirk value is
the `driver_data` of the genuine Xbox BT entries in the running kernel's module (`0x80` = `MS_QUIRK_FF` on 7.2;
read it from the `hid_device_id` table of `hid-microsoft.ko` rather than assuming it). Its sysfs driver name is
`microsoft`. This needs root and is a system change: explain it and get the user's approval first.

- Try it live: `echo <bus:dev> > /sys/bus/hid/drivers/hid-generic/unbind`, then
  `echo "0005 <vid> <pid> 80" > /sys/bus/hid/drivers/microsoft/new_id` (binds it; else write the id to `bind`).
  Check `rumble=yes` and that the buttons/axes are unchanged (`KEY=`/`ABS=` bitmaps in `/proc/bus/input/devices`,
  so the user's Steam mapping still applies).
- **Restart Steam** afterwards: it keeps treating a pad that was first seen without rumble as rumble-less, even
  after reconnects. Only after a restart does the Steam-layer test buzz.
- Persist: a system oneshot that registers the id at boot, before the pad can connect, so it binds directly (no
  unbind/rebind on every connect, which a udev rule on the pad would need, and Steam never sees it without rumble).
  `/etc` survives SteamOS updates; log it in the notebook's CHANGELOG. (Live bind verified; the unit across a
  reboot not yet: check `systemctl status` and `--list` after the next boot.)

  ```ini
  # /etc/systemd/system/<pad>-rumble.service
  [Unit]
  Description=Bind <pad> (Bluetooth) to the Xbox BT HID driver for rumble
  Before=bluetooth.service

  [Service]
  Type=oneshot
  RemainAfterExit=yes
  ExecStart=/bin/sh -c 'modprobe hid-microsoft && echo "0005 <vid> <pid> 80" > /sys/bus/hid/drivers/microsoft/new_id || true'

  [Install]
  WantedBy=multi-user.target
  ```
  Revert: `systemctl disable --now` the unit, delete it, reboot.

Not fixed by this (Machenike G5 Pro): the pad never answers HID GET_REPORT (bluetoothd logs `HIDP GET_REPORT request
timed out` every 3 s, probably Steam's requests on hidraw: unverified), and all controllers freeze for up to a minute after it
connects. Similar reports for other brands are open upstream (BlueZ level), unverified fix.

## Emulators

- Bind players 1-4 to Steam pads 0-3 by index. Emulator-specific settings and pitfalls (e.g. EmuDeck's AutoMap hiding
  Steam's pads): stack folder.
- Emulators that bind by **name** (Dolphin: `SDL/<n>/<name>`) break whenever the set of controllers changes:
  `controller-sync/controller-sync --install` keeps Dolphin's GCPad/Wiimote devices in step with Steam's slots
  (user service, re-syncs whenever the slots file changes; `--status` shows the mapping).
- Some games only accept certain controller types (e.g. a Switch game that wants Handheld or single Joy-Con): the
  emulator log says which; fix with a per-game emulator config.

Log every change; back up configs before editing.
