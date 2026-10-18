# Spike: Claude icon in the Game Mode status bar (2026-10-18)

**Result: works.** Injected live into Steam's gamepad UI (Big Picture in Desktop Mode, same UI as Game Mode),
Steam client on SteamOS 3.8.28. Screenshot: `statusbar-icon.png` (✳ between search and Wi-Fi).

## How
1. Get webpack's require from `window.webpackChunksteamui.push([[Symbol()], {}, r => r])`.
2. Find the one module export that is a `React.memo` whose inner function source contains `quickAccessHeader`.
   That component renders the header status bar for both the main window and the Quick Access Menu
   (prop `quickAccessHeader`). Other stable markers in the same code: `"header gamepad focus"`, `BShowHeader`.
3. Wrap `memo.type`: call the original, then prepend our element to the **last Fragment** inside
   `ret.props.children.props.children` (the right-hand status group). Skip when `props.quickAccessHeader`.
4. Already-mounted header: walk up from `.FlexGrowUniversalSearch` via `__reactFiber*` to the fiber whose
   `type` is the original, set `fiber.type` (+ `alternate.type`) to the wrapper, then bump hook 0
   (`fiber.memoizedState.queue.dispatch(n => n + 1)`), which is Steam's own force-update counter.
   Without this the icon only appears after a remount.

Code used: `statusbar-icon-inject.js` (run in the `SharedJSContext` CEF target, port 8080).

## Risks / to do in the plugin
- Steam updates rename minified symbols: find by source strings only, never by export names; if 0 or >1
  matches, log and fall back to the QAM entry (no icon).
- Structure assumptions (Provider → Mi → [.., Fragment]) checked at runtime; on mismatch, render nothing.
- Gamepad focus: the spike icon is a plain div (touch/mouse only). The plugin must use Steam's focusable
  component (`Focusable` from `@decky/ui`) so the d-pad can reach it.
- Unpatch on plugin unload (restore `memo.type` and live fiber types).
- Must re-verify in real Game Mode (gamescope) and after each Steam client update.
