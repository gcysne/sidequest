// Right-side, full-height panel. Opened as a Steam modal so it gets its own gamepad focus tree
// and native B / Esc handling; CSS turns the centered dialog into a side panel.
import { ModalRoot, showModal } from "@decky/ui";
import { callable } from "@decky/api";
import { useEffect, useState } from "react";
import { DEFAULT_SETTINGS, Settings, getState, setState, subscribe } from "./store";
import { ClaudeTerminal } from "./terminal";

const getSettings = callable<[], Settings>("get_settings");
const CSS_ID = "sidequest-panel-css";
// Steam's gamepad UI keeps a 40px status bar on top and a 42px button-hint footer at the bottom;
// the panel sits between them so neither hides the header or the input row.
const TOP = "40px";
const BOTTOM = "42px";
const css = (width: number) => `
.sidequest-modal { position: fixed !important; top: ${TOP} !important; right: 0 !important; bottom: ${BOTTOM} !important;
  left: auto !important; width: ${width}vw !important; max-width: none !important; height: auto !important;
  max-height: none !important; margin: 0 !important; border-radius: 0 !important; padding: 0 !important;
  background: #1a2029 !important; box-shadow: -12px 0 40px rgba(0,0,0,0.8) !important; display: flex !important;
  flex-direction: column !important; transform: none !important; z-index: 10000 !important; }
.sidequest-modal > div { flex: 1; display: flex; flex-direction: column; padding: 0 !important; margin: 0 !important; max-height: none !important; }
.sidequest-modal .DialogContent, .sidequest-modal .DialogContent_InnerWidth {
  width: 100% !important; max-width: none !important; flex: 1 1 auto !important; height: 100% !important; padding: 0 !important; margin: 0 !important; }
.sidequest-modal form, .sidequest-modal form > div { height: 100%; }
`;

let handle: { Close: () => void } | null = null;

function markClosed() {
  if (!handle) return;
  handle = null;
  setState({ panelOpen: false });
}

function ensureCss(doc: Document, width: number) {
  let s = doc.getElementById(CSS_ID);
  if (!s) {
    s = doc.createElement("style");
    s.id = CSS_ID;
    doc.head.appendChild(s);
  }
  s.textContent = css(width); // overwrite: settings or a reinstalled plugin may change it
}

function PanelBody({ close }: { close: () => void }) {
  const [s, set] = useState(getState());
  useEffect(() => subscribe(() => set(getState())), []);
  useEffect(() => markClosed, []); // unmounted by any route (B, Esc, Steam closing modals)
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", color: "#dcdedf" }}>
      <div style={{ height: 52, display: "flex", alignItems: "center", gap: 12, padding: "0 16px", borderBottom: "1px solid #2f3640" }}>
        <span style={{ color: "#d97757", fontSize: 22, fontWeight: 700 }}>{"✳"}</span>
        <span style={{ fontWeight: 600, fontSize: 17 }}>Claude</span>
        <span style={{ fontSize: 12, padding: "3px 9px", borderRadius: 10, background: s.running ? "#59bf4033" : "#e0484833" }}>
          {s.running ? "session running" : "no session"}
        </span>
        {/* Touch only: B closes the panel, and keeping this out of the gamepad focus tree leaves the terminal
            as the only focus target. */}
        <div onClick={close}
          style={{ marginLeft: "auto", padding: "5px 12px", borderRadius: 5, background: "#ffffff14", cursor: "pointer" }}>
          B  Close
        </div>
      </div>
      <ClaudeTerminal />
    </div>
  );
}

let opening = false;

export async function openClaudePanel() {
  if (handle || opening) return;
  opening = true;
  let settings = DEFAULT_SETTINGS;
  try { settings = await getSettings(); } catch { /* keep defaults */ }
  opening = false;
  if (handle) return;
  setState({ settings });
  const win = (window as any).SteamUIStore?.WindowStore?.GamepadUIMainWindowInstance?.BrowserWindow
    ?? (window as any).SteamUIStore?.WindowStore?.SteamUIWindows?.[0]?.BrowserWindow;
  if (win?.document) ensureCss(win.document, settings.panel_width);
  // Reset our state ourselves: Steam does not always call fnOnClose (e.g. when B/Esc closes it).
  const close = () => { const h = handle; markClosed(); h?.Close(); };
  handle = showModal(
    <ModalRoot modalClassName="sidequest-modal" bAllowFullSize bHideCloseIcon onCancel={close} closeModal={close} onEscKeypress={close}>
      <PanelBody close={close} />
    </ModalRoot>,
    win,
    { fnOnClose: markClosed, bNeverPopOut: true },
  );
  setState({ panelOpen: true });
}

export function closeClaudePanel() { const h = handle; markClosed(); h?.Close(); }
