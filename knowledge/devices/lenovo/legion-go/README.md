# Lenovo Legion Go (1st generation)

Maintainers: @gcysne. Facts verified on a 83E1 (Z1 Extreme, BIOS N3CN39WW), SteamOS 3.9.5.

## Display
- 2560x1600 panel, 60 and 144 Hz modes, no VRR. Even frame pacing: cap at 30 (60 Hz) or 36/48/72 (144 Hz).
- Much higher resolution than a Steam Deck: for demanding games render at 1280x800 (exactly half, scales cleanly)
  with FSR/XeSS rather than native.

## Memory
- The BIOS reserves a fixed GPU carve-out (UMA frame buffer). With 4 GB reserved, the OS sees ~11.3 GB. Heavy PC
  games want 16 GB: keep textures low/medium and make sure swap is large enough (`notes/hardware.md` shows it).

## Controllers
- SteamOS's InputPlumber handles the detachable controllers, attached and detached. **Don't install Handheld Daemon
  (HHD)**: it fights InputPlumber for the controllers and its installer refuses SteamOS.
- On detach the receiver re-enumerates (`17ef:6182` → `6184` for a few seconds → `6182`); InputPlumber re-attaches it.
  Desktop Steam's controller list may not refresh; test in Game Mode.
- The back buttons (Y1–Y3, M2, M3) reach games through Steam Input but not Steam's own UI (Decky plugins can't use them).

## Power and thermals
- See `../_common/README.md`: the QAM TDP slider uses a quiet fan table; on AC use the performance profile
  (`../_common/power-thermals/profile-on-ac/`).
- Performance profile limits: 20 W sustained, 30 W / 35 W boost, CPU current limit 20.

## Known-good settings
- Switch emulation (Ryujinx), docked 1080p: most 2D/light 3D games hold 60 fps on AC in the performance profile.
  Breath of the Wild / Tears of the Kingdom need the UltraCam 60 fps mods (nx-optimizer) and run hot.
