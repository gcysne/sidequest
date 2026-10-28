---
name: rom-library
description: Organize an emulation library - folder per system, No-Intro/Redump file naming, one file per game, BIOS placement, de-duplication, and scraping metadata/artwork for the frontend (Skyscraper). Use when adding or organizing ROMs/disc images, renaming, or fixing missing artwork/metadata in the frontend.
---

# ROM library

Paths and frontend details come from the stack folder (e.g. `stacks/emudeck/README.md`).

## Layout

- One folder per system, using the frontend's system names (ES-DE: `snes`, `megadrive`, `psx`, `gc`, `switch`...).
- **One game = one file** when possible: PS1 as CHD (`chdman createcd -i game.cue -o "Title (Region).chd"`; for
  CCD/IMG write a one-track cue first), PSP as ISO, GameCube as RVZ, cartridges as the ROM or a zip. Multi-file only
  when the format needs it (a folder with the same standard name).
- Extras from ROM sets (manuals, emulators, texture packs) don't go into the library; BIOS files go to the BIOS
  folder (and next to the games when a core needs it, e.g. `neogeo.zip`).
- Damaged files (failed archive tests, bad dumps when a clean one exists) never go in: list them in
  `notes/roms/` and quarantine them, then delete with the user's OK.
- Log every move/rename in `notes/roms/organize-log.tsv`.

## Naming (No-Intro / Redump style)

`Title (Region) (Languages) (Rev N) (Flags).ext`, e.g. `Mega Man X (USA) (v1.1).smc`. `romname.py` implements it:
`python3 .claude/skills/rom-library/romname.py "<old name>"...` prints the standard name (import `standard_name()`
for batch work).

- Regions/languages come from the existing name; **never guess** a missing region.
- GoodTools tags are translated: `(U)`→`(USA)`, `(JUE)`→`(Japan, USA, Europe)`, `[a1]`→`(Alt 1)`, `[h]`→`(Hack)`,
  `[T+Eng]`→`(Translated En)`, `[b]`→`(Bad Dump)`, `[o]`→`(Overdump)`; `[!]`, `[c]`, `[C]` are dropped.
- **Arcade romsets keep their short set names** (`sf2.zip`, lower case): emulators identify them by file name.
- Extensions lower case.

## Scraping (Skyscraper)

- Skyscraper (Gemba fork) isn't packaged for SteamOS: build it in a Distrobox container and link the binary into
  `~/.local/bin`. Config `~/.skyscraper/config.ini`: frontend `esde` (or the user's), input/game list/media paths,
  no videos/manuals unless wanted. Keep `~/.skyscraper/cache` (re-generating lists is then offline and instant).
- Sources: consoles → `screenscraper` (anonymous: 1 thread, 10k requests/day; an account gives more) then
  `thegamesdb` for misses; arcade → `arcadedb`. Long runs as a user unit:
  `systemd-run --user --unit=rom-scrape <script>`.
- New games only: `skyscraper -p <system> -s screenscraper --flags onlymissing`, then `skyscraper -p <system>` to write
  the game list. Unmatched games ("Skipped games"): rename to the official No-Intro/Redump title and retry.
