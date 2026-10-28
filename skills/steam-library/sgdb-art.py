#!/usr/bin/env python3
"""Download SteamGridDB hero / logo / wide (+ cover if asked) for a Steam shortcut, via the public API (no key).
Usage: sgdb-art.py OUTDIR SGDB_GAME_ID [--cover] [--skip N:kind ...]
Writes OUTDIR/{hero,logo,wide[,cover]}.{png,jpg} and OUTDIR/SOURCES.txt. Picks the highest-scored asset that is not
nsfw/humor/epilepsy/animated; wide = landscape grid, cover = portrait grid. --skip 1:wide takes the 2nd wide instead.
Always look at the result before applying (add-shortcut.sh --art, or set-art.sh for existing shortcuts)."""
import json, os, sys, urllib.request
H = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
get = lambda u, d=None: urllib.request.urlopen(urllib.request.Request(u, data=d, headers=H), timeout=30).read()

def assets(kind, gid, page):
    body = json.dumps({"asset_type": kind, "game_id": [gid], "page": page, "limit": 48, "order": "score_desc", "filters": {}})
    return json.loads(get("https://www.steamgriddb.com/api/public/search/assets", body.encode()))["data"]["assets"]

def main():
    out, gid = sys.argv[1], int(sys.argv[2])
    kinds = [("hero", "hero", None), ("logo", "logo", None), ("wide", "grid", "land")]
    if "--cover" in sys.argv: kinds.append(("cover", "grid", "port"))
    skip = dict((k, int(n)) for n, k in (a.split(":") for a in sys.argv[3:] if ":" in a))
    os.makedirs(out, exist_ok=True); src = [f"SteamGridDB game {gid} https://www.steamgriddb.com/game/{gid}"]
    for name, kind, shape in kinds:
        ok = []
        for page in range(4):
            a = assets(kind, gid, page)
            ok += [x for x in a if not (x.get("nsfw") or x.get("humor") or x.get("epilepsy") or x.get("is_animated"))
                   and x.get("mime") in ("image/png", "image/jpeg")
                   and (shape is None or (shape == "land") == (x["width"] > x["height"]))]
            if len(ok) > skip.get(name, 0) or not a: break
        for f in os.listdir(out):
            if f.split(".")[0] == name: os.remove(os.path.join(out, f))
        if len(ok) <= skip.get(name, 0):
            src.append(f"{name}: none"); continue
        x = ok[skip.get(name, 0)]; ext = "png" if x["mime"] == "image/png" else "jpg"
        open(f"{out}/{name}.{ext}", "wb").write(get(x["url"]))
        src.append(f"{name}.{ext} {x['width']}x{x['height']} {x['url']}")
    open(f"{out}/SOURCES.txt", "w").write("\n".join(src) + "\n")
    print(gid, [s.split(" http")[0] for s in src[1:]])

main()
