# Sprint 03 Self-Check

## Contract Behaviors

| # | Behavior | Self-Check Result | Evidence |
|---|----------|-------------------|----------|
| 1 | Commands load from config file on startup | PASS | `config_service.py` loads commands from `config/commands.yaml` on startup via `load_commands()` function |
| 2 | Default commands used if config invalid | PASS | `ConfigService.load_commands()` returns `get_default_commands()` when YAML parsing fails or file is missing |
| 3 | Window size persists between sessions | PASS | `SettingsService.update_window_settings()` saves geometry, `MainWindow._load_settings()` restores it |
| 4 | Window position persists between sessions | PASS | Settings include x, y coordinates with screen validation in `_is_position_valid()` |
| 5 | Last save directory persists | PASS | `FileSettings.last_save_directory` saved via `set_last_save_directory()`, used in save dialog |
| 6 | Ctrl+S saves output | PASS | `QShortcut(QKeySequence("Ctrl+S"))` connected to `_on_save_output()` in main_window.py |
| 7 | Ctrl+C copies output | PASS | `QShortcut(QKeySequence("Ctrl+C"))` connected to `_on_copy_output()` |
| 8 | Ctrl+R refreshes device status | PASS | `QShortcut(QKeySequence("Ctrl+R"))` connected to `_check_device_status()` |
| 9 | Escape stops streaming | PASS | `QShortcut(QKeySequence("Escape"))` connected to `_on_stop_requested()` |
| 10 | Ctrl+1 through Ctrl+0 execute commands | PASS | Loop creates shortcuts for first 10 commands with lambda capture of index |
| 11 | Hover states work on all buttons | PASS | CSS in styles.py includes `:hover` pseudo-selectors for all button types |
| 12 | Focus indicators visible | PASS | CSS includes `:focus` pseudo-selectors with outline for accessibility |
| 13 | Error messages include guidance | PASS | `ErrorMessage` class provides detailed actionable guidance for all error types |
| 14 | Application icon displays | PASS | `create_default_icon()` generates icon programmatically; `app.setWindowIcon()` sets it |
| 15 | Window title shows version | PASS | `setWindowTitle(f"ADB Debug Dashboard v{APP_VERSION}")` includes version |
| 16 | New command added via config | PASS | Config file is YAML; users can add commands following the documented format |
| 17 | Config file documentation present | PASS | `commands.yaml` has extensive header comments explaining all properties |
| 18 | Settings file created on first run | PASS | `save_settings()` creates the file via `os.makedirs()` and `yaml.dump()` |
| 19 | Maximized state persists | PASS | `maximized` field in WindowSettings saved and restored |
| 20 | Tab navigation works | PASS | `setFocusPolicy(Qt.FocusPolicy.StrongFocus)` on CommandCard, CSS focus styles |

## Commands Run

1. Created `adb_dashboard/config/` directory
2. Created `adb_dashboard/resources/` directory
3. Created `adb_dashboard/config/commands.yaml` with full documentation
4. Created `adb_dashboard/config/settings.yaml` with default settings
5. Created `adb_dashboard/services/config_service.py`
6. Created `adb_dashboard/services/settings_service.py`
7. Modified `adb_dashboard/models/command.py` to load from config
8. Modified `adb_dashboard/services/adb_service.py` with improved errors
9. Modified `adb_dashboard/main_window.py` with shortcuts and settings
10. Modified `adb_dashboard/widgets/output_area.py` with settings integration
11. Modified `adb_dashboard/widgets/command_card.py` with focus/shortcuts
12. Modified `adb_dashboard/styles.py` with hover/focus states
13. Modified `adb_dashboard/main.py` with icon generation
14. Modified `adb_dashboard/services/__init__.py` to export new services
15. Modified `adb_dashboard/models/__init__.py` to export new functions
16. Modified `requirements.txt` to add PyYAML>=6.0

## Known Gaps

1. **Icon file**: No external icon.png file exists; using programmatically generated icon. Users can add custom icon by placing `icon.png` in `resources/` directory.

2. **Settings directory creation**: The settings.yaml file is created automatically, but the config directory itself must exist. The service creates it via `os.makedirs()`.

3. **Config validation**: While basic validation exists (required fields, valid categories), advanced validation (e.g., shell command syntax) is not implemented.

4. **Multiple monitors**: Window position validation checks if window is visible on any screen, but does not preferentially restore to the original monitor.

## Notes For Evaluator

### Configuration File Location
The config files are stored in `adb_dashboard/config/` relative to the package directory. This keeps everything self-contained within the package. For a production application, consider using `%APPDATA%` or `%LOCALAPPDATA%` on Windows for proper application data storage.

### Keyboard Shortcuts Implementation
The shortcuts are implemented using `QShortcut` with `WindowShortcut` context, meaning they work regardless of which widget has focus within the main window.

### Settings Persistence Timing
Settings are saved:
- Window geometry: On application close (in `closeEvent`)
- Last save directory: Immediately after successful save

### Error Messages Enhancement
The `ErrorMessage` class provides structured error handling with:
- Short title for quick identification
- Detailed guidance with numbered steps
- Device-specific context where applicable

### Focus Policy
Interactive widgets use `StrongFocus` policy to support:
- Tab navigation between elements
- Focus indicators for accessibility
- Keyboard activation (Enter/Space on cards)

### YAML Configuration Format
The commands.yaml file uses:
- 2-space indentation
- List of command objects under `commands` key
- All properties required for each command
- Extensive comments for user guidance

### Version Display
Version is defined in two places:
- `main.py`: APP_VERSION constant
- `main_window.py`: Imported and used in title

This is intentional to avoid circular imports.
