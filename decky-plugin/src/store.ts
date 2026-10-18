// Tiny shared state: is the panel open, is the Claude session running.
type State = { panelOpen: boolean; running: boolean };
let state: State = { panelOpen: false, running: false };
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
