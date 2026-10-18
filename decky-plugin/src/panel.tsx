// Right-side, full-height panel. Opened as a Steam modal so it gets its own gamepad focus tree
// and native B / Esc handling; CSS turns the centered dialog into a side panel.
import { Focusable, ModalRoot, showModal } from "@decky/ui";
import { useEffect, useState } from "react";
import { getState, setState, subscribe } from "./store";
import { ClaudeTerminal } from "./terminal";

const WIDTH = "58vw"; // TODO: setting
const CSS_ID = "claude-deck-panel-css";
const CSS = `
.claude-deck-modal { position: fixed !important; top: 0 !important; right: 0 !important; bottom: 0 !important;
  left: auto !important; width: ${WIDTH} !important; max-width: none !important; height: 100vh !important;
  max-height: none !important; margin: 0 !important; border-radius: 0 !important; padding: 0 !important;
  background: #1a2029 !important; box-shadow: -12px 0 40px rgba(0,0,0,0.8) !important; display: flex !important;
  flex-direction: column !important; transform: none !important; z-index: 10000 !important; }
.claude-deck-modal > div { flex: 1; display: flex; flex-direction: column; padding: 0 !important; margin: 0 !important; max-height: none !important; }
`;

let handle: { Close: () => void } | null = null;

function ensureCss(doc: Document) {
  if (doc.getElementById(CSS_ID)) return;
  const s = doc.createElement("style");
  s.id = CSS_ID;
  s.textContent = CSS;
  doc.head.appendChild(s);
}

function PanelBody({ close }: { close: () => void }) {
  const [s, set] = useState(getState());
  useEffect(() => subscribe(() => set(getState())), []);
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", color: "#dcdedf" }}>
      <div style={{ height: 52, display: "flex", alignItems: "center", gap: 12, padding: "0 16px", borderBottom: "1px solid #2f3640" }}>
        <span style={{ color: "#d97757", fontSize: 22, fontWeight: 700 }}>{"✳"}</span>
        <span style={{ fontWeight: 600, fontSize: 17 }}>Claude</span>
        <span style={{ fontSize: 12, padding: "3px 9px", borderRadius: 10, background: s.running ? "#59bf4033" : "#e0484833" }}>
          {s.running ? "session running" : "no session"}
        </span>
        <Focusable preferredFocus onActivate={close} onClick={close} onCancelButton={close}
          style={{ marginLeft: "auto", padding: "5px 12px", borderRadius: 5, background: "#ffffff14", cursor: "pointer" }}>
          B  Close
        </Focusable>
      </div>
      <ClaudeTerminal />
    </div>
  );
}

export function openClaudePanel() {
  if (handle) return;
  const win = (window as any).SteamUIStore?.WindowStore?.GamepadUIMainWindowInstance?.BrowserWindow
    ?? (window as any).SteamUIStore?.WindowStore?.SteamUIWindows?.[0]?.BrowserWindow;
  if (win?.document) ensureCss(win.document);
  const close = () => { handle?.Close(); };
  handle = showModal(
    <ModalRoot modalClassName="claude-deck-modal" bAllowFullSize bHideCloseIcon onCancel={close} closeModal={close} onEscKeypress={close}>
      <PanelBody close={close} />
    </ModalRoot>,
    win,
    { fnOnClose: () => { handle = null; setState({ panelOpen: false }); }, bNeverPopOut: true },
  );
  setState({ panelOpen: true });
}

export function closeClaudePanel() { handle?.Close(); }
