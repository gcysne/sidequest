#!/usr/bin/env python3
"""Discover this handheld's hardware and software and match it to Sidequest's device folders.

Usage: discover.py [--json] [--write NOTES_DIR]
  default    print the profile as Markdown
  --json     print it as JSON
  --write D  write D/hardware.md (keeps anything below the "## Observations" heading) and D/hardware.json

Read-only: it only reads /sys, /proc, /etc, D-Bus properties and command output. No root needed.
"""
import glob, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

SIDEQUEST = Path(os.environ.get("SIDEQUEST_HOME", Path.home() / ".local/lib/sidequest"))
if not (SIDEQUEST / "devices").is_dir():          # running from a git clone
    SIDEQUEST = Path(__file__).resolve().parents[2]


def read(p, default=""):
    try:
        return Path(p).read_text(errors="replace").strip()
    except OSError:
        return default


def run(*cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def dmi():
    keys = ["sys_vendor", "product_name", "product_version", "product_family", "board_vendor", "board_name",
            "bios_version", "bios_date"]
    return {k: read(f"/sys/class/dmi/id/{k}") for k in keys}


def os_info():
    rel = dict(re.findall(r'^(\w+)="?([^"\n]*)"?$', read("/etc/os-release"), re.M))
    return {"id": rel.get("ID", ""), "name": rel.get("PRETTY_NAME", ""), "version": rel.get("VERSION_ID", ""),
            "build": rel.get("BUILD_ID", ""), "variant": rel.get("VARIANT_ID", ""), "kernel": os.uname().release,
            "readonly_root": run("steamos-readonly", "status") or None,
            "decky": read(Path.home() / "homebrew/services/.loader.version") or None,
            "steam_client": read(Path.home() / ".local/share/Steam/package/steam_client_ubuntu12.installed") or None}


def cpu():
    info = read("/proc/cpuinfo")
    model = (re.search(r"model name\s*:\s*(.+)", info) or [None, ""])[1]
    cpus = sorted(glob.glob("/sys/devices/system/cpu/cpu[0-9]*"))
    gov = read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    return {"model": model, "threads": len(cpus),
            "max_mhz": int(read("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", "0")) // 1000,
            "scaling_driver": read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_driver"),
            "governor": gov, "epp": read("/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference"),
            "boost": read("/sys/devices/system/cpu/cpufreq/boost") or None}


def gpu():
    out = []
    for dev in sorted(glob.glob("/sys/class/drm/card[0-9]")):
        d = Path(dev) / "device"
        if not (d / "vendor").exists():
            continue
        g = {"card": Path(dev).name, "pci_id": f"{read(d / 'vendor')[2:]}:{read(d / 'device')[2:]}",
             "driver": Path(os.path.realpath(d / "driver")).name}
        slot = Path(os.path.realpath(d)).name
        g["name"] = re.sub(r"^\S+\s+", "", run("lspci", "-s", slot)) or None
        for k, f in (("vram_mb", "mem_info_vram_total"), ("gtt_mb", "mem_info_gtt_total")):
            v = read(d / f)
            g[k] = int(v) // 2**20 if v.isdigit() else None
        od = read(d / "pp_od_clk_voltage")
        m = re.search(r"SCLK:\s*(\d+)Mhz\s+(\d+)Mhz", od)
        g["sclk_range_mhz"] = [int(m[1]), int(m[2])] if m else None
        g["power_level"] = read(d / "power_dpm_force_performance_level") or None
        out.append(g)
    return out


def memory():
    mi = dict(re.findall(r"^(\w+):\s+(\d+)", read("/proc/meminfo"), re.M))
    swaps = [l.split()[0] for l in read("/proc/swaps").splitlines()[1:]]
    return {"ram_visible_mb": int(mi.get("MemTotal", 0)) // 1024, "swap_mb": int(mi.get("SwapTotal", 0)) // 1024,
            "swap_devices": swaps}


def displays():
    out = []
    for c in sorted(glob.glob("/sys/class/drm/card*-*")):
        name = Path(c).name.split("-", 1)[1]
        modes = list(dict.fromkeys(read(f"{c}/modes").split()))
        out.append({"connector": name, "status": read(f"{c}/status"), "modes": modes[:6],
                    "internal": name.startswith(("eDP", "DSI", "LVDS"))})
    return out


def storage():
    try:
        j = json.loads(run("lsblk", "-J", "-b", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,LABEL,FSTYPE,TRAN,RM"))
    except ValueError:
        return []
    out = []
    for d in j.get("blockdevices", []):
        if d.get("type") != "disk" or d["name"].startswith(("zram", "loop")):
            continue
        parts = [p for p in d.get("children", []) or [] if p.get("mountpoint") or p.get("label")]
        out.append({"name": d["name"], "size_gb": round(int(d["size"]) / 1e9), "transport": d.get("tran"),
                    "removable": bool(d.get("rm")),
                    "mounted": [{"label": p.get("label"), "mount": p.get("mountpoint"), "fs": p.get("fstype")}
                                for p in parts if p.get("mountpoint")]})
    return out


def controllers():
    pads, cur = [], {}
    for line in read("/proc/bus/input/devices").splitlines() + [""]:
        if not line.strip():
            if "js" in cur.get("handlers", "") and cur.get("vendor") != "28de":   # skip Steam's virtual pads
                pads.append({k: cur[k] for k in ("name", "vendor", "product", "bus") if k in cur})
            cur = {}
        elif line.startswith("I:"):
            m = dict(re.findall(r"(\w+)=(\w+)", line))
            cur.update(bus={"0003": "usb", "0005": "bluetooth", "0019": "host"}.get(m.get("Bus"), m.get("Bus")),
                       vendor=m.get("Vendor"), product=m.get("Product"))
        elif line.startswith("N:"):
            cur["name"] = line.split("=", 1)[1].strip('"')
        elif line.startswith("H:"):
            cur["handlers"] = line
    daemons = {d: run("systemctl", "is-active", d) or "inactive" for d in ("inputplumber", "hhd@" + os.environ.get("USER", "deck"))}
    return {"physical_pads": pads, "daemons": daemons}


def busprop(iface, prop):
    out = run("busctl", "--user", "get-property", "com.steampowered.SteamOSManager1",
              "/com/steampowered/SteamOSManager1", f"com.steampowered.SteamOSManager1.{iface}", prop)
    if " " not in out:
        return None
    sig, val = out.split(" ", 1)
    if sig == "as":                                  # 'as 2 "a" "b"' -> "a, b"
        return ", ".join(re.findall(r'"([^"]*)"', val))
    return val.strip().strip('"')


def power():
    p = {}
    tree = run("busctl", "--user", "introspect", "com.steampowered.SteamOSManager1", "/com/steampowered/SteamOSManager1")
    p["steamos_manager_interfaces"] = sorted(set(re.findall(r"com\.steampowered\.SteamOSManager1\.(\w+)\s+interface", tree)))
    if "PerformanceProfile1" in p["steamos_manager_interfaces"]:
        p["performance_profile"] = busprop("PerformanceProfile1", "PerformanceProfile")
        p["available_profiles"] = busprop("PerformanceProfile1", "AvailablePerformanceProfiles")
    if "TdpLimit1" in p["steamos_manager_interfaces"]:
        p["tdp_w"] = busprop("TdpLimit1", "TdpLimit")
        p["tdp_range_w"] = [busprop("TdpLimit1", "TdpLimitMin"), busprop("TdpLimit1", "TdpLimitMax")]
    p["platform_profile"] = read("/sys/firmware/acpi/platform_profile") or None
    p["platform_profile_choices"] = read("/sys/firmware/acpi/platform_profile_choices") or None
    fw = {}
    for a in glob.glob("/sys/class/firmware-attributes/*/attributes/*/current_value"):
        parts = Path(a).parts
        fw[f"{parts[-4]}/{parts[-2]}"] = read(a)
    p["firmware_attributes"] = fw or None
    hw = {}
    for h in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
        name = read(f"{h}/name")
        fans = sorted(Path(f).name for f in glob.glob(f"{h}/fan*_input") + glob.glob(f"{h}/pwm[0-9]"))
        hw[name] = fans
    p["hwmon"] = list(hw)
    p["fan_sensors_or_control"] = {k: v for k, v in hw.items() if v} or None
    bats = []
    for b in glob.glob("/sys/class/power_supply/*"):
        if read(f"{b}/type") == "Battery":
            design = read(f"{b}/energy_full_design") or read(f"{b}/charge_full_design")
            full = read(f"{b}/energy_full") or read(f"{b}/charge_full")
            bats.append({"name": Path(b).name,
                         "health_pct": round(100 * int(full) / int(design)) if design.isdigit() and full.isdigit() and int(design) else None,
                         "charge_limit_control": any(Path(f"{b}/{f}").exists() for f in
                                                     ("charge_control_end_threshold", "charge_behaviour"))})
        elif read(f"{b}/type") == "Mains":
            p["ac_online"] = read(f"{b}/online") == "1"
    p["batteries"] = bats
    return p


def stacks():
    s = {}
    if Path.home().joinpath(".config/EmuDeck/settings.sh").exists():
        m = re.search(r'^emulationPath="?([^"\n]+)', read(Path.home() / ".config/EmuDeck/settings.sh"), re.M)
        s["emudeck"] = {"emulation_path": m[1] if m else None}
    if shutil.which("flatpak") and "net.retrodeck.retrodeck" in run("flatpak", "list", "--app", "--columns=application"):
        s["retrodeck"] = {}
    if Path.home().joinpath("homebrew/plugins").is_dir():
        s["decky_plugins"] = sorted(p.name for p in Path.home().joinpath("homebrew/plugins").iterdir() if p.is_dir())
    return s


def load_devices():
    try:
        import yaml
    except ImportError:
        return []
    out = []
    for f in sorted((SIDEQUEST / "devices").glob("**/device.yaml")):
        try:
            d = yaml.safe_load(f.read_text()) or {}
        except yaml.YAMLError:
            continue
        d["_folder"] = str(f.parent.relative_to(SIDEQUEST))
        out.append(d)
    return out


def match_device(ids):
    for d in load_devices():
        for rule in d.get("match") or []:
            if all(str(ids.get(k, "")).strip().lower() == str(v).strip().lower() for k, v in rule.items()):
                return d
    return None


def profile():
    ids = dmi()
    o = os_info()
    dev = match_device(ids)
    folders = []
    if dev:
        vendor = dev["_folder"].split("/")[1]
        folders = [dev["_folder"], f"devices/{vendor}/_common", "devices/_common"]
    else:
        folders = ["devices/_common"]
    os_dir = f"os/{o['id']}" if (SIDEQUEST / "os" / o["id"]).is_dir() else None
    st = stacks()
    return {"generated": time.strftime("%Y-%m-%d %H:%M"), "dmi": ids,
            "device": {"id": dev.get("id") if dev else None, "name": dev.get("name") if dev else None,
                       "folders": [f for f in folders if (SIDEQUEST / f).is_dir()]},
            "os": o, "os_folder": os_dir,
            "stack_folders": [f"stacks/{k}" for k in st if (SIDEQUEST / "stacks" / k).is_dir()],
            "cpu": cpu(), "gpu": gpu(), "memory": memory(), "displays": displays(), "storage": storage(),
            "controllers": controllers(), "power": power(), "software": st}


def markdown(p):
    L = [f"# Hardware profile", "", f"_Generated {p['generated']} by the hardware-profile skill. Re-run after updates;"
         " add your own findings under **Observations** (kept on re-runs)._", ""]
    d = p["dmi"]
    L += ["## Device", "",
          f"- **Model:** {d['sys_vendor']} {d['product_name']} ({d['product_version'] or d['product_family']}), "
          f"board {d['board_name']}, BIOS {d['bios_version']} ({d['bios_date']})"]
    if p["device"]["id"]:
        L.append(f"- **Matched device folder:** `{p['device']['id']}` ({p['device']['name']}). Knowledge: "
                 + ", ".join(f"`{f}`" for f in p["device"]["folders"]))
    else:
        L.append("- **No device folder matches this model.** Generic advice only; consider contributing one "
                 "(contribute skill).")
    o = p["os"]
    L += [f"- **OS:** {o['name']} (version {o['version']}, build {o['build']}), kernel {o['kernel']}"
          + (f", root fs {o['readonly_root']}" if o["readonly_root"] else ""),
          f"- **Decky Loader:** {o['decky'] or 'not installed'}; OS folder: `{p['os_folder'] or 'none'}`; "
          f"stack folders: {', '.join('`'+s+'`' for s in p['stack_folders']) or 'none'}", ""]
    c, m = p["cpu"], p["memory"]
    L += ["## Compute", "",
          f"- **CPU:** {c['model']}, {c['threads']} threads, max {c['max_mhz']} MHz, driver {c['scaling_driver']}, "
          f"governor {c['governor']}, EPP {c['epp'] or '-'}, boost {c['boost'] or '-'}"]
    for g in p["gpu"]:
        L.append(f"- **GPU:** {g['name'] or g['pci_id']} ({g['driver']}), VRAM carve-out {g['vram_mb']} MB, "
                 f"GTT {g['gtt_mb']} MB, clock range {g['sclk_range_mhz'] or '-'} MHz, level {g['power_level']}")
    L += [f"- **Memory:** {m['ram_visible_mb']} MB visible to the OS, swap {m['swap_mb']} MB ({', '.join(m['swap_devices'])})", ""]
    L += ["## Display", ""]
    for x in p["displays"]:
        if x["status"] == "connected":
            L.append(f"- `{x['connector']}` ({'internal' if x['internal'] else 'external'}): modes {', '.join(x['modes']) or '-'}")
    L += ["", "## Storage", ""]
    for s in p["storage"]:
        mounts = "; ".join(f"{x['label'] or '-'} at {x['mount']} ({x['fs']})" for x in s["mounted"])
        L.append(f"- `{s['name']}` {s['size_gb']} GB {s['transport'] or ''}{' removable' if s['removable'] else ''}: {mounts or 'not mounted'}")
    ct = p["controllers"]
    L += ["", "## Controllers", "",
          "- **Daemons:** " + ", ".join(f"{k} {v}" for k, v in ct["daemons"].items())]
    for x in ct["physical_pads"]:
        L.append(f"- {x.get('name')} ({x.get('vendor')}:{x.get('product')}, {x.get('bus')})")
    pw = p["power"]
    L += ["", "## Power and thermals", "",
          f"- **SteamOS Manager interfaces:** {', '.join(pw['steamos_manager_interfaces']) or 'none (not SteamOS?)'}",
          f"- **Performance profile:** {pw.get('performance_profile') or '-'} of {pw.get('available_profiles') or '-'}; "
          f"TDP {pw.get('tdp_w') or '- (not in custom profile)'} W, range {pw.get('tdp_range_w') or '-'}",
          f"- **ACPI platform profile:** {pw['platform_profile'] or '-'} (choices: {pw['platform_profile_choices'] or '-'})",
          f"- **Firmware power attributes:** {pw['firmware_attributes'] or 'none'}",
          f"- **Fan sensors/control:** {pw['fan_sensors_or_control'] or 'none exposed by the kernel'} (hwmon: {', '.join(pw['hwmon'])})",
          f"- **AC power:** {'plugged in' if pw.get('ac_online') else 'battery'}; batteries: "
          + ", ".join(f"{b['name']} health {b['health_pct']}%{' (charge limit control)' if b['charge_limit_control'] else ''}" for b in pw["batteries"]),
          ""]
    sw = p["software"]
    L += ["## Software", ""]
    if "emudeck" in sw:
        L.append(f"- **EmuDeck:** emulation folder {sw['emudeck']['emulation_path']}")
    if "retrodeck" in sw:
        L.append("- **RetroDECK** installed")
    if "decky_plugins" in sw:
        L.append(f"- **Decky plugins:** {', '.join(sw['decky_plugins']) or 'none'}")
    return "\n".join(L) + "\n"


def main():
    p = profile()
    if "--json" in sys.argv:
        print(json.dumps(p, indent=1))
        return
    md = markdown(p)
    if "--write" in sys.argv:
        notes = Path(sys.argv[sys.argv.index("--write") + 1])
        notes.mkdir(parents=True, exist_ok=True)
        old = read(notes / "hardware.md")
        obs = old[old.index("## Observations"):] if "## Observations" in old else "## Observations\n\n"
        (notes / "hardware.md").write_text(md + "\n" + obs.rstrip() + "\n")
        (notes / "hardware.json").write_text(json.dumps(p, indent=1) + "\n")
        print(f"wrote {notes / 'hardware.md'}")
    else:
        print(md)


if __name__ == "__main__":
    main()
