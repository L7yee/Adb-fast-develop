---
working_directory: E:/workplace
install_command: pip install -r requirements.txt
build_command: none
start_command: python -m adb_dashboard.main
access_url: none
healthcheck_method: gui-launch
healthcheck_url: none
---

# Runtime Notes

## Prerequisites

1. **Python 3.13.13** must be installed and available in PATH
2. **ADB (Android Debug Bridge)** must be installed and in system PATH
   - Verify with: `adb version`
   - Common locations: Android SDK platform-tools directory
3. **PyQt6** dependency (installed via requirements.txt)
4. **PyYAML** dependency (installed via requirements.txt)

## Startup Steps

1. Open a command prompt/terminal
2. Navigate to the project directory: `cd E:/workplace`
3. Install dependencies (first time only): `pip install -r requirements.txt`
4. Launch the application: `python -m adb_dashboard.main`

## Sprint 3 Features

### Configuration System

Commands are now loaded from an external YAML configuration file at `adb_dashboard/config/commands.yaml`.

**To add a new command:**
1. Open `config/commands.yaml`
2. Copy an existing command block
3. Modify the properties:
   - `id`: Unique identifier (use underscores, no spaces)
   - `label`: Display name shown on the command card
   - `shell_command`: The ADB shell command (without 'adb shell' prefix)
   - `category`: One of "read", "streaming", or "action"
   - `auto_refresh_capable`: true/false
4. Save and restart the application

**If the config file is missing or invalid:**
The application falls back to default commands automatically.

### Settings Persistence

User settings are saved to `adb_dashboard/config/settings.yaml`:
- Window size and position
- Maximized state
- Last used save directory

Settings are automatically:
- Loaded on startup
- Saved when closing the application
- Created with defaults if missing

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save output to file |
| Ctrl+C | Copy output to clipboard |
| Ctrl+R | Refresh device status |
| Escape | Stop current operation |
| Ctrl+1 | Execute first command |
| Ctrl+2 | Execute second command |
| ... | ... |
| Ctrl+0 | Execute tenth command |

Shortcuts are also shown in button tooltips.

### UI Polish

- Consistent hover states on all buttons
- Focus indicators for keyboard navigation (Tab key)
- Button press states with visual feedback
- Smooth transitions
- Application icon visible in window and taskbar
- Window title includes version number

### Error Messages

Error messages now include actionable guidance:

| Scenario | Message Includes |
|----------|-----------------|
| Device not connected | Steps to connect device and enable USB debugging |
| ADB not found | Installation instructions |
| Permission denied | Authorization troubleshooting |
| Command timeout | Device recovery steps |
| Activity not found | Device compatibility notes |
| Empty output | Possible causes |

## All 10 Commands Functional

| Command | Category | Special Features |
|---------|----------|------------------|
| Memory Info | read | Auto-refresh capable, Ctrl+1 |
| Brightness | read | Auto-refresh capable, Ctrl+2 |
| GPIO Status | read | Auto-refresh capable, Ctrl+3 |
| Interrupt Info | read | Auto-refresh capable, Ctrl+4 |
| Serial Port Info | read | Standard, Ctrl+5 |
| Audio Register Info | read | Standard, Ctrl+6 |
| Get Events | streaming | Real-time streaming, Ctrl+7 |
| Unisoc Engineer Mode | action | Activity launch, Ctrl+8 |
| MTK Engineer Mode | action | Activity launch, Ctrl+9 |
| MTK DebugLogger | action | Activity launch, Ctrl+0 |

### Auto-Refresh Feature

Commands marked as auto-refresh capable display:
- Toggle button (AR) on the card
- Interval dropdown (1s, 5s, 10s, 30s)
- Cyan border/indicator when active

### Streaming Support

The "Get Events" command provides real-time streaming output:
- Events appear line-by-line as they occur
- Stop button appears in toolbar during streaming
- Click Stop or press Escape to terminate

### Export Functionality

The output toolbar provides:
- **Save**: Opens file dialog to save output as .txt file (Ctrl+S)
- **Copy**: Copies current output to system clipboard (Ctrl+C)
- **Stop**: Visible during streaming or auto-refresh operations (Escape)
- **Clear**: Removes output and stops any active operations

### Execution State Feedback

The state label shows:
- **Ready** (gray): No operation active
- **Running...** (amber): Command executing
- **Streaming...** (amber): Real-time streaming active
- **Auto-Refresh** (cyan): Periodic polling active
- **Completed** (green): Command finished successfully
- **Error** (red): Command failed with guidance

## Verification Notes

### Application Launch Verification

When the application starts, verify:

1. **Main window appears** with title "ADB Debug Dashboard v0.3.0"
2. **Window size** is remembered from previous session (or default 1024x700)
3. **Dark theme** is applied (dark background, light text)
4. **Application icon** is visible in window title bar and taskbar
5. **Header** contains:
   - App title "ADB Debug Dashboard v0.3.0"
   - Status indicator (colored dot + label)
   - "Refresh" button (tooltip shows Ctrl+R)
6. **Left panel** shows command cards in 2-column grid
7. **Right panel** shows output area with toolbar
8. **Config file** is read (commands appear as defined in commands.yaml)

### Device Status Verification

- **Green indicator + device ID**: Device connected
- **Gray indicator + "Disconnected"**: No device connected
- **Red indicator + "ADB not found"**: ADB not in PATH

### Keyboard Shortcuts Verification

1. Press Ctrl+R - device status should refresh
2. Execute a command, press Ctrl+S - save dialog should open
3. Execute a command, press Ctrl+C - output should be copied
4. Start streaming, press Escape - streaming should stop
5. Press Ctrl+1 through Ctrl+0 - respective commands should execute

### Settings Persistence Verification

1. Resize the window to a specific size
2. Move the window to a specific position
3. Close the application
4. Reopen the application
5. Verify window opens at the same size and position

### Configuration File Verification

1. Open `adb_dashboard/config/commands.yaml`
2. Verify documentation header is present
3. Add a new test command
4. Restart the application
5. Verify the new command appears
6. Remove the test command

### Error Messages Verification

1. Disconnect all devices
2. Execute any command
3. Verify error message includes actionable guidance
4. The message should suggest steps to resolve the issue

## Technical Notes

- Commands execute asynchronously in background threads (QThread)
- Streaming uses subprocess.Popen with line-by-line reading
- Auto-refresh uses QTimer for periodic execution
- UI does not block during any operation
- Output uses Consolas monospace font
- Minimum window size enforced at 800x600
- Standard command timeout: 30 seconds
- Auto-refresh default interval: 5 seconds
- Settings saved in YAML format with UTF-8 encoding
- Config validation with fallback to defaults
- Window position validated against screen geometry

## Files Structure

```
adb_dashboard/
  config/
    commands.yaml     # Command definitions (editable)
    settings.yaml     # User settings (auto-managed)
  models/
    command.py        # Command model with config loading
  services/
    adb_service.py    # ADB execution with improved errors
    config_service.py # YAML config loader
    settings_service.py # Settings persistence
  widgets/
    command_card.py   # Command cards with shortcuts
    output_area.py    # Output with save/copy
    auto_refresh_controls.py
    status_indicator.py
  resources/
    README.md         # Icon instructions
  main.py             # Entry point with icon
  main_window.py      # Main window with shortcuts
  styles.py           # Dark theme with focus states
```
