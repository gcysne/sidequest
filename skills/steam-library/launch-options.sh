#!/usr/bin/env bash
# Show or change launch options of every shortcut in a Steam collection, live (Steam's client API).
#   launch-options.sh "<collection>"                       list each shortcut's launch options
#   launch-options.sh "<collection>" add "<prefix>"        put <prefix> in front (e.g. "MANGOHUD=1 %command% ")
#   launch-options.sh "<collection>" remove "<prefix>"     take it off again
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../../lib/sqpaths.sh
. "$HERE/../../lib/sqpaths.sh"
COLL="${1:?usage: launch-options.sh COLLECTION [add|remove PREFIX]}"; MODE="${2:-list}"; PREFIX="${3:-}"
[[ "$MODE" == list || -n "$PREFIX" ]] || { echo "add/remove need a PREFIX" >&2; exit 2; }
j() { python3 -I -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
cat >"$T/x.js" <<JS
(async () => { const COLL = $(j "$COLL"), MODE = $(j "$MODE"), P = $(j "$PREFIX"), out = [];
  const col = collectionStore.userCollections.find(c => c.displayName === COLL);
  if (!col) return 'no collection ' + COLL;
  for (const a of col.allApps) {
    const d = await new Promise(r => { const h = SteamClient.Apps.RegisterForAppDetails(a.appid, x => { h.unregister(); r(x); }); });
    let o = d.strShortcutLaunchOptions || '';
    if (MODE === 'add' && !o.startsWith(P)) { o = P + o; SteamClient.Apps.SetShortcutLaunchOptions(a.appid, o); }
    if (MODE === 'remove' && o.startsWith(P)) { o = o.slice(P.length); SteamClient.Apps.SetShortcutLaunchOptions(a.appid, o); }
    out.push(a.appid + '  ' + a.display_name + '  |  ' + o);
  }
  return out.join('\n'); })()
JS
sq_steam_js "$T/x.js"
