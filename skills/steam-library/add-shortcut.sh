#!/usr/bin/env bash
# Add a non-Steam shortcut live through Steam's client API (CEF devtools on 127.0.0.1:8080), no Steam restart.
# Usage: add-shortcut.sh --name NAME --exe PATH [--dir DIR] [--options "LAUNCH OPTIONS"] [--collection NAME]
#                        [--art DIR] [--icon FILE]
#   --art DIR: optional cover.png (600x900), hero.png, logo.png, wide.png (920x430) are applied when present.
# Prints JSON with the new app id. If a shortcut with the same name exists, prints it and changes nothing.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../../lib/sqpaths.sh
. "$HERE/../../lib/sqpaths.sh"
NAME="" EXE="" DIR="" OPTS="" COLL="" ART="" ICON=""
while (($#)); do
    case "$1" in
        --name) NAME="$2"; shift 2 ;; --exe) EXE="$2"; shift 2 ;; --dir) DIR="$2"; shift 2 ;;
        --options) OPTS="$2"; shift 2 ;; --collection) COLL="$2"; shift 2 ;; --art) ART="$2"; shift 2 ;;
        --icon) ICON="$2"; shift 2 ;; *) sed -n '2,7p' "$0"; exit 2 ;;
    esac
done
[[ -n "$NAME" && -n "$EXE" ]] || { sed -n '2,7p' "$0"; exit 2; }
[[ -n "$DIR" ]] || DIR="$(dirname "$EXE")/"
curl -s -m 3 http://127.0.0.1:8080/json >/dev/null || { echo '{"error":"Steam devtools not reachable on 127.0.0.1:8080 (is Steam running?)"}'; exit 1; }

WORK=$(mktemp -d); trap 'kill ${SRV:-0} 2>/dev/null || true; rm -rf "$WORK"' EXIT
PORT=0
if [[ -n "$ART" && -d "$ART" ]]; then
    PORT=$((20000 + RANDOM % 20000))
    python3 -I "$SQ_LIB/steam-cdp/corsserve.py" "$ART" "$PORT" >/dev/null 2>&1 & SRV=$!
    sleep 1
fi
# All values go to JS as JSON strings, so names with quotes or apostrophes are safe.
j() { python3 -I -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }
cat >"$WORK/add.js" <<EOF
(async () => {
  const NAME = $(j "$NAME"), EXE = $(j "\"$EXE\""), DIR = $(j "\"$DIR\""), OPTS = $(j "$OPTS");
  const COLL = $(j "$COLL"), ICON = $(j "$ICON"), PORT = $PORT;
  const existing = appStore.allApps.filter(a => a.display_name === NAME).map(a => a.appid);
  if (existing.length) return JSON.stringify({exists: existing});
  const id = await SteamClient.Apps.AddShortcut(NAME, EXE.slice(1, -1), '', '');
  await new Promise(r => setTimeout(r, 300));
  SteamClient.Apps.SetShortcutName(id, NAME);
  SteamClient.Apps.SetShortcutExe(id, EXE);
  SteamClient.Apps.SetShortcutStartDir(id, DIR);
  SteamClient.Apps.SetShortcutLaunchOptions(id, OPTS);
  if (ICON) SteamClient.Apps.SetShortcutIcon(id, ICON);
  const art = [];
  if (PORT) {
    const b64 = async f => { const r = await fetch('http://127.0.0.1:' + PORT + '/' + f); if (!r.ok) return null;
      const b = new Uint8Array(await r.arrayBuffer()); let s = '';
      for (let i = 0; i < b.length; i += 32768) s += String.fromCharCode.apply(null, b.subarray(i, i + 32768)); return btoa(s); };
    for (const [f, t] of [['cover.png', 0], ['hero.png', 1], ['logo.png', 2], ['wide.png', 3]]) {
      const data = await b64(f); if (data) { await SteamClient.Apps.SetCustomArtworkForApp(id, data, 'png', t); art.push(f); }
    }
  }
  let collection = null;
  if (COLL) {
    await new Promise(r => setTimeout(r, 1500));
    let col = collectionStore.userCollections.find(c => c.displayName === COLL);
    if (!col) col = collectionStore.NewUnsavedCollection(COLL, undefined, []);
    col.AsDragDropCollection().AddApps([appStore.GetAppOverviewByAppID(id)]);
    await col.Save();
    collection = COLL;
  }
  return JSON.stringify({id, art, collection});
})()
EOF
sq_steam_js "$WORK/add.js"
