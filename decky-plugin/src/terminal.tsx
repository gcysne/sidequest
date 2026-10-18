// Live view of the Claude tmux session inside the panel (xterm.js + backend pty bridge).
import { Focusable, GamepadButton, TextField } from "@decky/ui";
import { addEventListener, callable, removeEventListener } from "@decky/api";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { useEffect, useRef, useState } from "react";
import xtermCss from "./xterm-css";

const termOpen = callable<[number, number], { ok: boolean; error?: string }>("term_open");
const termInput = callable<[string], void>("term_input");
const termResize = callable<[number, number], void>("term_resize");
const termClose = callable<[], void>("term_close");

const KEYS: Record<number, string> = {
  [GamepadButton.DIR_UP]: "\x1b[A", [GamepadButton.DIR_DOWN]: "\x1b[B",
  [GamepadButton.DIR_RIGHT]: "\x1b[C", [GamepadButton.DIR_LEFT]: "\x1b[D",
};

function injectCss(doc: Document) {
  if (doc.getElementById("claude-deck-xterm-css")) return;
  const s = doc.createElement("style");
  s.id = "claude-deck-xterm-css";
  s.textContent = xtermCss;
  doc.head.appendChild(s);
}

function b64ToBytes(b64: string) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

export function ClaudeTerminal() {
  const host = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [text, setText] = useState("");

  useEffect(() => {
    const el = host.current;
    if (!el) return;
    injectCss(el.ownerDocument);
    const term = new Terminal({
      fontFamily: '"DejaVu Sans Mono", "Noto Sans Mono", monospace', fontSize: 15, cursorBlink: true,
      scrollback: 5000, allowProposedApi: false,
      theme: { background: "#101215", foreground: "#dcdedf", cursor: "#d97757", selectionBackground: "#d9775755" },
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(el);
    termRef.current = term;
    fit.fit();

    const onOutput = (b64: string) => term.write(b64ToBytes(b64));
    const onExit = () => setError("Session detached or ended.");
    addEventListener<[string]>("term_output", onOutput);
    addEventListener("term_exit", onExit);
    const dataSub = term.onData((d) => { termInput(d); });

    termOpen(term.cols, term.rows).then((r) => { if (!r.ok) setError(r.error ?? "could not attach"); });

    const ro = new ResizeObserver(() => {
      const before = `${term.cols}x${term.rows}`;
      fit.fit();
      if (`${term.cols}x${term.rows}` !== before) termResize(term.cols, term.rows);
    });
    ro.observe(el);

    return () => {
      ro.disconnect();
      dataSub.dispose();
      removeEventListener("term_output", onOutput);
      removeEventListener("term_exit", onExit);
      termClose();
      term.dispose();
      termRef.current = null;
    };
  }, []);

  const send = () => {
    if (!text) { termInput("\r"); return; }
    termInput(text);
    setTimeout(() => termInput("\r"), 30); // Claude Code treats a pasted burst + Enter as one submit
    setText("");
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
      <Focusable
        noFocusRing={false}
        onActivate={() => termInput("\r")}
        onSecondaryButton={() => termInput("\x1b")}
        onGamepadDirection={(evt: any) => {
          const key = KEYS[evt?.detail?.button];
          if (key) { termInput(key); evt.preventDefault?.(); evt.stopPropagation?.(); }
        }}
        onOKActionDescription="Enter"
        onSecondaryActionDescription="Esc"
        style={{ flex: 1, minHeight: 0, margin: "10px 12px 0", borderRadius: 6, background: "#101215",
                 padding: "8px 10px", border: "1px solid #ffffff14", position: "relative" }}
      >
        <div ref={host} style={{ width: "100%", height: "100%" }} />
        {error && (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
                        background: "#101215e0", color: "#f0a07f" }}>{error}</div>
        )}
      </Focusable>
      <div style={{ display: "flex", gap: 10, alignItems: "center", padding: "10px 12px" }}>
        <div style={{ flex: 1 }}
             onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); send(); } }}>
          <TextField value={text} onChange={(e) => setText(e.target.value)} />
        </div>
        <Focusable onActivate={send} onClick={send}
          style={{ height: 40, padding: "0 16px", borderRadius: 6, background: "#d97757", color: "#1b0f0a",
                   fontWeight: 700, display: "flex", alignItems: "center", cursor: "pointer" }}>
          Send
        </Focusable>
      </div>
    </div>
  );
}
