# Product Spec

## Approval Snapshot

- **product**: ADB Debug Dashboard - A Windows desktop application for executing ADB shell commands and viewing diagnostic output
- **locked architecture**: Python desktop application with PyQt6 GUI framework, modular command registry pattern for extensibility
- **locked stack**: Python 3.13.13 + PyQt6
- **total_sprints**: 3

## Overview

ADB Debug Dashboard is a lightweight Windows desktop application designed for firmware/engineer debugging workflows. It provides a modern card-style dashboard interface where each ADB command is presented as a clickable card. Users execute commands one at a time and view results in a terminal-style text output area.

The application targets personal debugging use cases, prioritizing simplicity and speed over multi-user or multi-device features. Output can be exported to file or clipboard for documentation purposes.

## Goals

1. **Single-command execution**: Provide a clean interface to execute any of the 10 predefined ADB commands with one click
2. **Clear output display**: Show command output in a terminal-style scrolling text area that preserves raw output format
3. **Extensible architecture**: Design a command registry system that allows future commands to be added without core UI changes
4. **Error handling**: Gracefully handle disconnected devices and ADB unavailability with clear user feedback
5. **Export capability**: Allow users to save output to file or copy to clipboard
6. **Auto-refresh/polling**: Enable periodic command execution for monitoring dynamic values (e.g., memory info, brightness)
7. **Modern UX**: Deliver a card-style dashboard that feels contemporary and is easy to navigate

## Non-Goals

1. **Multi-device support**: No device selection, serial management, or parallel execution across devices
2. **Cross-platform support**: Windows-only; no macOS or Linux support
3. **Batch execution**: No queuing or running multiple commands in sequence
4. **Command customization**: Users cannot add, edit, or remove commands through the UI (only through code/config extension)
5. **History logging**: No persistent command history or output log database
6. **Parsed output formatting**: Output is displayed as raw text; no table parsing or structured views

## Locked Decisions

| Decision | Value |
|----------|-------|
| GUI Framework | PyQt6 |
| Python Version | 3.13.13 |
| Platform | Windows only |
| Device Model | Single connected device |
| UI Pattern | Card-style dashboard |
| Output Style | Terminal plain text |
| Export Methods | Save to file, Copy to clipboard |
| Extensibility | Command registry pattern (code-level extension) |
| Auto-refresh | Supported for applicable commands with configurable interval |

## Sprint Plan

### Sprint 1: Core Shell

**Theme**: Application foundation and ADB integration

**Outcomes**:
- PyQt6 application scaffold with main window
- ADB service layer that can:
  - Detect connected device
  - Execute shell commands via `adb shell`
  - Handle connection errors gracefully
- Device status indicator in UI header
- Basic card layout displaying all 10 commands
- Click-to-execute for a subset of commands (5 simple read commands)
- Output display area showing command results

**Acceptance Criteria**:
- App launches and shows device connection status
- Clicking a command card executes the ADB command
- Output appears in the text area
- "Device not connected" message shows when appropriate

### Sprint 2: Full Command Support and Output

**Theme**: Complete all 10 commands, output handling, and auto-refresh

**Outcomes**:
- All 10 commands implemented and functional
- Streaming output support for `getevent -l` (real-time event capture)
- Stop/cancel button for streaming commands
- Auto-refresh/polling feature:
  - Toggle button on applicable command cards (memory info, brightness, etc.)
  - Configurable refresh interval (dropdown: 1s, 5s, 10s, 30s)
  - Visual indicator when auto-refresh is active
  - Auto-refresh stops when switching to another command
- Export functionality:
  - Save output to text file
  - Copy output to clipboard
- Clear output button
- Command execution state feedback (running, completed, error)

**Acceptance Criteria**:
- All 10 command cards are functional
- `getevent -l` streams events until user stops it
- User can enable auto-refresh on supported commands
- Auto-refresh updates output at the selected interval
- User can save any output to a file
- User can copy output to clipboard
- UI shows clear feedback during command execution

### Sprint 3: Polish and Extensibility

**Theme**: User experience refinement and extension scaffolding

**Outcomes**:
- Command registry system with JSON/YAML config file for command definitions
- UI polish: consistent styling, proper spacing, hover states
- Keyboard shortcuts for common actions (e.g., Ctrl+S to save)
- Error message improvements with actionable guidance
- Application icon and window title
- Settings persistence (window size, last used directory for save)
- Documentation comment block explaining how to add new commands

**Acceptance Criteria**:
- Commands can be added by editing a config file without code changes
- UI feels polished and responsive
- App remembers window size between sessions
- Clear documentation for extending commands

## Acceptance Notes

1. **Device Detection**: The app should check device status on startup and provide a refresh button to re-check
2. **Streaming Commands**: For `getevent -l`, implement proper process termination when user clicks stop
3. **Output Encoding**: Handle UTF-8 and common encoding issues from ADB output
4. **Error Messages**: Show specific errors (device not found, ADB not installed, permission denied, etc.)
5. **Config File**: Use a readable format (YAML preferred) for the command registry
6. **No Admin Requirement**: App should run without administrator privileges
7. **Auto-refresh Behavior**: Auto-refresh should stop automatically when: switching to another command, device disconnects, or user manually stops it. Commands suitable for auto-refresh: memory info, brightness, GPIO status, interrupt info.
