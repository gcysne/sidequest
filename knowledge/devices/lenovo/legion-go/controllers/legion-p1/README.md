# legion-p1: keep the built-in controller as Player 1 (optional)

When the Legion Go's controllers re-enumerate (detached and reattached, or a mode switch), InputPlumber's
"Legion Go Controller" reappears after any external pads already connected, and Steam gives it a later slot. Anything
that binds Player 1 to Steam pad 0 (Ryujinx, emulators bound by index) then gets the external pad as Player 1.

`legion-p1` watches Steam's slot file (`~/.local/share/Steam/config/virtualgamepadinfo.txt`) and, when the Legion Go
controller (`28de:12fe` in Steam's list) isn't in slot 0, moves it up with `SteamClient.Input.SwapControllerOrder`
(what Quick Access > Reorder Controllers does). Other pads keep their relative order. Works mid-game; a reconnect is
fixed about 2 s later.

Only install it if the owner wants the built-in controller to always be Player 1 (a guest on an external pad can still
be reordered by hand, but this service will move the Legion Go back on the next slot change).

```
legion-p1 --status       # Steam's slots and what a run would do
legion-p1 --install      # user units legion-p1.path + legion-p1.service; --uninstall removes them
```

Needs Steam's devtools port (Decky Loader). Log: `~/.local/state/sidequest/legion-p1.log`.
Verified: Legion Go (1st gen) 83E1, SteamOS 3.9.5, with a Bluetooth pad forced into slot 0: moved back in ~8 s
(path trigger + 2 s settle). Internal Steam API: re-test after Steam updates.
