// Tiny shared state: is the panel open, is the Claude session running, is everything installed.
// Panel settings come from ~/.config/claude-deck/config (PANEL_WIDTH, PANEL_FONT_SIZE), read on every open.
export type Settings = { panel_width: number; font_size: number };
export const DEFAULT_SETTINGS: Settings = { panel_width: 70, font_size: 15 };
type State = { panelOpen: boolean; running: boolean; claudeInstalled: boolean; scriptsInstalled: boolean; busy: boolean;
               settings: Settings };
let state: State = { panelOpen: false, running: false, claudeInstalled: true, scriptsInstalled: true, busy: false,
                     settings: DEFAULT_SETTINGS };
const subs = new Set<() => void>();

export const getState = () => state;
export function setState(patch: Partial<State>) {
  state = { ...state, ...patch };
  subs.forEach((f) => f());
}
export function subscribe(f: () => void) {
  subs.add(f);
  return () => { subs.delete(f); };
}
export let openPanel = () => {};
export function setOpener(f: () => void) { openPanel = f; }
