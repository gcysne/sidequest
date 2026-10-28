#!/usr/bin/env bash
# Apply artwork to EXISTING Steam shortcuts live (CEF devtools on 127.0.0.1:8080), no Steam restart.
# Usage: set-art.sh APPID:ARTDIR [APPID:ARTDIR ...]
#   ARTDIR may hold cover / hero / logo / wide as .png or .jpg (from sgdb-art.py); missing ones are left unchanged.
# New shortcuts: use add-shortcut.sh --art DIR instead.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../../lib/sqpaths.sh
. "$HERE/../../lib/sqpaths.sh"
(($#)) || { sed -n '2,5p' "$0"; exit 2; }
curl -s -m 3 http://127.0.0.1:8080/json >/dev/null || { echo "Steam devtools not reachable on 127.0.0.1:8080"; exit 1; }
WORK=$(mktemp -d); trap 'kill ${SRV:-0} 2>/dev/null || true; rm -rf "$WORK"' EXIT
# Serve every art folder under WORK/<appid> (symlinks) to the Steam JS context.
for pair in "$@"; do
    id="${pair%%:*}"; dir="${pair#*:}"
    [[ "$id" =~ ^[0-9]+$ && -d "$dir" ]] || { echo "bad argument: $pair"; exit 2; }
    ln -s "$(realpath "$dir")" "$WORK/$id"
done
PORT=$((20000 + RANDOM % 20000))
python3 -I "$SQ_LIB/steam-cdp/corsserve.py" "$WORK" "$PORT" >/dev/null 2>&1 & SRV=$!
sleep 1
IDS=$(printf '%s\n' "$@" | cut -d: -f1 | paste -sd,)
cat >"$WORK/set.js" <<EOF
(async () => {
  const P = $PORT, ids = [$IDS], out = [];
  const b64 = async f => { const r = await fetch('http://127.0.0.1:' + P + '/' + f); if (!r.ok) return null;
    const b = new Uint8Array(await r.arrayBuffer()); let s = '';
    for (let i = 0; i < b.length; i += 32768) s += String.fromCharCode.apply(null, b.subarray(i, i + 32768)); return btoa(s); };
  for (const id of ids) {
    const done = [];
    for (const [n, t] of [['cover', 0], ['hero', 1], ['logo', 2], ['wide', 3]])
      for (const ext of ['png', 'jpg']) {
        const d = await b64(id + '/' + n + '.' + ext);
        if (d) { await SteamClient.Apps.SetCustomArtworkForApp(id, d, ext, t); done.push(n); break; }
      }
    out.push(id + ': ' + (done.join(',') || 'nothing'));
  }
  return out.join('\n');
})()
EOF
sq_steam_js "$WORK/set.js"
