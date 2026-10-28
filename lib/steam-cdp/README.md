# steam-cdp: Steam's client API from scripts

Steam's UI is a Chromium (CEF) app. With remote debugging on (`127.0.0.1:8080`, enabled by Decky Loader), scripts
can run JavaScript in its `SharedJSContext` and call the same client API the UI uses (`SteamClient.Apps.*`,
`appStore`, `collectionStore`): add shortcuts, set artwork and launch options, read controller mappings, restart
Steam. Changes apply live, without restarting Steam.

- `cdp.mjs TARGET FILE.js`: evaluate FILE.js in the CEF target (e.g. `SharedJSContext`), print the awaited result.
- `corsserve.py DIR PORT`: serve a folder to the Steam JS context (used to upload artwork files).
- `node.sh`: find a usable Node.js.

These are internal Steam APIs: a Steam update can rename them. Test after Steam updates (post-update-check skill).
