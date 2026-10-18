// Tiny shared state: is the panel open, is the Claude session running, is everything installed.
type State = { panelOpen: boolean; running: boolean; claudeInstalled: boolean; scriptsInstalled: boolean; busy: boolean };
let state: State = { panelOpen: false, running: false, claudeInstalled: true, scriptsInstalled: true, busy: false };
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
