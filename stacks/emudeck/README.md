# EmuDeck

Applies when `~/.config/EmuDeck/settings.sh` exists (hardware-profile lists it). Verified with EmuDeck on SteamOS
3.9.5; emulator versions change often, so check before relying on details.

## Paths

- Emulation root: `emulationPath` in `~/.config/EmuDeck/settings.sh` (internal or SD card). Below it: `roms/<system>/`
  (ES-DE system names: `snes`, `megadrive`, `psx`, `gc`, `switch`...), `bios/`, `saves/`, `storage/`,
  `tools/launchers/<emulator>.sh`, `tools/downloaded_media/<system>/` (scraped art).
- ES-DE game lists: `~/ES-DE/gamelists/<system>/gamelist.xml`. ES-DE is EmuDeck's frontend (one Steam shortcut).
- BIOS/firmware/keys go in `bios/` (user-supplied only).

## Steam shortcuts for single games

Exe `"<emulationPath>/tools/launchers/<emu>.sh"`, start dir `"<emulationPath>/tools/launchers/"`, launch options:
`--fullscreen "<rom>"` (Ryujinx), `-f -g "<rom>"` (PPSSPP), `-f "<rom>"` (mGBA). Title = No-Intro title without tags,
", The" moved to the front. Use the steam-library skill (live, no Steam restart).

## Controllers: turn EmuDeck AutoMap off

EmuDeck's AutoMap (`autoMapSwitch`, `autoMapDolphin`, `autoMapCemu` in `settings.sh`; `.automap.*` in
`~/.config/EmuDeck/settings.json`) makes its launchers hide Steam's virtual pads and rewrite Ryujinx/Dolphin/Cemu
bindings on every launch: in Game Mode games then lose controllers or get the wrong player order. Set them to
`false` (back up both files first), then bind players to Steam's pads by index (controllers skill). Re-check after
EmuDeck updates or "reset" actions.

Per emulator, player N = Steam pad N-1:

| Emulator | Setting |
|---|---|
| Ryujinx | `input_config` Player1-4 ids `<n>-00000003-28de-0000-ff11-000001000000`, Pro Controller; motion from the controller (GamepadDriver) on P1 |
| Dolphin | binds by device **name** (`SDL/<n>/<name>`): keep in sync with `skills/controllers/controller-sync`; `SIDevice1-3 = 6` and `Wiimote2-4 Source = 1` for extra players |
| Cemu | controller1-3 uuids → pads 1-3 |
| RMG (N64) | profiles per player (Automatic) |
| xemu, Flycast | ports 2-4 on the same GUID / `maple_sdl_joystick_1..3` |
| RetroArch, DuckStation, PCSX2, RPCS3 | fine by default (DuckStation: multitap off unless a game needs it) |

## Nintendo Switch (Ryujinx)

- Needs the user's `prod.keys`/`title.keys` and firmware. Keys in `~/.config/Ryujinx/system/` (EmuDeck links
  `bios/ryujinx/keys`). Firmware can be installed by hand: each NCA as `bis/system/Contents/registered/<id>.nca/00`.
- Some games need a minimum firmware (Pokémon Let's Go: 9.0+). Check the log's "Using Firmware Version".
- **Updates and DLC must be registered per game** or games launched from Steam run without them: Ryujinx records
  them only during its window's library scan. Base title ID lower-case = `<id>`:
  - Updates: `~/.config/Ryujinx/games/<id>/updates.json` = `{"selected": "<newest update path>", "paths": [<base>, <update>...]}`.
  - DLC needs NCA ids from inside the files: open the Ryujinx window once in Desktop Mode (library scan) until
    `games/<id>/dlc.json` exists. Confirm with `Loading update NCA` / `AddAocItem` in the boot log.
  - Keep updates/DLC out of `roms/switch/` (ES-DE would list them): `storage/switch/<game>/{updates,dlc}/`.
- Global: docked mode = 1080p output; Vulkan.
- **Per-game config**: `~/.config/Ryujinx/games/<id>/Config.json` (a full copy of the global `Config.json` with
  changes) is used when the game is launched. Example: Pokémon Let's Go accepts only Handheld / single Joy-Con / Poké
  Ball (log: "Hid Remap: No matching controllers found. Application requests 'Handheld, JoyconLeft, JoyconRight,
  Pokeball'"): per-game config with `docked_mode: false`, `res_scale: 1.5` (720p × 1.5 = 1080p) and Player1 replaced by
  `Handheld` (controller_type Handheld) on Steam pad 0.
- 60 fps mods for 30-fps Zelda titles: UltraCam from MaxLastBreath/nx-optimizer (BotW, TotK) in
  `~/.config/Ryujinx/mods/contents/<id>/`. Very CPU/thermal heavy: pair with the device's best cooling profile.
- "GPU processing thread is too slow, waiting on CPU" bursts in the log = CPU-bound: usually thermal throttling
  (power-thermals skill), not GPU settings.

## Scraping

Skyscraper (rom-library skill) with frontend `esde` writes ES-DE game lists and `downloaded_media`.
