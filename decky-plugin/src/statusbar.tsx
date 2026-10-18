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

// Steam's status-bar icons share a few (minified, version-specific) classes that carry their size and the
// gamepad focus highlight. Copy whatever classes all focusable neighbours have in common, so the icon is
// highlighted like the others without hard-coding Steam's class names.
function siblingClasses(el: HTMLElement): string[] {
  const sibs = [...(el.parentElement?.children ?? [])].filter(
    (e) => e !== el && e.getAttribute("tabindex") !== null && e.getAttribute("role") !== null,
  ) as HTMLElement[];
  if (!sibs.length) return [];
  let common = [...sibs[0].classList];
  for (const e of sibs.slice(1)) common = common.filter((c) => e.classList.contains(c));
  return common.filter((c) => c !== "Panel" && c !== "Focusable");
}

function ClaudeIcon() {
  const [s, set] = useState(getState());
  const [extra, setExtra] = useState("");
  useEffect(() => subscribe(() => set(getState())), []);
  const ref = (el: HTMLElement | null) => {
    if (!el || extra) return;
    const c = siblingClasses(el).join(" ");
    if (c) setExtra(c);
  };
  if (!s.running) return null;
  return (
    <Focusable
      ref={ref as any}
      className={`claude-deck-icon ${extra}`}
      onActivate={() => openPanel()}
      onClick={() => openPanel()}
      style={{ display: "flex", alignItems: "center", justifyContent: "center",
               color: "#d97757", fontSize: "22px", fontWeight: 700, cursor: "pointer",
               ...(extra ? {} : { height: "100%", padding: "0 8px" }) }}
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
