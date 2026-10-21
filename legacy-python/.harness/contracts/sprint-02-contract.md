# Sprint 02 Contract

## Summary

Extend the ADB Debug Dashboard with full command support for all 10 commands, streaming output for `getevent -l`, auto-refresh/polling capability, export functionality, and enhanced execution state feedback.

## Primary Path

1. User launches the application (Sprint 1 foundation)
2. All 10 command cards are now clickable and functional
3. User clicks a streaming command card ("Get Events")
4. Output area shows real-time streaming events until user clicks Stop
5. User clicks a polling-capable command (e.g., "Memory Info")
6. User enables auto-refresh toggle and selects interval (5s)
7. Output automatically refreshes every 5 seconds until disabled or command changes
8. User clicks Save button to export output to a text file
9. User clicks Copy button to copy output to clipboard
10. Clear button removes current output content

## In Scope

### All 10 Commands Functional

Enable execution of all 10 commands defined in `COMMANDS`:

| Command | Category | Special Handling |
|---------|----------|------------------|
| Memory Info | read | Auto-refresh capable |
| Brightness | read | Auto-refresh capable |
| GPIO Status | read | Auto-refresh capable |
| Interrupt Info | read | Auto-refresh capable |
| Serial Port Info | read | Standard |
| Audio Register Info | read | Standard |
| Get Events | streaming | Streaming output, Stop button |
| Unisoc Engineer Mode | action | Activity launch |
| MTK Engineer Mode | action | Activity launch |
| MTK DebugLogger | action | Activity launch |

### Streaming Output Support

- Real-time output streaming for `getevent -l`
- Line-by-line output display as events arrive
- Stop/Cancel button appears when streaming command is active
- Proper process termination when user stops streaming
- Visual indicator showing streaming is active

### Auto-Refresh/Polling Feature

- Toggle button on applicable command cards (memory info, brightness, GPIO status, interrupt info)
- Interval dropdown selector: 1s, 5s, 10s, 30s (default: 5s)
- Visual indicator when auto-refresh is active (pulsing dot or icon)
- Auto-refresh stops when:
  - User toggles it off
  - User switches to another command
  - Device disconnects
- Auto-refresh does NOT apply to streaming commands (they already provide real-time output)

### Export Functionality

- **Save to File**: Opens file save dialog, exports output as .txt file
- **Copy to Clipboard**: Copies current output to system clipboard
- Toolbar buttons in output area:
  - Save button with file icon
  - Copy button with clipboard icon
- Buttons disabled when no output exists

### Clear Output

- Clear button removes content from output area
- Also stops any active auto-refresh or streaming

### Command Execution State Feedback

- Running state: Spinner or pulsing indicator, card shows active styling
- Completed state: Success checkmark or green flash
- Error state: Red highlight with error message in output
- State labels in output toolbar: "Ready", "Running...", "Completed", "Error"

## Out Of Scope

- Command registry configuration file (Sprint 3)
- Keyboard shortcuts for save/copy (Sprint 3)
- Settings persistence (window size, last save directory) (Sprint 3)
- UI polish animations beyond functional states (Sprint 3)
- Application icon (Sprint 3)
- Parsed/formatted output views (non-goal per spec)

## Locked Assumptions

| Decision | Value |
|----------|-------|
| GUI Framework | PyQt6 |
| Python Version | 3.13.13 |
| Platform | Windows only |
| Theme | Dark theme (established in Sprint 1) |
| Device Model | Single connected device |
| Output Style | Terminal plain text |
| Auto-refresh Intervals | 1s, 5s, 10s, 30s |
| Auto-refresh Default | 5 seconds |
| Auto-refresh Capable Commands | Memory Info, Brightness, GPIO Status, Interrupt Info |

## Files Expected To Change

### Files to Modify

```
adb_dashboard/
    main_window.py           # Add auto-refresh logic, streaming handling, export triggers
    services/
        adb_service.py       # Add streaming execution, process management
    models/
        command.py           # Add auto_refresh_capable flag to Command model
    widgets/
        command_card.py      # Add auto-refresh toggle, interval selector, active indicator
        output_area.py       # Add Save, Copy, Stop buttons; state feedback
        status_indicator.py  # No changes expected
    styles.py                # Add styles for new UI elements
```

### New Files to Create

```
adb_dashboard/
    widgets/
        auto_refresh_controls.py  # Toggle switch and interval dropdown component
```

## Testable Behaviors

| # | Behavior | Verification |
|---|----------|--------------|
| 1 | All 10 command cards are clickable and enabled | Launch app with device connected, verify all cards respond to hover and click |
| 2 | Clicking "Audio Register Info" executes and shows output | Click card, verify `adb shell cat /sys/kernel/debug/mtksocaudio` executes, output displays |
| 3 | Clicking "Get Events" starts streaming output | Click card, verify events stream in real-time line-by-line |
| 4 | Stop button appears during streaming | When Get Events is running, verify Stop button is visible and enabled |
| 5 | Clicking Stop terminates streaming | During streaming, click Stop, verify process terminates and output stops |
| 6 | Auto-refresh toggle appears on Memory Info card | Verify toggle control is visible on Memory Info, Brightness, GPIO Status, Interrupt Info cards |
| 7 | Auto-refresh toggle does NOT appear on Get Events card | Verify toggle control is NOT visible on streaming commands |
| 8 | Enabling auto-refresh starts periodic execution | Toggle auto-refresh on Memory Info, verify output updates at selected interval |
| 9 | Auto-refresh interval selector works | Change interval from 5s to 1s, verify refresh rate changes |
| 10 | Auto-refresh stops when switching commands | Enable auto-refresh on Memory Info, click another command, verify auto-refresh stops |
| 11 | Auto-refresh stops when device disconnects | During auto-refresh, disconnect device, verify auto-refresh stops |
| 12 | Save button exports output to file | Execute a command, click Save, verify file dialog opens, save file, verify content matches output |
| 13 | Copy button copies output to clipboard | Execute a command, click Copy, paste in text editor, verify content matches output |
| 14 | Save/Copy buttons disabled when no output | On fresh launch or after Clear, verify Save and Copy buttons are disabled |
| 15 | Clear button removes output | Execute a command, click Clear, verify output area is empty |
| 16 | Execution state shows "Running..." during command | Execute any command, verify "Running..." status appears |
| 17 | Execution state shows "Completed" after success | After command completes successfully, verify "Completed" status |
| 18 | Execution state shows "Error" after failure | Disconnect device, execute command, verify "Error" status and message |
| 19 | Stop button terminates auto-refresh | Enable auto-refresh, click Stop, verify auto-refresh stops |
| 20 | Engineer Mode commands launch activities | Click Unisoc/MTK Engineer Mode or DebugLogger, verify activity launches on device |

## Runtime Assumptions

1. User has ADB installed and accessible via system PATH
2. User has Python 3.13.13 installed
3. User has PyQt6 installed
4. A single Android device may or may not be connected via USB
5. USB debugging is enabled on the connected device (if any)
6. For streaming commands, device generates events (e.g., touch, key presses)
7. For activity launch commands, the respective packages are installed on the device

## Technical Specifications

### StreamingCommandWorker (extends QThread)

```python
class StreamingCommandWorker(QThread):
    """Worker thread for streaming ADB commands like getevent -l."""

    line_received = pyqtSignal(str)  # Emits each line as received
    started_signal = pyqtSignal()
    stopped_signal = pyqtSignal()

    def __init__(self, shell_command: str, parent=None):
        super().__init__(parent)
        self.shell_command = shell_command
        self._process = None
        self._is_running = False

    def run(self):
        """Execute command and stream output line by line."""
        # Use subprocess.Popen for streaming
        # Read stdout line by line in loop
        # Emit line_received for each line

    def stop(self):
        """Terminate the streaming process."""
        # Terminate subprocess
        # Set _is_running = False
```

### AutoRefreshManager

```python
class AutoRefreshManager(QObject):
    """Manages auto-refresh polling for commands."""

    refresh_triggered = pyqtSignal()  # Emitted when refresh should occur

    def __init__(self, parent=None):
        self._timer = QTimer()
        self._interval_ms = 5000  # Default 5 seconds
        self._is_active = False

    def set_interval(self, seconds: int):
        """Set refresh interval in seconds."""

    def start(self):
        """Start auto-refresh timer."""

    def stop(self):
        """Stop auto-refresh timer."""

    def is_active(self) -> bool:
        """Return whether auto-refresh is active."""
```

### Command Model Extension

```python
@dataclass
class Command:
    id: str
    label: str
    shell_command: str
    is_clickable: bool
    category: str  # "read", "action", or "streaming"
    auto_refresh_capable: bool = False  # NEW: Whether auto-refresh applies
```

### OutputArea Toolbar Addition

```
+--------------------------------------------------+
| Output          [Running...]    [Save] [Copy] [Stop] [Clear] |
+--------------------------------------------------+
|                                                  |
|  (Terminal output area)                          |
|                                                  |
+--------------------------------------------------+
```

- Status label shows: Ready, Running..., Completed, Error
- Stop button only visible during streaming or auto-refresh
- Save/Copy disabled when no output content

### Auto-Refresh Controls Layout

```
+------------------------------------------+
| Memory Info                    [AR] [5s] |
| Read                            (*)      |
+------------------------------------------+
```

- [AR]: Toggle button for auto-refresh
- [5s]: Dropdown for interval selection
- (*): Pulsing indicator when active

### Color Additions

| Element | Color Code |
|---------|------------|
| Streaming Active | #ff9800 (amber) |
| Auto-Refresh Active | #00bcd4 (cyan) |
| Running State Text | #ff9800 (amber) |
| Completed State Text | #4caf50 (green) |

## Risks Or Notes

### Technical Risks

1. **Streaming process cleanup**: Must ensure subprocess is properly terminated when stopping `getevent -l` to avoid orphan processes. Use `process.terminate()` then `process.wait()` with timeout.

2. **Auto-refresh race conditions**: If auto-refresh triggers while previous command is still executing, must skip or queue appropriately. Recommend skipping and waiting for next interval.

3. **Clipboard access on Windows**: PyQt6 clipboard should work, but verify with `QApplication.clipboard()`.

4. **File save dialog blocking**: Use `QFileDialog.getSaveFileName()` which is modal but acceptable for this use case.

5. **Activity launch commands**: The `am start` commands may fail silently if package not installed. Capture stderr and display in output.

### Implementation Notes

1. **Streaming implementation**:
   - Use `subprocess.Popen` with `stdout=subprocess.PIPE`
   - Read lines in a loop using `process.stdout.readline()`
   - Check `isRunning()` flag between lines for stop request
   - Emit signals on the main thread via Qt's signal/slot mechanism

2. **Auto-refresh timing**:
   - Use `QTimer` with single-shot or repeating timeout
   - Store timer in MainWindow or dedicated manager
   - Stop timer when: user disables, command changes, device disconnects, app closes

3. **Button state management**:
   - Track output content state (`has_output: bool`)
   - Track execution state (`is_executing: bool`, `is_streaming: bool`, `is_auto_refreshing: bool`)
   - Update button enabled/visible states based on combined state

4. **Memory considerations**:
   - Streaming output can grow large; consider limiting buffered lines
   - Auto-refresh should replace output, not append

5. **Signal/slot connections**:
   - Use Qt signals for all async operations
   - Avoid calling UI methods directly from worker threads

### Edge Cases

1. **Rapid command switching**: If user clicks multiple commands quickly, cancel previous execution
2. **Device disconnect during streaming**: Detect via error output, stop streaming, update status
3. **Auto-refresh with no device**: Skip refresh, show error, stop auto-refresh
4. **Empty output**: Save/Copy should handle gracefully (save empty file, copy empty string)
5. **Special characters in output**: Ensure encoding handled with `errors='replace'`

### Deferred to Sprint 3

- Keyboard shortcuts (Ctrl+S for save, Ctrl+C for copy, Escape to stop)
- Settings persistence (remember last save directory, preferred refresh interval)
- Command registry config file
- UI polish (animations, hover states refinement)

## Acceptance Criteria Summary

- [ ] All 10 command cards are functional and clickable
- [ ] Get Events streams real-time output until stopped
- [ ] Stop button terminates streaming commands
- [ ] Auto-refresh toggle works on Memory Info, Brightness, GPIO Status, Interrupt Info
- [ ] Auto-refresh interval selector offers 1s, 5s, 10s, 30s options
- [ ] Auto-refresh stops when switching commands or device disconnects
- [ ] Save button exports output to user-selected file
- [ ] Copy button copies output to system clipboard
- [ ] Clear button removes output content
- [ ] Execution state feedback shows Running/Completed/Error
- [ ] UI remains responsive during all operations
