import { ButtonItem, Navigation, PanelSection, PanelSectionRow, staticClasses } from "@decky/ui";
import { callable, definePlugin } from "@decky/api";
import { useEffect, useState } from "react";
import { closeClaudePanel, openClaudePanel } from "./panel";
import { patchStatusBar, unpatchStatusBar } from "./statusbar";
import { getState, openPanel, setOpener, setState, subscribe } from "./store";

const sessionStatus = callable<[], { running: boolean }>("session_status");
const POLL_MS = 5000;

function QamContent({ iconOk }: { iconOk: boolean }) {
  const [s, set] = useState(getState());
  useEffect(() => subscribe(() => set(getState())), []);
  return (
    <PanelSection>
      <PanelSectionRow>
        <div>{s.running ? "Session running" : "No Claude session running"}</div>
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem layout="below" onClick={() => { Navigation.CloseSideMenus(); setTimeout(() => openPanel(), 300); }}>
          Open Claude panel
        </ButtonItem>
      </PanelSectionRow>
      <PanelSectionRow>
        <div style={{ fontSize: 12, color: "#8b929a" }}>
          Status-bar icon: {iconOk ? "active" : "unavailable on this Steam version"}
        </div>
      </PanelSectionRow>
    </PanelSection>
  );
}

export default definePlugin(() => {
  const poll = () => sessionStatus().then((r) => setState({ running: r.running })).catch(() => setState({ running: false }));
  poll();
  const timer = setInterval(poll, POLL_MS);
  setOpener(openClaudePanel);
  let iconOk = false;
  try { iconOk = patchStatusBar(); } catch (e) { console.error("[claude-deck] patch failed", e); }

  return {
    name: "Claude Deck",
    titleView: <div className={staticClasses.Title}>Claude Deck</div>,
    content: <QamContent iconOk={iconOk} />,
    icon: <span style={{ fontWeight: 700 }}>{"✳"}</span>,
    onDismount() {
      clearInterval(timer);
      closeClaudePanel();
      unpatchStatusBar();
    },
  };
});
