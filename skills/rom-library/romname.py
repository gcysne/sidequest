"""ROM file naming standard (No-Intro style) for an emulation library.

Target pattern:  Title (Region) (Languages) (Rev N) (Flags).ext
  - Region / languages / revision come from the existing name; nothing is guessed.
  - GoodTools codes are translated: (U) -> (USA), (JUE) -> (Japan, USA, Europe),
    [T+Eng...] -> (Translated En), [h..] -> (Hack), [a2] -> (Alt 2), [b] -> (Bad Dump).
  - Pure quality markers are dropped: [!] verified, [c] checksum ok, [C] GB Color compatible, [S] SGB.
  - Extension lower-cased, whitespace/underscores normalized.
Arcade romsets (MAME/FBNeo/Neo Geo) must NOT be renamed: emulators match them by file name.
"""

import re

GOODTOOLS_REGIONS = {
    "U": "USA", "E": "Europe", "J": "Japan", "W": "World", "B": "Brazil", "K": "Korea",
    "C": "China", "A": "Australia", "F": "France", "G": "Germany", "S": "Spain", "I": "Italy",
    "H": "Netherlands", "D": "Netherlands", "SW": "Sweden", "FN": "Finland", "NL": "Netherlands",
    "UK": "UK", "HK": "Hong Kong", "R": "Russia", "Unk": "Unknown", "PD": "Public Domain",
    "Unl": "Unlicensed", "1": "Japan, Korea", "4": "USA, Brazil", "5": "NTSC", "8": "PAL",
}
NOINTRO_REGIONS = {
    "USA", "Europe", "Japan", "World", "Brazil", "Korea", "China", "Australia", "France", "Germany",
    "Spain", "Italy", "Netherlands", "Sweden", "Asia", "Canada", "UK", "Taiwan", "Hong Kong",
    "Russia", "Scandinavia", "Unknown", "Latin America", "Portugal", "Poland", "Greece", "Denmark",
    "Norway", "Finland",
}
LANG = re.compile(r"^[A-Z][a-z](-[A-Za-z]+)?(,[A-Z][a-z](-[A-Za-z]+)?)*$")
REV = re.compile(r"^(Rev [0-9A-Z.]+|v ?[0-9][0-9.a-z]*|V[0-9][0-9.]*)$")
KNOWN_PAREN = re.compile(r"^(Beta[ 0-9]*|Proto[ 0-9]*|Demo|Sample|Unl|Hack|Alt[ 0-9]*|Bad Dump|"
                         r"Translated [A-Za-z]+|Trainer|Fixed|Overdump|Pirate|Virtual Console|"
                         r"Disc [0-9]+|Disk [0-9]+|Side [AB]|SGB Enhanced|GB Compatible|Rumble Version|"
                         r"NTSC|PAL|Kiosk|Debug|Aftermarket|Homebrew|Track [0-9]+)$")


def _goodtools_region(code: str):
    """'U' -> 'USA', 'JUE' -> 'Japan, USA, Europe', 'UK' -> 'UK'. None if not a region code."""
    if code in GOODTOOLS_REGIONS:
        return GOODTOOLS_REGIONS[code]
    if re.fullmatch(r"[UEJWBKAFGSI]{2,4}", code):
        return ", ".join(GOODTOOLS_REGIONS[c] for c in code)
    return None


def _bracket_flag(tag: str):
    """GoodTools [..] flag -> No-Intro style flag, or None to drop."""
    t = tag.strip()
    if t in ("!", "c", "C", "S", "BF", "x", "M"):
        return None
    m = re.fullmatch(r"a(\d*)", t)
    if m:
        return f"Alt {m.group(1) or 1}"
    if re.fullmatch(r"b\d*.*", t):
        return "Bad Dump"
    if re.fullmatch(r"o\d*", t):
        return "Overdump"
    if re.fullmatch(r"f\d*.*", t):
        return "Fixed"
    if re.fullmatch(r"p\d*.*", t):
        return "Pirate"
    if re.fullmatch(r"t\d*.*", t):
        return "Trainer"
    m = re.fullmatch(r"T[+-]([A-Za-z]{2,3}).*", t)
    if m:
        return f"Translated {m.group(1)[:2].capitalize()}"
    if re.fullmatch(r"h\d*.*", t):
        return "Hack"
    if re.fullmatch(r"(SLUS|SCUS|SLES|SCES|SLPS|SLPM|SCPS)-?\d+", t):  # PS1 serials: drop from name
        return None
    if t == "PS1":
        return None
    return None  # unknown bracket tags are dropped (kept in the rename log)


def standard_name(filename: str) -> str:
    """Return the standardized file (or folder) name for one ROM."""
    m = re.match(r"^(.*?)((?:\.[A-Za-z0-9]{1,4}){0,2})$", filename)
    stem, ext = m.group(1), m.group(2)
    known_ext = {".zip", ".7z", ".rar", ".nes", ".smc", ".sfc", ".swc", ".fig", ".gen", ".md", ".smd",
                 ".gg", ".sms", ".gb", ".gbc", ".gba", ".n64", ".z64", ".v64", ".iso", ".cue", ".bin",
                 ".img", ".ccd", ".sub", ".chd", ".cso", ".rvz", ".wbfs", ".wad", ".nsp", ".xci", ".nkit.iso",
                 ".gcm", ".pbp", ".m3u"}
    if ext.lower() not in known_ext:  # folder names or names with dots in the title
        last = re.search(r"(\.[A-Za-z0-9]{1,4})$", filename)
        if last and last.group(1).lower() in known_ext:
            stem, ext = filename[: -len(last.group(1))], last.group(1)
        else:
            stem, ext = filename, ""
    stem = stem.replace("_", " ")

    regions, langs, revs, flags = [], [], [], []
    # pull out (...) and [...] groups in order
    title_part = re.split(r"\s*[\(\[]", stem, maxsplit=1)[0]
    for kind, inner in re.findall(r"([\(\[])([^\)\]]*)[\)\]]", stem):
        inner = inner.strip()
        if not inner:
            continue
        if kind == "[":
            f = _bracket_flag(inner)
            if f:
                flags.append(f)
            else:
                r = _goodtools_region(inner)
                if r and len(inner) <= 3 and inner not in ("C", "S", "M"):
                    regions.append(r)
            continue
        if KNOWN_PAREN.match(inner):
            flags.append(inner)
        elif all(p.strip() in NOINTRO_REGIONS for p in inner.split(",")):
            regions.append(", ".join(p.strip() for p in inner.split(",")))
        elif _goodtools_region(inner):
            regions.append(_goodtools_region(inner))
        elif LANG.match(inner.replace(" ", "")):
            langs.append(inner.replace(" ", ""))
        elif REV.match(inner):
            v = inner if inner.startswith("Rev") else "v" + inner.lstrip("vV ").strip()
            revs.append(v)
        elif re.fullmatch(r"(?i)rev ?([0-9a-z]+)", inner):
            revs.append("Rev " + re.fullmatch(r"(?i)rev ?([0-9a-z]+)", inner).group(1).upper())
        elif KNOWN_PAREN.match(inner):
            flags.append(inner)
        else:
            # alternate title like "(Hercs Adventures)" or unknown info: keep as-is
            flags.append(inner)

    title = re.sub(r"\s+", " ", title_part).strip(" -")
    parts = [title]
    seen = set()
    for group in (regions[:1], langs[:1], revs[:1], flags):
        for g in group:
            if g not in seen and g.lower() != title.lower():
                parts.append(f"({g})")
                seen.add(g)
    return " ".join(parts) + ext.lower()


if __name__ == "__main__":
    import sys
    for n in sys.argv[1:]:
        print(f"{n!r} -> {standard_name(n)!r}")
