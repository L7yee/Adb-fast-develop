# ADB Dashboard

The current application is in `electron/`. The Python/PyQt implementation is preserved in `legacy-python/` as a separate historical version. New application work should use Electron; do not add a Python dependency to the current app.

## Start every new conversation here

- Read `docs/PROJECT_STATE.md` and `CHANGELOG.md` before changing the project. They record the current release, user decisions, verification evidence, and remaining limitations.
- Check `git status --short --branch` before editing. Preserve existing user changes.
- Run `node electron/scripts/history.js` from the repository root to read every commit with the application version stored in that commit. This command is read-only and needs no npm dependencies.
- Check `electron/package.json`, the lockfile root version, and the release tag before choosing a new version. Git and the current files take precedence when a document has become stale; correct the document and report the mismatch.

## Keep the project record current

- For every completed change, update the unreleased section of `CHANGELOG.md` with what changed and the checks actually performed. Update `docs/PROJECT_STATE.md` whenever the current behavior, release, user decisions, or outstanding work changes.
- Commit hashes are recorded automatically by Git and shown by the history command, including documentation commits. Do not create another commit merely to insert the previous documentation commit's hash into itself.
- For an application release, keep `electron/package.json` and its lockfile root versions aligned; use `vX.Y.Z` tags and record the tag, source commit, release URL, changes, and validation in `CHANGELOG.md`. Only call a release published after confirming its actual uploaded assets.
- Documentation-only changes do not require a new application version, installer, or Release. Record them under unreleased instead.
- The user expects completed changes to be committed and pushed, and application releases to include an installer and portable ZIP on GitHub. Respect any narrower instruction in the current conversation and report failures honestly.
- End with the resulting version/commit or Release link, relevant verification, and any unfinished work. Do not rely on chat history as the only record.

## Development

- Run commands from `electron/`: `npm ci`, `npm start`, `npm test`, `npm run dist`.
- ADB must be available on the host `PATH` for device features.
- `electron/main.js`: window lifecycle and IPC handlers.
- `electron/preload.js`: narrow, context isolated renderer API.
- `electron/adb.js`: device detection and process execution. Use `spawn` with an argument list, never a host shell.
- `electron/display-info.js`: one-shot screen information reads, source priorities, and parsing.
- `electron/config.js`: YAML command migration, validation, and persistence in Electron user data.
- `electron/renderer/`: UI. Keep untrusted command output as text, not HTML.
- `electron/config/commands.yaml`: bundled default commands; do not write to it at runtime.
- `electron/tests/`: Node core tests and a manual Electron UI smoke check.

Commands run once per click (`read` or `action`). Keep kernel and Logcat snapshots in the Logs workspace, with separate persisted save paths. Preserve the remaining user workflows and verify changes with a relevant test or a running app check.
