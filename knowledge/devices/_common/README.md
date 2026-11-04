# Any SteamOS handheld

Knowledge that holds on every device. Skills read this after the model and vendor folders.

- Steam Input presents every controller to games as a Steam virtual pad (`28de:11ff`), in Steam's player order
  (`~/.local/share/Steam/config/virtualgamepadinfo.txt`). Emulators should bind players to those pads by index.
- The QAM TDP slider and per-game performance profiles go through SteamOS Manager (`com.steampowered.SteamOSManager1`
  on the user bus); what it exposes depends on the device (hardware-profile lists the interfaces).
- Frame-rate caps only pace evenly at divisors of the panel's refresh rate unless the panel has VRR.
