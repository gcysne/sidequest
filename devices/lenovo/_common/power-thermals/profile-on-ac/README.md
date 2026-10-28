# profile-on-ac (Lenovo)

Charger plugged in + a game running → Lenovo's **performance** profile (strong fan curve); back to the previous
profile/TDP afterwards. See the script's header for the details and why a fixed TDP is worse on Lenovo devices.

- Install: `./profile-on-ac --install` (user service, no root). Remove: `--uninstall`. Status: `--status`.
- Proton games: add their process name (the `.exe` name cut to 15 characters) to `~/.config/sidequest/profile-on-ac.games`,
  one regex per line, e.g. `JediSurvivor\.e.*`.
- Log: `~/.local/state/sidequest/profile-on-ac.log`.
- Verified on: Legion Go (83E1), SteamOS 3.9.5: Kirby's Return to Dream Land Deluxe (Ryujinx) went from 99 °C and
  6–8 fps drops to 89 °C max and 59.8 fps average.
