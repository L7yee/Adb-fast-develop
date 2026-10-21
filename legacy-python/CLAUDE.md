# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ADB Debug Dashboard is a Windows desktop application for executing ADB shell commands on connected Android devices. Built with Python 3.13 and PyQt6, it provides a modern card-style dashboard interface for common ADB debugging workflows.

## Running the Application

```bash
# From the project root (E:\workplace\adb_dashboard)
py run.py

# Or run directly
py -m adb_dashboard.main
```

## Architecture

### Layered Architecture

```
main.py              # Application entry point, icon setup, exception handling
main_window.py       # MainWindow orchestrating all UI components
widgets/             # UI components (cards, dialogs, controls)
services/            # Business logic (ADB, config, settings)
models/              # Data structures (Command)
config/              # YAML configuration files
```

### Key Components

- **MainWindow** (`main_window.py`): Central orchestrator handling device status, command execution, auto-refresh, compare mode, and keyboard shortcuts. Uses two-panel layout with command cards on left and output area on right.

- **ADBService** (`services/adb_service.py`): Handles device detection, command execution (async via QThread workers), streaming commands, auto-refresh polling, and root access detection.

- **ConfigService** (`services/config_service.py`): Loads and validates command definitions from `config/commands.yaml`.

- **SettingsService** (`services/settings_service.py`): Persists user preferences (window geometry, file paths) to `config/settings.yaml`.

### Widget Hierarchy

- **CommandCard**: Clickable card for each ADB command with auto-refresh controls, drag-drop reordering, and keyboard shortcuts (Ctrl+1 through Ctrl+0)
- **OutputArea**: Terminal-style output display with save/copy/stop/clear toolbar and Ctrl+wheel zoom
- **StatusIndicator**: Device connection status with colored dot
- **CommandManagerDialog**: Add/edit/delete commands UI
- **AutoRefreshControls**: Toggle and interval selector (1s, 5s, 10s, 30s)

### Command Categories

- **read**: Standard commands that return output immediately (e.g., `cat /proc/meminfo`)
- **streaming**: Continuous real-time output (e.g., `getevent -l`, `dmesg -w`)
- **action**: Launches activities, no output expected (e.g., `am start ...`)

### Configuration Files

- `config/commands.yaml`: Command definitions with id, label, shell_command, category, auto_refresh_capable, requires_root
- `config/settings.yaml`: Window geometry and file path persistence

## Key Patterns

### Async Command Execution

Commands run in QThread workers to prevent UI blocking:
- `CommandWorker`: Standard commands with 30s timeout
- `StreamingCommandWorker`: Continuous output via `readline()`
- `DeviceCheckWorker`: Non-blocking device status checks

### Signal-Based Communication

UI components communicate via PyQt signals:
- `clicked`: Command card execution
- `auto_refresh_toggled`: Auto-refresh state change
- `device_check_finished`: Async device status result
- `clear_requested`/`stop_requested`: Output area controls

### Error Handling

`ErrorMessage` class provides actionable guidance for common ADB errors (device not found, unauthorized, permission denied, etc.) with resolution steps.

## Dependencies

- Python 3.13
- PyQt6
- PyYAML

## Development Notes

- Dark theme colors defined in `styles.py` and widget constants
- Window geometry persists across sessions via SettingsService
- Commands can be reordered via drag-drop in "Reorder" mode
- Compare mode highlights differences between consecutive command outputs
- APK installation supports `--bypass-low-target-sdk-block` for deprecated SDK versions
