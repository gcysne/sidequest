// Adds the Claude icon to Steam's Game Mode status bar (see docs/spikes/statusbar-icon.md).
// Steam has no API for this: we wrap the header component, found by stable strings in its source.
// Any mismatch => log and do nothing (the Quick Access Menu entry still works).
import { Focusable } from "@decky/ui";
import { useEffect, useState } from "react";
import { getState, openPanel, subscribe } from "./store";

const MARKER = "quickAccessHeader";
const TAG = "[claude-deck]";

type Memo = { $$typeof: symbol; type: (props: any) => any };
let patched: { memo: Memo; orig: (props: any) => any; wrapper: (props: any) => any } | null = null;

function ClaudeIcon() {
  const [s, set] = useState(getState());
  useEffect(() => subscribe(() => set(getState())), []);
  if (!s.running) return null;
  return (
    <Focusable
      className="claude-deck-icon"
      onActivate={() => openPanel()}
      onClick={() => openPanel()}
      style={{ display: "flex", alignItems: "center", height: "100%", padding: "0 8px",
               color: "#d97757", fontSize: "22px", fontWeight: 700, cursor: "pointer" }}
    >
      {"✳"}
    </Focusable>
  );
}

function findHeaderMemo(): Memo | null {
  let req: any;
  (window as any).webpackChunksteamui.push([[Symbol("claude-deck")], {}, (r: any) => { req = r; }]);
  const hits: Memo[] = [];
  for (const id of Object.keys(req.m)) {
    let mod: any;
    try { mod = req(id); } catch { continue; }
    if (!mod || typeof mod !== "object") continue;
    for (const k of Object.keys(mod)) {
      let v: any;
      try { v = mod[k]; } catch { continue; }
      if (v?.$$typeof === Symbol.for("react.memo") && typeof v.type === "function" &&
          v.type.toString().includes(MARKER)) hits.push(v);
    }
  }
  if (hits.length !== 1) { console.warn(TAG, `header component matches: ${hits.length}, icon disabled`); return null; }
  return hits[0];
}

// Header fibers already on screen: swap their type and bump Steam's force-update counter (hook 0).
function swapLiveFibers(from: any, to: any) {
  const React = (window as any).SP_REACT;
  for (const w of (window as any).SteamUIStore?.WindowStore?.SteamUIWindows ?? []) {
    const doc: Document | undefined = (w.m_BrowserWindow || w.BrowserWindow)?.document;
    const host = doc?.querySelector(".FlexGrowUniversalSearch") as any;
    if (!host) continue;
    let f = host[Object.keys(host).find((k) => k.startsWith("__reactFiber")) ?? ""];
    while (f && f.type !== from) f = f.return;
    if (!f) continue;
    f.type = to;
    if (f.alternate) f.alternate.type = to;
    const q = f.memoizedState?.queue;
    if (typeof q?.dispatch === "function" && typeof f.memoizedState.memoizedState === "number") q.dispatch((n: number) => n + 1);
  }
  void React;
}

export function patchStatusBar(): boolean {
  const React = (window as any).SP_REACT;
  const memo = findHeaderMemo();
  if (!memo || !React) return false;
  const orig = memo.type;
  const wrapper = function (this: any, props: any) {
    const ret = orig.call(this, props);
    try {
      if (!props?.quickAccessHeader) {
        const arr = ret?.props?.children?.props?.children;
        if (Array.isArray(arr)) {
          const grp = [...arr].reverse().find((x: any) => x?.type === React.Fragment && Array.isArray(x.props?.children));
          if (grp) grp.props.children = [<ClaudeIcon key="claude-deck-icon" />, ...grp.props.children];
        }
      }
    } catch (e) { console.error(TAG, "status bar inject failed", e); }
    return ret;
  };
  memo.type = wrapper;
  patched = { memo, orig, wrapper };
  swapLiveFibers(orig, wrapper);
  return true;
}

export function unpatchStatusBar() {
  if (!patched) return;
  patched.memo.type = patched.orig;
  swapLiveFibers(patched.wrapper, patched.orig);
  patched = null;
}
