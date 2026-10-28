# Device knowledge

Everything that only applies to some handhelds lives here, so the skills (`skills/`) stay generic.

```
devices/
  _common/                 any SteamOS handheld
  <vendor>/_common/        shared by a vendor's models (drivers, vendor quirks)
  <vendor>/<model>/        one model (or a few that behave the same)
    device.yaml            how to recognise it + facts (required)
    README.md              quirks, known-good settings, maintainers (required)
    <skill>/               scripts, services and notes for that skill on this device
```

The agent looks in the model folder first, then `<vendor>/_common`, then `_common`. The hardware-profile skill
picks the model folder by matching `device.yaml` against the firmware's DMI fields.

## Adding a device

1. Run the hardware-profile skill on the device: it prints the DMI fields (`sys_vendor`, `product_name`, ...).
2. Create `devices/<vendor>/<model>/` (lower-case, hyphens: `asus/rog-ally-x`). Split a model into separate folders
   **only when settings, controls or quirks differ**; otherwise add more `match` rules to one folder.
3. Write `device.yaml` (fields below) and a `README.md`. Only state facts you verified on the device; mark the rest
   as unverified.
4. `python3 ci/check-devices.py` must pass. Then open a pull request (the contribute skill does all of this).

## device.yaml

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Folder path below `devices/`, e.g. `lenovo/legion-go` |
| `name` | yes | Human name |
| `match` | yes | List of rules; a rule matches when **all** its DMI fields equal the device's (case-insensitive) |
| `maintainers` | yes | GitHub handles who review changes to this folder |
| `soc`, `display`, `controllers`, `power`, `tested`, `notes` | no | Facts: see `lenovo/legion-go/device.yaml` for the shape |
