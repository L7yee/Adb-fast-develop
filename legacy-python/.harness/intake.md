# Product Intake

## Original Brief

User needs an ADB command desktop application (host computer software) with a simple interface where each command corresponds to a specific function:

| Command | Function |
|---------|----------|
| `adb shell cat /sys/kernel/debug/mtksocaudio` | Audio Register info |
| `cat /sys/class/leds/lcd-backlight/brightness` | Brightness |
| `cat /sys/kernel/debug/gpio` | Kernel GPIO allocation status |
| `cat /proc/meminfo` | Memory info |
| `cat /proc/interrupts` | Interrupt info |
| `cat /proc/tty/driver/serial` | Serial port info |
| `getevent -l` | Get events/keys/touch |
| `am start -n com.sprd.engineermode/.EngineerModeActivity` | Unisoc Engineer Mode |
| `am start com.mediatek.engineermode/com.mediatek.engineermode.EngineerMode` | MTK Engineer Mode |
| `am start com.debug.loggerui/com.debug.loggerui.MainActivity` | MTK User DebugLogger |

## Current Project Analysis

- This is a new project (no existing codebase).
- Target runtime: Desktop application for Windows.
- Core functionality: Execute ADB shell commands and display results.
- The brief specifies 10 distinct commands with clear functional labels.

## Clarification Questionnaire

### Product and Users

1. **Who are the primary users of this tool?** (e.g., firmware engineers, QA testers, field support, or all of the above?)

2. **What is the core user workflow?** Will users typically:
   - Run one command at a time for quick diagnostics?
   - Run multiple commands sequentially during debugging sessions?
   - Need to monitor output continuously (e.g., for `getevent -l` which streams events)?

3. **Is this MVP focused only on the 10 listed commands, or should the application be extensible for future commands?**

### Platform and UX

4. **What is your preferred UI style?**
   - Traditional desktop form with buttons/panels?
   - Modern dashboard with cards/tiles?
   - Compact single-window layout vs. multi-tab interface?

5. **How should command output be displayed?**
   - Plain text in a scrollable terminal-style area?
   - Formatted/parsed output (e.g., tables for memory info)?
   - Real-time streaming for commands like `getevent -l`?

### Device Connection Handling

6. **Will the tool need to handle multiple connected devices?** If yes, should users:
   - Select a device from a dropdown before running commands?
   - Run commands simultaneously on all connected devices?

7. **How should the tool behave if no device is connected or ADB is not available?**

### Data and Output

8. **Do you need data export functionality?** (e.g., save output to file, copy to clipboard, export logs for reports)

9. **Should any commands support auto-refresh or periodic polling?** (e.g., refresh memory info every 5 seconds)

### Stack and Infrastructure

10. **Is this Windows-only, or should it be cross-platform (macOS, Linux)?**

11. **Do you have any preferences for the technology stack?** (e.g., Electron, PyQt, WPF, WinForms, or no preference)

### Constraints and Non-Goals

12. **Are there any explicit non-goals for this version?** (e.g., no scripting support, no command customization, no history logging)

13. **Do you have a target delivery timeline or any deadline constraints?**

## User Clarifications

1. **Primary users**: Self for debugging purposes (personal debugging tool)

2. **Core workflow**: Run one command at a time

3. **Extensibility**: Should support future extension for additional commands

4. **UI style**: Modern card-style dashboard

5. **Output display**: Terminal-style plain text scrolling area

6. **Multiple devices**: Not supported (single device only)

7. **No device handling**: Display "Device not connected" prompt

8. **Export functionality**: Required (save output to file, copy to clipboard)

9. **Auto-refresh**: Required for certain commands (e.g., memory info, brightness)

10. **Platform**: Windows only

11. **Technology stack**: Python 3.13.13 (already installed), PyQt6 or CustomTkinter recommended

## Locked Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Target users | Personal debugging tool | Simplicity-focused, no multi-user concerns |
| Workflow | One command at a time | Direct execution model, no batch/queue |
| Extensibility | Architecture must support future commands | Plugin-style or command registry pattern |
| UI paradigm | Modern card-style dashboard | Visual clarity, extensible layout |
| Output format | Terminal-style plain text | Familiar to debug engineers, preserves raw output |
| Device handling | Single device, show error if disconnected | Simplest viable model |
| Export | Required (file save + clipboard) | Debug workflow needs to capture output |
| Platform | Windows only | No cross-platform overhead |
| Stack | Python 3.13 + PyQt6 | Modern Qt bindings, good ecosystem, user preference |
| Auto-refresh | Required for applicable commands | Enables periodic polling for monitoring |

## Open Questions

None - all clarification questions have been answered.
