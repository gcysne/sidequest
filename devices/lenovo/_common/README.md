# Lenovo handhelds (shared)

- Recent kernels drive Lenovo's gaming firmware through the `lenovo-wmi-gamezone` (platform profiles) and
  `lenovo-wmi-other` (power limits as firmware attributes: `ppt_pl1_spl`, `ppt_pl2_sppt`, `ppt_pl3_fppt`, `ppt_cpu_cl`)
  drivers. SteamOS Manager uses them for its performance profiles and the TDP slider.
- **Fans:** in the "custom" profile (any TDP set from the QAM slider) the embedded controller uses a quiet fan table;
  under sustained load the CPU can reach ~99 °C and throttle. Lenovo's own **performance** profile uses an aggressive
  fan curve. With no fan control exposed by the kernel, switching to the performance profile is the practical way
  to get stronger cooling: see `power-thermals/profile-on-ac/`.
- Direct fan control needs the `acpi_call` module (not shipped by SteamOS) and EC writes: firmware-level, explicit
  user approval only.
