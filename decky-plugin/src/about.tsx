// Full-screen "About" page (cog button in the plugin's title bar), with About / Controls / Credits tabs.
import { DialogButton, Focusable, Navigation, SidebarNavigation, staticClasses } from "@decky/ui";
import { callable } from "@decky/api";
import { useEffect, useState } from "react";

export const ABOUT_ROUTE = "/sidequest/about";
const REPO = "https://github.com/gcysne/sidequest";
const pluginInfo = callable<[], { version: string }>("plugin_info");

function openUrl(url: string) {
  Navigation.NavigateToExternalWeb(url);
}

export function openAbout() {
  Navigation.CloseSideMenus();
  Navigation.Navigate(ABOUT_ROUTE);
}

const cogIcon = (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
    <path d="M19.14 12.94a7.07 7.07 0 0 0 .06-.94 7.07 7.07 0 0 0-.06-.94l2.03-1.58a.49.49 0 0 0 .12-.62l-1.92-3.32a.49.49 0 0 0-.59-.22l-2.39.96a7.03 7.03 0 0 0-1.62-.94l-.36-2.54a.48.48 0 0 0-.48-.4h-3.84a.48.48 0 0 0-.48.4l-.36 2.54c-.59.24-1.13.56-1.62.94l-2.39-.96a.48.48 0 0 0-.59.22L2.74 8.87a.48.48 0 0 0 .12.62l2.03 1.58a7.4 7.4 0 0 0 0 1.88l-2.03 1.58a.49.49 0 0 0-.12.62l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.49.38 1.03.7 1.62.94l.36 2.54c.05.24.25.4.48.4h3.84c.24 0 .44-.16.48-.4l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.49.49 0 0 0-.12-.62l-2.03-1.58zM12 15.6a3.6 3.6 0 1 1 0-7.2 3.6 3.6 0 0 1 0 7.2z" />
  </svg>
);

// Title bar of the Quick Access entry: name on the left, cog on the right (like CSS Loader).
export function TitleView() {
  return (
    <Focusable className={staticClasses.Title}
      style={{ display: "flex", alignItems: "center", width: "100%", padding: 0, boxShadow: "none" }}>
      <div style={{ marginRight: "auto" }}>Sidequest</div>
      <DialogButton style={{ height: 28, width: 40, minWidth: 0, padding: "6px 12px", display: "flex",
        alignItems: "center", justifyContent: "center" }} onClick={openAbout}>
        {cogIcon}
      </DialogButton>
    </Focusable>
  );
}

const h2 = { fontWeight: "bold", fontSize: "1.4em", margin: "18px 0 6px" } as const;
const muted = { color: "#8b929a" } as const;
const linkRow = { display: "flex", gap: 10, flexWrap: "wrap", marginTop: 14 } as const;
const btn = { width: "auto", minWidth: 0, padding: "8px 16px" } as const;

function AboutPage() {
  const [version, setVersion] = useState("");
  useEffect(() => { pluginInfo().then((r) => setVersion(r.version)).catch(() => {}); }, []);
  return (
    <div>
      <div style={{ fontSize: "1.8em", fontWeight: "bold" }}>✳ Sidequest</div>
      <div style={{ fontSize: "1.1em" }}>for Claude Code</div>
      <div style={muted}>{version ? `Version ${version}` : "Alpha"}</div>
      <p>
        Claude Code on SteamOS handhelds, in Game Mode. One persistent Claude Code session that you open as a side
        panel from Steam's status bar, drive with the controller and the touchscreen, and also reach from Desktop
        Mode and your phone.
      </p>
      <Focusable style={linkRow}>
        <DialogButton style={btn} onClick={() => openUrl(REPO)}>Project page</DialogButton>
        <DialogButton style={btn} onClick={() => openUrl(`${REPO}/blob/main/docs/usage.md`)}>User guide</DialogButton>
        <DialogButton style={btn} onClick={() => openUrl(`${REPO}/issues`)}>Report a problem</DialogButton>
      </Focusable>
      <div style={h2}>License</div>
      <div>Open source under the MIT License.</div>
      <div style={h2}>Disclaimer</div>
      <div style={muted}>
        Sidequest is a community project. It is not affiliated with or endorsed by Anthropic or Valve. "Claude"
        and "Claude Code" are trademarks of Anthropic. Using Claude Code requires a Claude account and is subject to
        Anthropic's terms.
      </div>
    </div>
  );
}

const CONTROLS: [string, string][] = [
  ["A", "Enter: send, confirm a choice"],
  ["B", "Close the panel (Claude keeps running)"],
  ["X", "Shift+Tab: switch Claude's mode"],
  ["Y", "Steam keyboard, typing straight into Claude's prompt"],
  ["D-pad / left stick", "Arrow keys: menus, prompts, history, cursor"],
  ["LT", "Esc: interrupt Claude; twice on an empty prompt = rewind"],
  ["RT (hold)", "Space, held: push-to-talk in /voice hold mode"],
  ["LB / RB", "Page Up / Page Down"],
  ["Menu (☰)", "/ : start a slash command"],
  ["View (⧉)", "Tab: autocomplete"],
  ["Touchscreen", "Drag to scroll, tap to click"],
];

function ControlsPage() {
  return (
    <div>
      <div style={{ ...h2, marginTop: 0 }}>In the Claude panel</div>
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <tbody>
          {CONTROLS.map(([k, v]) => (
            <tr key={k} style={{ borderBottom: "1px solid #ffffff1a" }}>
              <td style={{ padding: "6px 16px 6px 0", fontWeight: "bold", whiteSpace: "nowrap" }}>{k}</td>
              <td style={{ padding: "6px 0" }}>{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p style={muted}>
        Open the panel with the ✳ icon in the status bar or from Quick Access &gt; Sidequest. In Desktop Mode,
        run <code>claude-session</code> in a terminal to join the same session.
      </p>
    </div>
  );
}

function CreditsPage() {
  return (
    <div>
      <div style={{ ...h2, marginTop: 0 }}>Creator</div>
      <div style={{ fontSize: "1.2em", fontWeight: "bold" }}>gcysne</div>
      <div>
        Idealizer and lead of the project: had the idea, sets its direction and design, and tests every build on
        real hardware. Main contributor.
      </div>
      <Focusable style={linkRow}>
        <DialogButton style={btn} onClick={() => openUrl("https://github.com/gcysne")}>github.com/gcysne</DialogButton>
      </Focusable>
      <div style={h2}>Code</div>
      <div>Written by Claude (Anthropic's Claude Code), working with gcysne.</div>
      <div style={h2}>Contributors</div>
      <div>Everyone who reports problems, tests on new devices and sends improvements.</div>
      <Focusable style={linkRow}>
        <DialogButton style={btn} onClick={() => openUrl(`${REPO}/graphs/contributors`)}>All contributors</DialogButton>
      </Focusable>
      <div style={h2}>Built with</div>
      <div style={muted}>Decky Loader · xterm.js · tmux · Piper (optional voice)</div>
    </div>
  );
}

export function AboutRouter() {
  return (
    <SidebarNavigation title="Sidequest" showTitle pages={[
      { title: "About", content: <AboutPage /> },
      { title: "Controls", content: <ControlsPage /> },
      { title: "Credits", content: <CreditsPage /> },
    ]} />
  );
}
