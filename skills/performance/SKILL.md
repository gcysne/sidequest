---
name: performance
description: Profile, benchmark and optimize games on the handheld - measure fps, frame pacing, CPU/GPU load and clocks, temperatures and power (gamescope stats, MangoHud), find the bottleneck (CPU, GPU, thermal, memory), then tune frame cap, power profile and settings. Use when the user reports low fps, stutter, heat, battery drain, or asks for the best settings.
---

# Performance: measure, find the bottleneck, tune

## Measure

| Tool | When |
|---|---|
| `perf-monitor --until-exit <process>` | Game Mode, any game: per-second CSV in `notes/perf-logs/monitor-*.csv` with fps and focused app (gamescope's stats pipe), CPU temp/clocks, GPU clock/busy/temp, socket power, power limit, Ryujinx CPU stalls. Run detached: `systemd-run --user --unit=perf-monitor .claude/skills/performance/perf-monitor --until-exit <comm>`. **Steam's performance overlay must be off** while it runs (both read the same pipe). `--summary FILE` lists the slow seconds. |
| MangoHud logging | Per game: launch options `MANGOHUD=1 %command%` (steam-library `launch-options.sh` does whole collections) plus a MangoHud config with `output_folder=<notes>/perf-logs`; `perf-summary` summarises the CSVs (avg, 1% low, time under 55 fps). In Game Mode Steam points MangoHud at gamescope's own config, so logging works best in Desktop Mode; turn it off again afterwards. |
| Steam's performance overlay | Quick look for the user (QAM > Performance). |

Always note the conditions: AC/battery, power profile/TDP, resolution, game area, emulator version.

## Find the bottleneck

- **CPU-bound:** GPU busy low (<60%) and GPU clock low while fps drops; one or more CPU cores near max; for Ryujinx,
  "GPU processing thread is too slow, waiting on CPU" in its log.
- **Thermal throttling:** CPU temperature at the limit (~95-100 °C on AMD APUs) right before the drops, clocks
  falling. Fix the cooling side first (power-thermals skill: on some devices the TDP slider uses a quiet fan table).
- **GPU-bound:** GPU busy ~95-100% at high clock: lower resolution/upscale (FSR/XeSS), lighter settings.
- **Memory:** heavy swapping, low "MemAvailable", stutter when loading areas: lower textures, check swap size and
  the GPU carve-out (device folder).
- **Shader compilation stutter:** first-time spikes that disappear on a second run (Steam shader pre-caching, emulator
  shader caches).

## Tune (in this order)

1. **Frame-rate cap** that divides the panel's refresh rate evenly (device folder: refresh modes, VRR). Stable frame
   pacing beats a higher average.
2. **Power:** profile/TDP (power-thermals skill). On AC there's no reason to save power; on battery find the lowest
   TDP that holds the cap.
3. **Settings:** resolution (high-resolution panels: render lower and upscale), then the heaviest options first.
   Emulators: per-game settings, established mods for that exact game version.

Measure before and after; report numbers (avg fps, 1% low, max temperature, power). Write the final settings in
`notes/games/<game>.md` so they're reproducible: in-game settings, launch options, profile/TDP, cap, Proton/emulator
version. Good settings for a game on a device are worth contributing (device folder README, "Known-good settings").
