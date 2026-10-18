// Full-height panel on the right side of the screen, rendered as a Decky global component.
import { Focusable } from "@decky/ui";
import { useEffect, useState } from "react";
import { closePanel, getState, subscribe } from "./store";

const WIDTH = "58%"; // TODO: setting

export function ClaudePanel() {
  const [s, set] = useState(getState());
  useEffect(() => subscribe(() => set(getState())), []);
  if (!s.panelOpen) return null;
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 7000 }}>
      <div onClick={closePanel} style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.6)" }} />
      <Focusable
        onCancel={closePanel}
        onCancelButton={closePanel}
        style={{ position: "absolute", top: 0, right: 0, bottom: 0, width: WIDTH, background: "#1a2029",
                 boxShadow: "-12px 0 40px rgba(0,0,0,0.8)", display: "flex", flexDirection: "column", color: "#dcdedf" }}
      >
        <div style={{ height: 52, display: "flex", alignItems: "center", gap: 12, padding: "0 16px", borderBottom: "1px solid #2f3640" }}>
          <span style={{ color: "#d97757", fontSize: 22, fontWeight: 700 }}>{"✳"}</span>
          <span style={{ fontWeight: 600, fontSize: 17 }}>Claude</span>
          <span style={{ fontSize: 12, padding: "3px 9px", borderRadius: 10, background: s.running ? "#59bf4033" : "#e0484833" }}>
            {s.running ? "session running" : "no session"}
          </span>
          <Focusable onActivate={closePanel} onClick={closePanel}
            style={{ marginLeft: "auto", padding: "5px 12px", borderRadius: 5, background: "#ffffff14", cursor: "pointer" }}>
            B  Close
          </Focusable>
        </div>
        <div style={{ flex: 1, margin: 12, borderRadius: 6, background: "#101215", display: "flex",
                      alignItems: "center", justifyContent: "center", color: "#8b929a" }}>
          Terminal goes here (next step)
        </div>
      </Focusable>
    </div>
  );
}
