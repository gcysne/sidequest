// Live view of the Claude tmux session inside the panel (xterm.js + backend pty bridge).
import { Focusable, GamepadButton } from "@decky/ui";
import { addEventListener, callable, removeEventListener } from "@decky/api";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { useEffect, useRef, useState } from "react";
import { getState } from "./store";
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

// Steam's on-screen keyboard belongs to the window that shows the panel.
function keyboardManager(doc: Document): any {
  const store = (window as any).SteamUIStore?.WindowStore;
  const wins: any[] = [...(store?.SteamUIWindows ?? [])];
  const inst = wins.find((w) => (w.m_BrowserWindow ?? w.BrowserWindow)?.document === doc) ?? store?.GamepadUIMainWindowInstance;
  return inst?.VirtualKeyboardManager ?? inst?.m_VirtualKeyboardManager;
}

export function ClaudeTerminal() {
  const host = useRef<HTMLDivElement>(null);
  const root = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const [error, setError] = useState<string | null>(null);
  const spaceTimer = useRef<number | null>(null);

  const stopSpace = () => {
    if (spaceTimer.current !== null) { clearInterval(spaceTimer.current); spaceTimer.current = null; }
  };
  useEffect(() => stopSpace, []);

  // Y: Steam's keyboard types into xterm's hidden textarea, so text goes straight into Claude Code's prompt
  // (one place to type, dictate and edit). Verified on the Legion Go, 2026-10-18.
  const openKeyboard = () => {
    const ta = termRef.current?.textarea;
    if (!ta) return;
    ta.focus();
    try { keyboardManager(ta.ownerDocument)?.CreateVirtualKeyboardRef({})?.ShowVirtualKeyboard(); }
    catch (e) { console.warn("claude-deck: could not open the keyboard", e); }
  };

  // Steam delivers gamepad input as DOM events (vgp_onoptions, ...); catch Y in the capture phase so nothing
  // else in the panel handles it first.
  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const onOptions = (e: Event) => {
      e.preventDefault(); e.stopPropagation();
      if (!(e as CustomEvent).detail?.is_repeat) openKeyboard();
    };
    el.addEventListener("vgp_onoptions", onOptions, true);
    return () => el.removeEventListener("vgp_onoptions", onOptions, true);
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
      return; // A, B, Y, directions: handled elsewhere
    }
    evt.preventDefault?.(); evt.stopPropagation?.();
  };

  const onButtonUp = (evt: any) => {
    trace("up", evt);
    if (evt?.detail?.button === GamepadButton.TRIGGER_RIGHT) stopSpace();
  };

  // The D-pad always sends arrows; consuming the event keeps gamepad focus on the terminal.
  const onDirection = (evt: any) => {
    trace("dir", evt);
    const key = ARROWS[evt?.detail?.button];
    if (!key) return;
    termInput(key);
    evt.preventDefault?.(); evt.stopPropagation?.();
  };

  useEffect(() => {
    const el = host.current;
    if (!el) return;
    injectCss(el.ownerDocument);
    const term = new Terminal({
      fontFamily: '"DejaVu Sans Mono", "Noto Sans Mono", monospace', fontSize: getState().settings.font_size, cursorBlink: true,
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

    // Touch drag scrolls: every row the finger moves becomes one SGR mouse-wheel event at the finger's cell.
    // tmux (mouse on) hands it to Claude Code's full-screen view or scrolls its own history, like the
    // touch-scroll bindings of the Claude Code shortcut. Finger down = content follows = wheel up.
    let lastY: number | null = null;
    const cellOf = (t: Touch) => {
      const r = el.getBoundingClientRect();
      const col = Math.min(term.cols, Math.max(1, Math.floor(((t.clientX - r.left) / r.width) * term.cols) + 1));
      const row = Math.min(term.rows, Math.max(1, Math.floor(((t.clientY - r.top) / r.height) * term.rows) + 1));
      return { col, row, rowPx: r.height / term.rows };
    };
    const onTouchStart = (e: TouchEvent) => { lastY = e.touches.length === 1 ? e.touches[0].clientY : null; };
    const onTouchMove = (e: TouchEvent) => {
      if (lastY === null || e.touches.length !== 1) return;
      const t = e.touches[0];
      const { col, row, rowPx } = cellOf(t);
      const steps = Math.trunc((t.clientY - lastY) / rowPx);
      if (steps === 0) return;
      e.preventDefault();
      const code = steps > 0 ? 64 : 65;
      termInput(`\x1b[<${code};${col};${row}M`.repeat(Math.min(Math.abs(steps), 10)));
      lastY += steps * rowPx;
    };
    const onTouchEnd = () => { lastY = null; };
    el.addEventListener("touchstart", onTouchStart, { passive: true });
    el.addEventListener("touchmove", onTouchMove, { passive: false });
    el.addEventListener("touchend", onTouchEnd);
    el.addEventListener("touchcancel", onTouchEnd);

    return () => {
      ro.disconnect();
      dataSub.dispose();
      el.removeEventListener("touchstart", onTouchStart);
      el.removeEventListener("touchmove", onTouchMove);
      el.removeEventListener("touchend", onTouchEnd);
      el.removeEventListener("touchcancel", onTouchEnd);
      removeEventListener("term_output", onOutput);
      removeEventListener("term_exit", onExit);
      termClose();
      term.dispose();
      termRef.current = null;
    };
  }, []);

  return (
    <Focusable ref={root} onButtonDown={onButtonDown} onButtonUp={onButtonUp}
      style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
      <Focusable
        preferredFocus
        noFocusRing={false}
        onActivate={() => termInput("\r")}
        onGamepadDirection={onDirection}
        onOKActionDescription="Enter"
        onSecondaryActionDescription="Shift+Tab"
        onOptionsActionDescription="Keyboard"
        style={{ flex: 1, minHeight: 0, margin: "10px 12px 12px", borderRadius: 6, background: "#101215",
                 padding: "8px 10px", border: "1px solid #ffffff14", position: "relative" }}
      >
        <div ref={host} style={{ width: "100%", height: "100%", touchAction: "none" }} />
        {error && (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
                        background: "#101215e0", color: "#f0a07f" }}>{error}</div>
        )}
      </Focusable>
    </Focusable>
  );
}
