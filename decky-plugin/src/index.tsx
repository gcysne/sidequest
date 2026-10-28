import { ButtonItem, ConfirmModal, Navigation, PanelSection, PanelSectionRow, showModal } from "@decky/ui";
import { addEventListener, callable, definePlugin, removeEventListener, routerHook, toaster } from "@decky/api";
import { ABOUT_ROUTE, AboutRouter, TitleView } from "./about";
import { useEffect, useState } from "react";
import { closeClaudePanel, openClaudePanel } from "./panel";
import { patchStatusBar, unpatchStatusBar } from "./statusbar";
import { getState, openPanel, setOpener, setState, subscribe } from "./store";

type Status = { running: boolean; claude_installed: boolean; scripts_installed: boolean };
type Result = { ok: boolean; error?: string };
const sessionStatus = callable<[], Status>("session_status");
const sessionStart = callable<[boolean], Result>("session_start");
const sessionNew = callable<[], Result>("session_new");
const sessionStop = callable<[], Result>("session_stop");
const POLL_MS = 5000;

async function poll() {
  try {
    const r = await sessionStatus();
    setState({ running: r.running, claudeInstalled: r.claude_installed, scriptsInstalled: r.scripts_installed });
  } catch {
    setState({ running: false });
  }
}

async function run(action: () => Promise<Result>, then?: () => void) {
  setState({ busy: true });
  try {
    const r = await action();
    if (!r.ok) toaster.toast({ title: "Sidequest", body: r.error ?? "Failed" });
    await poll();
    if (r.ok) then?.();
  } finally {
    setState({ busy: false });
  }
}

function openFromQam() {
  Navigation.CloseSideMenus();
  setTimeout(() => openPanel(), 300);
}

const start = (fresh: boolean) => run(() => sessionStart(fresh), openFromQam);

function confirm(title: string, text: string, ok: string, action: () => void) {
  showModal(<ConfirmModal strTitle={title} strDescription={text} strOKButtonText={ok} onOK={action} />);
}

function QamContent({ iconOk }: { iconOk: boolean }) {
  const [s, set] = useState(getState());
  useEffect(() => subscribe(() => set(getState())), []);
  if (!s.scriptsInstalled || !s.claudeInstalled) {
    return (
      <PanelSection>
        <PanelSectionRow>
          <div>
            {!s.scriptsInstalled ? "Sidequest isn't fully installed." : "Claude Code isn't installed."} In Desktop
            Mode, run <code>install.sh</code> from the Sidequest folder.
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }
  return (
    <PanelSection>
      <PanelSectionRow>
        <div>{s.running ? "Session running" : "No Claude session running"}</div>
      </PanelSectionRow>
      {s.running ? (
        <>
          <PanelSectionRow>
            <ButtonItem layout="below" disabled={s.busy} onClick={openFromQam}>Open Claude panel</ButtonItem>
          </PanelSectionRow>
          <PanelSectionRow>
            <ButtonItem layout="below" disabled={s.busy} onClick={() => confirm(
              "Start a new conversation?",
              "Claude restarts with an empty conversation. Anything it's doing now is interrupted. The current " +
              "conversation is kept and can be reopened with /resume.",
              "New conversation", () => run(sessionNew, openFromQam))}>
              New conversation
            </ButtonItem>
          </PanelSectionRow>
          <PanelSectionRow>
            <ButtonItem layout="below" disabled={s.busy} onClick={() => confirm(
              "Stop the Claude session?",
              "Claude Code exits. Anything it's doing now is interrupted. Start it again here at any time; it " +
              "continues the last conversation.",
              "Stop", () => run(sessionStop))}>
              Stop session
            </ButtonItem>
          </PanelSectionRow>
        </>
      ) : (
        <>
          <PanelSectionRow>
            <ButtonItem layout="below" disabled={s.busy} onClick={() => start(false)}>
              Start Claude (continue last conversation)
            </ButtonItem>
          </PanelSectionRow>
          <PanelSectionRow>
            <ButtonItem layout="below" disabled={s.busy} onClick={() => start(true)}>Start a new conversation</ButtonItem>
          </PanelSectionRow>
        </>
      )}
      <PanelSectionRow>
        <div style={{ fontSize: 12, color: "#8b929a" }}>
          Status-bar icon: {iconOk ? "shown while a session runs" : "unavailable on this Steam version"}
        </div>
      </PanelSectionRow>
    </PanelSection>
  );
}

// Links Claude opens (login, docs) arrive from the backend and open in Steam's built-in browser.
// The login callback goes to http://localhost:<port>, which Steam's browser reaches because it runs on this device.
function onOpenUrl(url: string) {
  closeClaudePanel();
  setTimeout(() => Navigation.NavigateToExternalWeb(url), 200);
}

function onToast(t: { title?: string; body?: string; critical?: boolean }) {
  toaster.toast({ title: t.title ?? "Claude", body: t.body ?? "", critical: !!t.critical });
}

export default definePlugin(() => {
  poll();
  const timer = setInterval(poll, POLL_MS);
  setOpener(openClaudePanel);
  addEventListener<[string]>("open_url", onOpenUrl);
  addEventListener<[any]>("toast", onToast);
  routerHook.addRoute(ABOUT_ROUTE, () => <AboutRouter />, { exact: true });
  let iconOk = false;
  try { iconOk = patchStatusBar(); } catch (e) { console.error("[sidequest] patch failed", e); }

  return {
    name: "Sidequest",
    titleView: <TitleView />,
    content: <QamContent iconOk={iconOk} />,
    icon: <span style={{ fontWeight: 700 }}>{"✳"}</span>,
    onDismount() {
      clearInterval(timer);
      removeEventListener("open_url", onOpenUrl);
      removeEventListener("toast", onToast);
      closeClaudePanel();
      unpatchStatusBar();
      routerHook.removeRoute(ABOUT_ROUTE);
    },
  };
});
