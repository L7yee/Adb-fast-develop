# Sprint 01 Contract

## Summary

Build the foundation for ADB Debug Dashboard: a PyQt6 application scaffold with ADB service layer, device status detection, command card layout, and click-to-execute functionality for 5 simple read commands with output display.

## Primary Path

1. User launches the application
2. Application displays main window with header showing device connection status
3. User sees 10 command cards in a grid layout (5 are clickable, 5 are displayed but disabled)
4. User clicks a clickable command card (e.g., "Memory Info")
5. Application executes the ADB shell command
6. Output appears in the terminal-style text area on the right
7. If no device is connected, appropriate error message displays

## In Scope

### Application Scaffold
- PyQt6 main window with dark theme styling
- Minimum window size 800x600, resizable
- Header bar with app title and device status indicator
- Two-panel layout: command cards on left, output area on right

### ADB Service Layer
- Device detection via `adb devices` command
- Shell command execution via `adb shell <command>`
- Asynchronous/non-blocking command execution
- Error handling for:
  - Device not connected
  - ADB not installed/not in PATH
  - Command execution failure

### UI Components
- Device status indicator (connected/disconnected/error states)
- Command card grid (2 columns, scrollable)
- Output text area (monospace font, read-only, scrollable)
- Visual feedback for command execution states

### Clickable Commands (Sprint 1)
These 5 simple read commands will be executable:
1. `cat /proc/meminfo` - Memory Info
2. `cat /sys/class/leds/lcd-backlight/brightness` - Brightness
3. `cat /sys/kernel/debug/gpio` - Kernel GPIO Status
4. `cat /proc/interrupts` - Interrupt Info
5. `cat /proc/tty/driver/serial` - Serial Port Info

### Displayed Commands (Not Yet Executable)
These 5 commands will be visible but disabled for Sprint 1:
1. `cat /sys/kernel/debug/mtksocaudio` - Audio Register Info
2. `getevent -l` - Get Events (streaming command)
3. `am start -n com.sprd.engineermode/.EngineerModeActivity` - Unisoc Engineer Mode
4. `am start com.mediatek.engineermode/com.mediatek.engineermode.EngineerMode` - MTK Engineer Mode
5. `am start com.debug.loggerui/com.debug.loggerui.MainActivity` - MTK DebugLogger

## Out Of Scope

- Auto-refresh/polling functionality (Sprint 2)
- Streaming command support for `getevent -l` (Sprint 2)
- Export functionality (save to file, copy to clipboard) (Sprint 2)
- Stop/cancel button for running commands (Sprint 2)
- Command registry configuration file (Sprint 3)
- Keyboard shortcuts (Sprint 3)
- Settings persistence (Sprint 3)
- UI polish and animations (Sprint 3)

## Locked Assumptions

| Decision | Value |
|----------|-------|
| GUI Framework | PyQt6 |
| Python Version | 3.13.13 |
| Platform | Windows only |
| Theme | Dark theme (default) |
| Device Model | Single connected device |
| Output Style | Terminal plain text |
| ADB Path | System PATH (user must have ADB installed) |

## Files Expected To Change

### New Files to Create

```
adb_dashboard/
    __init__.py
    main.py                    # Application entry point
    main_window.py             # Main PyQt6 window
    styles.py                  # Dark theme stylesheet
    services/
        __init__.py
        adb_service.py         # ADB command execution service
    models/
        __init__.py
        command.py             # Command data model
    widgets/
        __init__.py
        command_card.py        # Command card widget
        output_area.py         # Output display widget
        status_indicator.py    # Device status indicator widget
requirements.txt               # PyQt6 dependency
```

### No Existing Files to Modify

This is a new project with no existing application source code.

## Testable Behaviors

| # | Behavior | Verification |
|---|----------|--------------|
| 1 | Application launches and displays main window | Run `python adb_dashboard/main.py`, verify window appears with title "ADB Debug Dashboard" |
| 2 | Window has minimum size of 800x600 | Launch app, attempt to resize below minimum, verify constraint |
| 3 | Device status indicator shows in header | Visually verify status indicator present in header area |
| 4 | When device connected, status shows green "Connected" | Connect ADB device, verify status indicator shows connected state |
| 5 | When no device connected, status shows gray "Disconnected" | Disconnect all devices, verify status indicator shows disconnected state |
| 6 | 10 command cards display in 2-column grid | Visually verify 10 cards in grid layout |
| 7 | 5 simple read commands are clickable | Verify Memory Info, Brightness, GPIO Status, Interrupt Info, Serial Port Info cards respond to hover and click |
| 8 | 5 advanced commands are disabled (grayed out) | Verify Audio Register, Get Events, and 3 Engineer Mode cards are visually disabled and non-clickable |
| 9 | Clicking a clickable card executes ADB command | Click "Memory Info" card with device connected, verify `adb shell cat /proc/meminfo` is executed |
| 10 | Command output displays in output area | After clicking Memory Info, verify output appears in right panel text area |
| 11 | Output uses monospace font | Verify output text renders in Consolas or similar monospace font |
| 12 | Error message shows when device not connected | With no device, click a command card, verify "Device not connected" or similar message appears |
| 13 | Error message shows when ADB not available | With ADB not in PATH, launch app, verify appropriate error indicator/message |
| 14 | UI does not freeze during command execution | Execute a command, verify window remains responsive |
| 15 | Refresh button re-checks device status | Click refresh button, verify device status updates |

## Runtime Assumptions

1. User has ADB installed and accessible via system PATH
2. User has Python 3.13.13 installed
3. User has PyQt6 installed or will install via `pip install -r requirements.txt`
4. A single Android device may or may not be connected via USB
5. USB debugging is enabled on the connected device (if any)

## Technical Specifications

### ADB Service Interface

```python
class ADBService:
    def is_adb_available() -> bool:
        """Check if ADB is installed and in PATH."""

    def get_device_status() -> DeviceStatus:
        """Check if a device is connected. Returns DeviceStatus enum."""

    def execute_command(command: str) -> CommandResult:
        """Execute an ADB shell command asynchronously.
        Returns CommandResult with output or error."""

    def check_device() -> bool:
        """Run 'adb devices' and check for connected device."""
```

### Command Model

```python
@dataclass
class Command:
    id: str
    label: str
    shell_command: str
    is_clickable: bool  # True for Sprint 1 executable commands
    category: str       # "read" or "action" or "streaming"
```

### Color Palette

| Element | Color Code |
|---------|------------|
| Background | #1e1e1e |
| Card Surface | #2d2d2d |
| Accent | #0078d4 |
| Success | #4caf50 |
| Error | #f44336 |
| Warning | #ff9800 |
| Primary Text | #e0e0e0 |
| Secondary Text | #9e9e9e |

### Window Layout Structure

```
+--------------------------------------------------+
| Header: [App Title]     [Status Indicator] [Refresh] |
+---------------------+----------------------------+
|                     |                            |
|   Command Cards     |     Output Area            |
|   (2-column grid)   |     (monospace, scrollable)|
|   [Scrollable]      |                            |
|                     |                            |
+---------------------+----------------------------+
```

## Risks Or Notes

### Technical Risks
1. **ADB path variability**: Users may have ADB installed in non-standard locations. Consider future enhancement to allow custom ADB path configuration.
2. **Encoding issues**: ADB output may contain non-UTF-8 characters. Handle with `errors='replace'` or similar strategy.
3. **Long output**: Some commands (e.g., `cat /proc/interrupts`) may produce lengthy output. Ensure scrolling works smoothly.

### Implementation Notes
1. Use `QThread` or `QThreadPool` for async ADB command execution to prevent UI freezing
2. Use `subprocess.run()` with timeout for ADB commands to prevent indefinite hangs
3. Store command definitions in a Python list initially (will migrate to config file in Sprint 3)
4. Use Qt signals/slots for communication between service layer and UI
5. Consider using `adb devices -l` for more detailed device info if needed later

### Deferred to Later Sprints
- The 5 disabled commands require special handling:
  - Audio Register Info: May require root access on some devices
  - Get Events: Requires streaming output support (Sprint 2)
  - Engineer Mode commands: Launch activities, not read commands (Sprint 2)

## Acceptance Criteria Summary

- [ ] App launches and displays main window with dark theme
- [ ] Device connection status shows correctly in header
- [ ] 10 command cards display in grid layout (5 clickable, 5 disabled)
- [ ] Clicking a clickable card executes the corresponding ADB command
- [ ] Command output appears in the output text area
- [ ] "Device not connected" message shows when appropriate
- [ ] UI remains responsive during command execution
- [ ] Window minimum size enforced at 800x600
