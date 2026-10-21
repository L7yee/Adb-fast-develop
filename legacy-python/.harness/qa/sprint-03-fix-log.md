# Sprint 03 Fix Log

## Source QA Report
- report: `.harness/qa/sprint-03-qa-report.md`

## Fixes Applied

| Bug ID | Change | Files | Notes |
| --- | --- | --- | --- |
| BUG-001 | Removed incorrect `PenStyle` import from `PyQt6.QtGui` | `adb_dashboard/main.py` line 12 | In PyQt6, `PenStyle` is an enum at `PyQt6.QtCore.Qt.PenStyle`, not in `PyQt6.QtGui`. The code already correctly uses `Qt.PenStyle.NoPen` on line 49 via the existing `Qt` import from `QtCore`. The fix was to remove `PenStyle` from the QtGui import statement. |
| BUG-002 | Moved `QShortcut` import from `PyQt6.QtWidgets` to `PyQt6.QtGui` | `adb_dashboard/main_window.py` lines 10-22, 24 | In PyQt6, `QShortcut` is in `PyQt6.QtGui`, not `PyQt6.QtWidgets`. Removed `QShortcut` from the QtWidgets import block and added it to the QtGui import statement. |

## Deferred Or Unresolved Items
- None

## Verification Notes
- BUG-001: The import statement on line 12 of main.py now reads: `from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont`
- BUG-001: The `Qt` import from `PyQt6.QtCore` on line 13 provides access to `Qt.PenStyle.NoPen` which is used on line 49
- BUG-002: The QtWidgets import block no longer contains `QShortcut`
- BUG-002: The QtGui import statement now reads: `from PyQt6.QtGui import QKeySequence, QScreen, QShortcut`
- Application should now launch successfully without ImportError
