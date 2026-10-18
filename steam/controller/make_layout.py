#!/usr/bin/env python3
"""Build the Steam Input layout for the "Claude Code" shortcut (Legion Go).

    python3 make_layout.py [STEAM_ACCOUNT_ID] > controller_legion_go.vdf
STEAM_ACCOUNT_ID is the numeric folder name under ~/.local/share/Steam/userdata (install_layout.sh passes it).

Install with ./install_layout.sh (Steam must be closed, or it overwrites the file).

Layout:
  A Enter | B Escape | X Shift+Tab (mode) | Y on-screen keyboard
  D-pad arrows (repeat) | left stick scroll | right trackpad mouse
  LT Esc Esc (rewind) | RT hold = Space (push-to-talk)
  LB/RB Page Up/Down | Menu "/" | View Tab
  back buttons: 1 / 2 / 3 (permission prompts) and Ctrl+O (transcript)
"""

def binding(*b):
    return {"bindings": [("binding", x) for x in b]}

def act(kind, keys, **settings):
    """One activator. keys: list of binding strings."""
    a = {"bindings": [("binding", k) for k in keys]}
    if settings:
        a["settings"] = {k: str(v) for k, v in settings.items()}
    return (kind, a)

def press(*keys, **s):
    return [act("Full_Press", list(keys), **s)]

def combo(mod, key):
    # Steam's own pattern (launcher_kbm.vdf): modifier first, key 25 ms later.
    return [act("Full_Press", [f"key_press {mod}"]),
            act("Full_Press", [f"key_press {key}"], delay_start=25)]

def repeat(key):
    return [act("Full_Press", [key], hold_repeats=1, repeat_rate=60)]

def inputs(**m):
    return {name: {"activators": acts, "disabled_activators": {}} for name, acts in m.items()}

groups = [
    ("0", "four_buttons", inputs(
        button_a=press("key_press RETURN"),
        button_b=press("key_press ESCAPE"),
        button_x=combo("LEFT_SHIFT", "TAB"),
        button_y=press("controller_action SHOW_KEYBOARD"),
    ), None),
    ("9", "dpad", inputs(
        dpad_north=repeat("key_press UP_ARROW"),
        dpad_south=repeat("key_press DOWN_ARROW"),
        dpad_east=repeat("key_press RIGHT_ARROW"),
        dpad_west=repeat("key_press LEFT_ARROW"),
    ), None),
    # Left stick: push up/down to scroll the session.
    ("3", "dpad", inputs(
        dpad_north=[act("Full_Press", ["mouse_wheel SCROLL_UP"], hold_repeats=1, repeat_rate=50, interruptable=0)],
        dpad_south=[act("Full_Press", ["mouse_wheel SCROLL_DOWN"], hold_repeats=1, repeat_rate=50, interruptable=0)],
    ), None),
    ("8", "joystick_move", {}, None),
    # Right trackpad as a mouse, tap/click = left click.
    ("2", "absolute_mouse", inputs(click=press("mouse_button LEFT")), None),
    # LT: Escape twice (Claude Code's rewind menu).
    ("4", "trigger", inputs(click=[
        act("Start_Press", ["key_press ESCAPE"]),
        act("Start_Press", ["key_press ESCAPE"], delay_start=120),
    ]), {"output_trigger": "0"}),
    # RT: hold = Space, for /voice hold-to-talk.
    ("5", "trigger", inputs(click=press("key_press SPACE", haptic_intensity=2)), {"output_trigger": "0"}),
    ("7", "switches", inputs(
        button_escape=press("key_press FORWARD_SLASH"),   # Menu (≡)
        button_menu=press("key_press TAB"),               # View (⧉)
        left_bumper=repeat("key_press PAGE_UP"),
        right_bumper=repeat("key_press PAGE_DOWN"),
        button_back_left=press("key_press 1"),
        button_back_left_upper=press("key_press 2"),
        button_back_right=press("key_press 3"),
        button_back_right_upper=combo("LEFT_CONTROL", "O"),
    ), None),
]

sources = [("7", "switch active"), ("0", "button_diamond active"), ("2", "right_trackpad active"),
           ("3", "joystick active"), ("4", "left_trigger active"), ("5", "right_trigger active"),
           ("8", "right_joystick active"), ("9", "dpad active")]

def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

def emit(obj, ind):
    out = []
    items = obj if isinstance(obj, list) else obj.items()
    for k, v in items:
        if isinstance(v, (dict, list)):
            out += [f"{ind}{q(k)}", f"{ind}{{"] + emit(v, ind + "\t") + [f"{ind}}}"]
        else:
            out.append(f"{ind}{q(k)}\t\t{q(str(v))}")
    return out

import sys
account = int(sys.argv[1]) if len(sys.argv) > 1 else 0
creator = str(76561197960265728 + account) if account else "0"   # SteamID64 of the account
import os
url = ("autosave://" + os.path.expanduser("~") + "/.local/share/Steam/steamapps/common/Steam Controller Configs/"
       f"{account}/config/claude code/controller_legion_go.vdf")
root = [("version", "3"), ("revision", "4"), ("title", "Claude Code terminal"),
        ("description", "Terminal layout for Claude Code (claude-deck)"),
        ("creator", creator), ("progenitor", "default://claude code"),
        ("url", url),
        ("export_type", "unknown"), ("controller_type", "controller_legion_go"),
        ("controller_caps", "23117823"), ("major_revision", "0"), ("minor_revision", "0"),
        ("timestamp", "0")]
for gid, mode, inp, settings in groups:
    g = [("id", gid), ("mode", mode), ("name", ""), ("description", ""), ("inputs", inp)]
    if settings:
        g.append(("settings", settings))
    root.append(("group", g))
root.append(("preset", [("id", "0"), ("name", "Default"), ("group_source_bindings", sources)]))
root.append(("settings", [("left_trackpad_mode", "0"), ("right_trackpad_mode", "0")]))

print("\n".join(emit([("controller_mappings", root)], "")))
