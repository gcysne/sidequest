---
name: power-thermals
description: Power and thermal management on the handheld - TDP and performance profiles (SteamOS Manager), CPU boost, GPU clock levels, fan behaviour, charger-dependent profiles, battery care. Use for overheating, loud or silent fans, throttling, battery drain, or "use more/less power on AC".
---

# Power and thermals

1. **What the device exposes:** `notes/hardware.md` → "Power and thermals" (SteamOS Manager interfaces, available
   profiles, TDP range, firmware power attributes, fan sensors/control, battery charge-limit support). Never assume
   another device's controls exist.
2. **Device knowledge first:** `devices/<vendor>/<model>/power-thermals/`, `devices/<vendor>/_common/` (e.g. Lenovo:
   the QAM TDP slider switches the firmware to a quiet fan table; use the performance profile on AC instead,
   `devices/lenovo/_common/power-thermals/profile-on-ac/`).
3. **Controls (no root):** SteamOS Manager on the user bus:
   `busctl --user set-property com.steampowered.SteamOSManager1 /com/steampowered/SteamOSManager1 com.steampowered.SteamOSManager1.PerformanceProfile1 PerformanceProfile s <profile>`;
   `TdpLimit1.TdpLimit u <watts>` (only in profiles that expose it); `CpuBoost1`, `GpuPerformanceLevel1`. These are
   what the QAM sliders and Steam's per-game profiles use, so Steam may override them at game launch.
4. **Diagnose heat:** measure with the performance skill (CPU temperature, clocks, power over time). Throttling
   shows as clocks dropping at the temperature limit. Ask the user whether the fans get louder (many devices expose
   no fan sensor).
5. **Fan control** beyond what the OS exposes (ACPI calls, embedded-controller fan tables) is a firmware-level write:
   explain the risk, get explicit approval, and prefer anything the vendor profiles already offer.
6. **Battery care:** charge limits only where the hardware/driver supports them (hardware.md); otherwise say so.
7. Background services that change profiles must restore the previous state when they stop, log what they do, and
   leave manual changes alone. Log every change in `notes/CHANGELOG.md`.
