---
name: steam-library
description: Manage non-Steam shortcuts in the Steam library live through Steam's client API - add shortcuts, put them in collections, set launch options, and give them full artwork (cover, hero/header, logo, wide banner) from SteamGridDB, checked visually. Use when adding a game/app to Steam, fixing missing artwork or headers, or changing launch options of many shortcuts.
---

# Steam library

All tools talk to the running Steam client over its devtools port (`lib/steam-cdp/`); changes apply live, no Steam
restart. Steam must be running and Decky Loader installed (it enables the devtools port).

| Tool | Does |
|---|---|
| `add-shortcut.sh --name N --exe PATH [--dir D] [--options O] [--collection C] [--art DIR] [--icon F]` | New shortcut (skips if the name exists), into a collection, with artwork |
| `set-art.sh APPID:DIR ...` | Apply artwork to existing shortcuts |
| `sgdb-art.py OUTDIR SGDB_ID [--cover] [--skip N:kind]` | Download the best hero/logo/wide (and cover) from SteamGridDB |
| `launch-options.sh "<collection>" [add\|remove "<prefix>"]` | List or change launch options of a whole collection (e.g. `MANGOHUD=1 %command% `) |

Artwork folder files: `cover` (600x900), `hero` (wide header, ~1920x620), `logo` (transparent), `wide` (920x430),
as `.png` or `.jpg`. Shortcut ids for `set-art.sh`: ask Steam (`collectionStore.userCollections`, see the scripts).

## Artwork that looks right

1. SteamGridDB game id: `curl -s -A Mozilla/5.0 "https://www.steamgriddb.com/api/public/search/autocomplete?term=<title>"`
   (public API, no key). Pick the entry with the right name and year/platform, not hacks, remakes or other editions.
2. `python3 -I sgdb-art.py <dir> <id>`: top-rated assets, skipping nsfw/joke/animated ones. Keep a scraped cover as
   `cover.png` if the frontend already has one.
3. **Look at every image before applying** (make a contact sheet, read it): official English logo, no other console's
   branding (e.g. a "PlayStation 2" strip), header not tiny, title not baked into the hero twice (if it is, skip the
   logo). Replace bad picks with `--skip 1:<kind>`; if nothing exists, leave it out or build one from another image.
4. Apply, then record the sources (`<dir>/SOURCES.txt`) in `notes/steam-art/<appid>.txt`.

Steam collections: per system or category ("Nintendo Switch", "PSP", "Natives"); ask the user once which systems
get individual shortcuts (thousands of arcade sets would flood the library).
