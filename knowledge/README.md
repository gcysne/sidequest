# Shared knowledge

What Sidequest's agent knows about specific **devices**, **operating systems** and **emulation stacks**: the
quirks, known-good settings, fixes, scripts and services that only apply to some setups. The skills in `skills/` stay
generic and look things up here; the hardware-profile skill picks the folders that match your machine.

```
knowledge/
  devices/                 handhelds: devices/<vendor>/<model>/, devices/<vendor>/_common/, devices/_common/
  os/                      operating systems, by /etc/os-release ID: os/steamos/, os/bazzite/...
  stacks/                  emulation suites and frontends: stacks/emudeck/...
```

Most specific first: a model folder wins over its vendor's `_common/`, which wins over `devices/_common/`.

| Folder | What goes in | Guide |
|---|---|---|
| [`devices/`](devices/) | `device.yaml` (how to recognise the model, display modes, controllers, power and fan controls, tested versions), `README.md` (quirks, known-good settings, maintainers), and `<skill>/` subfolders with that device's scripts and services | [devices/README.md](devices/README.md) |
| [`os/`](os/) | The OS's rules: what survives updates, how to install things, where logs are | [os/README.md](os/README.md) |
| [`stacks/`](stacks/) | Paths, launchers, emulator settings and quirks of an emulation suite | [stacks/README.md](stacks/README.md) |

## This grows from real sessions

Every entry here should come from something that worked on a real device. When your agent solves a problem that
other owners would hit, it offers to contribute it (the `contribute` skill): it writes the change into the right
folder, removes personal data, shows it to you, and opens a pull request from your own GitHub account. You can also
just ask: *"Contribute what we learned about this device to Sidequest."*

Rules: no personal data (user names, serials, IPs, game libraries, personal paths), say what was verified (device,
OS version, date), and keep generic logic in the skills. Details: [CONTRIBUTING.md](../CONTRIBUTING.md).
