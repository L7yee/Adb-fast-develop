# ADB Dashboard

The current application is in `electron/`. The Python/PyQt implementation is preserved in `legacy-python/` as a separate historical version. New application work should use Electron; do not add a Python dependency to the current app.

## Development

- Run commands from `electron/`: `npm ci`, `npm start`, `npm test`, `npm run dist`.
- ADB must be available on the host `PATH` for device features.
- `electron/main.js`: window lifecycle and IPC handlers.
- `electron/preload.js`: narrow, context isolated renderer API.
- `electron/adb.js`: device detection and process execution. Use `spawn` with an argument list, never a host shell.
- `electron/config.js`: YAML command migration, validation, and persistence in Electron user data.
- `electron/renderer/`: UI. Keep untrusted command output as text, not HTML.
- `electron/config/commands.yaml`: bundled default commands; do not write to it at runtime.
- `electron/tests/`: Node core tests and a manual Electron UI smoke check.

Commands run once per click (`read` or `action`). Keep kernel and Logcat snapshots in the Logs workspace, with separate persisted save paths. Preserve the remaining user workflows and verify changes with a relevant test or a running app check.
