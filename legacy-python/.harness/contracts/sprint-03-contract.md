# Sprint 03 Contract

## Summary

Sprint 3 focuses on polish and extensibility - transforming the functional application from Sprint 2 into a polished, user-friendly, and extensible tool. This sprint introduces a command registry system with external configuration, UI refinements, keyboard shortcuts, settings persistence, and developer documentation for extending commands.

## Primary Path

1. User launches the application - it loads commands from an external YAML config file
2. Window opens with the remembered size and position from the previous session
3. User interacts with the polished UI - proper hover states, spacing, and visual consistency
4. User executes a command using keyboard shortcut (Ctrl+1 through Ctrl+0 for commands)
5. User presses Ctrl+S to save output, Ctrl+C to copy when output area is focused
6. User closes the application - settings (window size, position, last save directory) are persisted
7. Developer can add new commands by editing the config file without touching code

## In Scope

### 1. Command Registry with External Configuration

- YAML configuration file for command definitions
- Application loads commands from config file at startup
- Config file supports all command properties: id, label, shell_command, category, auto_refresh_capable
- Graceful fallback to default commands if config file is missing or invalid
- Config file location: `config/commands.yaml` (user can edit to add/modify commands)

### 2. Settings Persistence

- Window size and position remembered between sessions
- Last used directory for Save dialog persisted
- Settings stored in `config/settings.yaml`
- Settings loaded on startup, saved on application close

### 3. UI Polish

- Consistent hover states across all interactive elements
- Proper spacing and padding throughout
- Button press states with visual feedback
- Focus indicators for keyboard navigation
- Smooth state transitions (no jarring color changes)
- Application icon (embedded or referenced)

### 4. Keyboard Shortcuts

- Ctrl+S: Save output to file
- Ctrl+C: Copy output to clipboard (when output area focused)
- Ctrl+R: Refresh device status
- Escape: Stop current operation (streaming/auto-refresh)
- Number keys 1-9, 0 for quick command access (Ctrl+1 through Ctrl+0)
- Shortcuts documented in tooltips

### 5. Error Message Improvements

- Actionable guidance in error messages
- Specific messages for common failure scenarios
- Suggested actions when errors occur (e.g., "Check that USB debugging is enabled")

### 6. Documentation

- Docstring block in config file explaining how to add new commands
- Inline comments in YAML config explaining each property
- README section for extensibility (added to config file header)

### 7. Application Metadata

- Application icon (PNG embedded in package or loaded from file)
- Window title includes version number
- About dialog accessible via menu or button

## Out Of Scope

- Plugin architecture with dynamic loading (config file modification only)
- User-editable commands through GUI (config file editing only)
- Theme customization (dark theme remains locked)
- Localization/translation support
- Command aliases or custom shell commands through UI
- Multi-profile configurations

## Locked Assumptions

- Python 3.13.13 runtime
- PyQt6 GUI framework
- Windows-only platform
- YAML for configuration (human-readable, comment-friendly)
- Single device model unchanged
- Dark theme design direction unchanged
- Existing Sprint 1 and Sprint 2 features are complete and functional

## Files Expected To Change

### Files to Modify

| File | Changes |
|------|---------|
| `main.py` | Add icon loading, settings initialization, keyboard shortcuts, application metadata |
| `main_window.py` | Add keyboard shortcut handlers, settings persistence (save/restore window geometry), closeEvent enhancement |
| `models/command.py` | Refactor to load from config file, add config loading logic |
| `widgets/command_card.py` | Polish hover/press states, add keyboard shortcut badge/tooltip |
| `widgets/output_area.py` | Add keyboard shortcut support (Ctrl+S, Ctrl+C), polish button states |
| `services/adb_service.py` | Improve error messages with actionable guidance |
| `styles.py` | Refine hover states, focus indicators, consistent spacing |

### New Files to Create

| File | Purpose |
|------|---------|
| `config/commands.yaml` | External command definitions with documentation |
| `config/settings.yaml` | Persisted application settings |
| `services/config_service.py` | Service for loading/saving configuration files |
| `services/settings_service.py` | Service for managing application settings |
| `resources/icon.png` | Application icon (optional, can be embedded) |

### Directory Structure Addition

```
adb_dashboard/
  config/           <-- NEW
    commands.yaml
    settings.yaml
  resources/        <-- NEW (optional)
    icon.png
  services/
    config_service.py   <-- NEW
    settings_service.py <-- NEW
```

## Technical Specifications

### Configuration File Format (commands.yaml)

```yaml
# ADB Debug Dashboard - Command Configuration
# ============================================
#
# To add a new command, copy an existing command block and modify:
#   - id: Unique identifier (no spaces, use underscores)
#   - label: Display name shown on the command card
#   - shell_command: The ADB shell command to execute
#   - category: One of "read", "streaming", or "action"
#   - auto_refresh_capable: true/false - whether polling applies
#
# Category types:
#   - read: Standard command that reads and returns output
#   - streaming: Continuous output (e.g., getevent)
#   - action: Launches an activity (e.g., engineer mode)
#
# Auto-refresh capable commands:
#   Commands that benefit from periodic polling (e.g., memory info).
#   The user can enable auto-refresh with configurable intervals.

commands:
  - id: memory_info
    label: Memory Info
    shell_command: cat /proc/meminfo
    category: read
    auto_refresh_capable: true

  - id: brightness
    label: Brightness
    shell_command: cat /sys/class/leds/lcd-backlight/brightness
    category: read
    auto_refresh_capable: true

  # ... (remaining 8 commands)
```

### Settings File Format (settings.yaml)

```yaml
# ADB Debug Dashboard - User Settings
# Automatically managed - do not edit manually

window:
  width: 1024
  height: 700
  x: 100
  y: 100
  maximized: false

file:
  last_save_directory: ""

version: 1
```

### ConfigService Class

```python
class ConfigService:
    """Service for loading and validating command configuration."""

    CONFIG_PATH = "config/commands.yaml"

    def load_commands() -> List[Command]:
        """Load commands from YAML config file."""

    def validate_config(config: dict) -> bool:
        """Validate config structure and required fields."""

    def get_default_commands() -> List[Command]:
        """Return hardcoded default commands if config is invalid."""
```

### SettingsService Class

```python
class SettingsService:
    """Service for managing application settings persistence."""

    SETTINGS_PATH = "config/settings.yaml"

    def load_settings() -> Settings:
        """Load settings from file, return defaults if missing."""

    def save_settings(settings: Settings):
        """Save current settings to file."""

    def get_last_save_directory() -> str:
        """Get the last used directory for file save dialog."""

    def set_last_save_directory(path: str):
        """Update the last used save directory."""
```

### Keyboard Shortcut Implementation

```python
# In MainWindow
def _setup_shortcuts(self):
    """Setup keyboard shortcuts."""
    # Ctrl+S: Save
    self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
    self.save_shortcut.activated.connect(self._on_save_output)

    # Ctrl+C: Copy (when output area focused)
    self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
    self.copy_shortcut.activated.connect(self._on_copy_output)

    # Ctrl+R: Refresh device status
    self.refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
    self.refresh_shortcut.activated.connect(self._check_device_status)

    # Escape: Stop operation
    self.stop_shortcut = QShortcut(QKeySequence("Escape"), self)
    self.stop_shortcut.activated.connect(self._on_stop_requested)

    # Ctrl+1 through Ctrl+0: Quick command access
    for i in range(10):
        key = i + 1 if i < 9 else 0
        shortcut = QShortcut(QKeySequence(f"Ctrl+{key}"), self)
        shortcut.activated.connect(lambda _, idx=i: self._execute_command_by_index(idx))
```

### Improved Error Messages

| Scenario | Error Message | Actionable Guidance |
|----------|--------------|---------------------|
| Device not connected | "Device not connected" | "Connect your device via USB and enable USB debugging in Developer Options" |
| ADB not found | "ADB not found in PATH" | "Install Android SDK Platform Tools and add 'adb' to your system PATH" |
| Permission denied | "Permission denied" | "Ensure USB debugging is authorized on the device. Check the authorization prompt on your device screen" |
| Command timeout | "Command timed out" | "The device may be unresponsive. Try disconnecting and reconnecting" |
| Activity not found | "Activity not found" | "This engineer mode app may not be installed on your device" |
| Empty output | "No output received" | "The command completed but returned no data. The file or resource may not exist on this device" |

## Testable Behaviors

| # | Behavior | Verification |
|---|----------|--------------|
| 1 | Commands load from config file on startup | Delete/modify config file, verify commands reflect changes |
| 2 | Default commands used if config invalid | Corrupt config file, verify app still launches with default commands |
| 3 | Window size persists between sessions | Resize window, close, reopen - verify size is remembered |
| 4 | Window position persists between sessions | Move window, close, reopen - verify position is remembered |
| 5 | Last save directory persists | Save to specific directory, close, reopen save dialog - verify same directory |
| 6 | Ctrl+S saves output | Execute command, press Ctrl+S, verify save dialog opens |
| 7 | Ctrl+C copies output | Execute command, press Ctrl+C, paste in editor - verify content matches |
| 8 | Ctrl+R refreshes device status | Press Ctrl+R, verify device status refreshes |
| 9 | Escape stops streaming | Start streaming, press Escape, verify streaming stops |
| 10 | Ctrl+1 executes first command | Press Ctrl+1, verify first command executes |
| 11 | Ctrl+0 executes tenth command | Press Ctrl+0, verify tenth command executes |
| 12 | Hover states work on all buttons | Hover over each button, verify visual state change |
| 13 | Focus indicators visible | Tab through UI, verify focus outline on each element |
| 14 | Error messages include guidance | Disconnect device, execute command, verify actionable guidance shown |
| 15 | Application icon displays | Check window icon and taskbar icon |
| 16 | Window title shows version | Verify title includes version number |
| 17 | New command added via config | Add new command to config, restart app, verify new command appears |
| 18 | Config file documentation present | Open config file, verify docstring header explains how to add commands |
| 19 | Settings file created on first run | Delete settings file, launch app, close, verify settings file created |
| 20 | Maximized state persists | Maximize window, close, reopen - verify still maximized |

## Acceptance Criteria

1. Commands can be added by editing `config/commands.yaml` without code changes
2. Application loads commands from config file on startup
3. Graceful fallback to default commands if config is invalid or missing
4. Window size and position persist between sessions
5. Last used save directory persists between sessions
6. Ctrl+S triggers save output action
7. Ctrl+C copies output when output area has focus
8. Ctrl+R refreshes device status
9. Escape stops any running operation
10. Ctrl+1 through Ctrl+0 execute commands 1-10
11. All buttons have consistent hover states
12. All interactive elements have visible focus indicators
13. Error messages include actionable guidance
14. Application icon is visible in window and taskbar
15. Window title includes application name and version
16. Config file includes documentation explaining command addition
17. Settings file is created automatically if missing
18. UI feels polished with consistent spacing and transitions
19. Tab navigation works through all interactive elements
20. Application version is displayed (title bar, about if implemented)

## Runtime Assumptions

- Application runs on Windows 10/11
- Python 3.13.13 is installed
- PyQt6 is installed via requirements.txt
- PyYAML is installed for config file parsing
- ADB is in system PATH (for actual device commands)
- Config directory is writable by the application
- User has basic YAML editing capability for command extension

## Risks Or Notes

### Technical Risks

1. **Config file migration**: If config format changes in future versions, consider migration path. Mitigation: Include version field in config file.

2. **Settings file corruption**: If settings file becomes corrupted, app should not crash. Mitigation: Validate on load, fall back to defaults, log warning.

3. **Window position off-screen**: If saved position is outside visible screen area (e.g., after monitor disconnect), window may be unreachable. Mitigation: Validate position against available screens, reset to default if invalid.

4. **Keyboard shortcut conflicts**: System or other apps may intercept shortcuts. Mitigation: Use standard conventions (Ctrl+S, Ctrl+C), document in UI.

5. **Config file encoding**: YAML file must be UTF-8 for non-ASCII characters in labels. Mitigation: Explicitly specify encoding on read/write.

### Implementation Notes

1. **Config file location**: Consider using `appdirs` or similar for proper Windows app data location, but for simplicity, `config/` subdirectory is acceptable for this project.

2. **YAML library**: Use `PyYAML` package. Add to requirements.txt if not already present.

3. **Settings save timing**: Save settings in `closeEvent` handler. Also save after file save dialog to persist last directory.

4. **Icon embedding**: For reliability, consider embedding icon as base64 in Python file rather than external file (eliminates missing icon file risk).

5. **Shortcut context**: Use `Qt.ShortcutContext.WindowShortcut` for application-wide shortcuts, `WidgetShortcut` for widget-specific.

6. **Focus policy**: Set `Qt.FocusPolicy.StrongFocus` on interactive widgets for proper tab navigation.

### Edge Cases

1. **Config file with no commands**: Should show error or fall back to defaults
2. **Config file with duplicate IDs**: Should log warning and use first occurrence
3. **Invalid category value**: Should default to "read" with warning
4. **Invalid shell_command (empty)**: Should skip command with warning
5. **Settings file read-only**: Should log warning and use in-memory defaults
6. **Multiple monitors**: Window should restore to correct monitor
7. **Window maximized then closed**: Should restore maximized on next launch
8. **Very long command output**: Copy/save should still work (no size limit)

### Dependencies to Add

```
PyYAML>=6.0
```

---

## Sprint 3 Implementation Phases

### Phase 1: Configuration Infrastructure
1. Create config directory structure
2. Implement ConfigService for loading commands from YAML
3. Create default commands.yaml with documentation
4. Refactor Command model to use config service

### Phase 2: Settings Persistence
1. Implement SettingsService
2. Create settings.yaml structure
3. Add window geometry save/restore
4. Add last save directory persistence

### Phase 3: Keyboard Shortcuts
1. Add QShortcut handlers for all shortcuts
2. Connect shortcuts to actions
3. Add shortcut hints to tooltips
4. Test all shortcuts work correctly

### Phase 4: UI Polish
1. Refine all hover states in styles.py
2. Add focus indicators
3. Ensure consistent spacing
4. Add application icon
5. Update window title with version

### Phase 5: Error Messages
1. Improve error messages with actionable guidance
2. Add specific error detection logic
3. Test all error scenarios

### Phase 6: Final Testing
1. Test all testable behaviors
2. Verify config file documentation is clear
3. Test edge cases
4. Final UI review

---

*Contract created by Generator subagent on 2026-04-14.*
