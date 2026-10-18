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

// Same layout as the Steam Input layout of the "Claude Code" shortcut (steam/controller/make_layout.py),
// except B, which closes the panel here; Esc moves to LT (press LT twice for Claude Code's rewind).
const ESC = "\x1b";
const ARROWS: Record<number, string> = {
  [GamepadButton.DIR_UP]: "\x1b[A", [GamepadButton.DIR_DOWN]: "\x1b[B",
  [GamepadButton.DIR_RIGHT]: "\x1b[C", [GamepadButton.DIR_LEFT]: "\x1b[D",
};
const BUTTON_KEYS: Record<number, string> = {
  [GamepadButton.SECONDARY]: "\x1b[Z",        // X: Shift+Tab (mode)
  [GamepadButton.TRIGGER_LEFT]: ESC,           // LT: Esc
  [GamepadButton.BUMPER_LEFT]: "\x1b[5~",      // LB: Page Up
  [GamepadButton.BUMPER_RIGHT]: "\x1b[6~",     // RB: Page Down
  [GamepadButton.START]: "/",                  // Menu (≡): slash commands
  [GamepadButton.SELECT]: "\t",                // View: Tab
  [GamepadButton.REAR_LEFT_LOWER]: "1",        // back buttons: permission prompt answers
  [GamepadButton.REAR_LEFT_UPPER]: "2",
  [GamepadButton.REAR_RIGHT_LOWER]: "3",
  [GamepadButton.REAR_RIGHT_UPPER]: "\x0f",    // Ctrl+O: transcript
};
// Back buttons: on the Legion Go (SteamOS 3.8, InputPlumber) Steam does not pass them to its own UI, so they
// only work on devices where they arrive as REAR_* buttons. The left stick cannot be told apart from the D-pad
// (same button and source in Steam's events), so both send arrows; scroll with LB/RB or a touch drag.
const REPEATS = new Set<number>([GamepadButton.BUMPER_LEFT, GamepadButton.BUMPER_RIGHT]);
const SPACE_REPEAT_MS = 40; // RT held = Space auto-repeat, like holding the key (Claude Code /voice push-to-talk)

// Last gamepad events, for debugging mappings over CDP: window.__claudeDeckPad
function trace(kind: string, evt: any) {
  const w = window as any;
  const log = (w.__claudeDeckPad ??= []);
  log.push({ kind, button: evt?.detail?.button, source: evt?.detail?.source, repeat: evt?.detail?.is_repeat, t: Date.now() });
  if (log.length > 60) log.shift();
}

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
  const inputBox = useRef<HTMLDivElement>(null);
  const root = useRef<HTMLDivElement>(null);
  const textRef = useRef("");
  textRef.current = text;
  const nativeOk = useRef(false); // lets our own synthetic A through to the text field (opens the keyboard)
  const spaceTimer = useRef<number | null>(null);

  const stopSpace = () => {
    if (spaceTimer.current !== null) { clearInterval(spaceTimer.current); spaceTimer.current = null; }
  };
  useEffect(() => stopSpace, []);

  const inputEl = () => inputBox.current?.querySelector("input") as HTMLInputElement | null;

  // Y: focus the text box and give it an A press, which is how Steam's text fields open the on-screen keyboard.
  const openKeyboard = () => {
    const input = inputEl();
    if (!input) return;
    input.focus();
    nativeOk.current = true;
    try {
      input.dispatchEvent(new CustomEvent("vgp_onok", { bubbles: true, cancelable: true,
        detail: { button: GamepadButton.OK, source: 1, is_repeat: false } }));
    } finally { nativeOk.current = false; }
  };

  // Steam delivers gamepad input as DOM events (vgp_onok, vgp_onoptions, ...) to the focused element, and the
  // text field would handle A itself (open the keyboard). Listening in the capture phase on the panel root runs
  // first, so A always sends and Y always opens the keyboard.
  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const onOk = (e: Event) => {
      if (nativeOk.current) return;
      if (!inputBox.current?.contains(e.target as Node)) return; // terminal / Send: their own A handlers
      e.preventDefault(); e.stopPropagation();
      sendRef.current();
    };
    const onOptions = (e: Event) => {
      e.preventDefault(); e.stopPropagation();
      if (!(e as CustomEvent).detail?.is_repeat) openKeyboard();
    };
    el.addEventListener("vgp_onok", onOk, true);
    el.addEventListener("vgp_onoptions", onOptions, true);
    // Start with the text box focused, ready for Y / typing.
    const t = window.setTimeout(() => inputEl()?.focus(), 250);
    return () => {
      el.removeEventListener("vgp_onok", onOk, true);
      el.removeEventListener("vgp_onoptions", onOptions, true);
      clearTimeout(t);
    };
  }, []);

  const onButtonDown = (evt: any) => {
    trace("down", evt);
    const b = evt?.detail?.button;
    const repeat = !!evt?.detail?.is_repeat;
    if (b === GamepadButton.TRIGGER_RIGHT) {
      if (spaceTimer.current === null) {
        termInput(" ");
        const started = Date.now();
        spaceTimer.current = window.setInterval(() => {
          if (Date.now() - started > 60_000) { stopSpace(); return; } // lost button-up: never repeat forever
          termInput(" ");
        }, SPACE_REPEAT_MS);
      }
    } else if (b in BUTTON_KEYS) {
      if (repeat && !REPEATS.has(b)) return;
      termInput(BUTTON_KEYS[b]);
    } else {
      return; // A, B, directions: handled by their own props / Steam
    }
    evt.preventDefault?.(); evt.stopPropagation?.();
  };

  const onButtonUp = (evt: any) => {
    trace("up", evt);
    if (evt?.detail?.button === GamepadButton.TRIGGER_RIGHT) stopSpace();
  };

  const onDirection = (evt: any) => {
    trace("dir", evt);
    const b = evt?.detail?.button;
    const key = ARROWS[b];
    if (!key) return;
    termInput(key);
    evt.preventDefault?.(); evt.stopPropagation?.();
  };

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
    const t = textRef.current;
    if (!t) { termInput("\r"); return; }
    termInput(t);
    setTimeout(() => termInput("\r"), 30); // Claude Code treats a pasted burst + Enter as one submit
    setText("");
  };
  const sendRef = useRef(send);
  sendRef.current = send;

  // Button mapping sits on the outer Focusable so it also works while the text box or Send has focus.
  return (
    <Focusable ref={root} onButtonDown={onButtonDown} onButtonUp={onButtonUp}
      style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
      <Focusable
        noFocusRing={false}
        onActivate={() => termInput("\r")}
        onGamepadDirection={onDirection}
        onOKActionDescription="Enter"
        onSecondaryActionDescription="Shift+Tab"
        onOptionsActionDescription="Keyboard"
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
        <div ref={inputBox} style={{ flex: 1 }}
             onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); send(); } }}>
          <Focusable preferredFocus onOKActionDescription="Send" onOptionsActionDescription="Keyboard">
            <TextField value={text} onChange={(e) => setText(e.target.value)} />
          </Focusable>
        </div>
        <Focusable onActivate={send} onClick={send}
          style={{ height: 40, padding: "0 16px", borderRadius: 6, background: "#d97757", color: "#1b0f0a",
                   fontWeight: 700, display: "flex", alignItems: "center", cursor: "pointer" }}>
          Send
        </Focusable>
      </div>
    </Focusable>
  );
}
