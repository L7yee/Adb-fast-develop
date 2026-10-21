# ADB Dashboard

This project is an Electron desktop application. The active entry point is `electron/main.js`; the old Python/PyQt implementation is preserved in `legacy-python/` only as a migration reference.

## Development

- Install dependencies: `npm install`
- Run: `npm start`
- Core tests: `npm test`
- Windows packages: `npm run dist`
- ADB must be available on the host `PATH`.

## Structure

- `electron/main.js`: window lifecycle and IPC handlers.
- `electron/preload.js`: narrow, context isolated renderer API.
- `electron/adb.js`: device detection and process execution. Use `spawn` with an argument list, never a host shell.
- `electron/config.js`: YAML command migration, validation, and persistence in Electron user data.
- `electron/renderer/`: UI. Keep untrusted command output as text, not HTML.
- `config/commands.yaml`: bundled default command set; do not write to it at runtime.
- `tests/`: Node core tests and a manual Electron UI smoke check.

Preserve the existing command types (`read`, `streaming`, `action`) and user workflows when changing behavior. Keep changes focused and verify them with a relevant test or a running app check.
