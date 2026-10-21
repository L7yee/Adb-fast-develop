"""
Auto-refresh controls widget for ADB Debug Dashboard.

Provides toggle and interval selector for commands that support auto-refresh.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal

from ..services.adb_service import AutoRefreshManager


class AutoRefreshControls(QWidget):
    """
    Auto-refresh toggle and interval selector.

    Features:
    - Toggle button to enable/disable auto-refresh
    - Interval dropdown (1s, 5s, 10s, 30s)
    - Visual indicator when active
    """

    toggled = pyqtSignal(bool)  # Emitted when auto-refresh is toggled
    interval_changed = pyqtSignal(int)  # Emitted when interval changes

    # Color constants
    COLOR_INACTIVE = "#3d3d3d"
    COLOR_ACTIVE = "#00bcd4"  # Cyan for auto-refresh
    COLOR_TEXT = "#e0e0e0"
    COLOR_TEXT_INACTIVE = "#9e9e9e"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_active = False
        self._setup_ui()

    def _setup_ui(self):
        """Build the auto-refresh controls UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Toggle button
        self.toggle_button = QPushButton("AR")
        self.toggle_button.setFixedSize(32, 24)
        self.toggle_button.setToolTip("Toggle Auto-Refresh")
        self.toggle_button.clicked.connect(self._on_toggle_clicked)
        self._apply_toggle_style(False)
        layout.addWidget(self.toggle_button)

        # Interval dropdown
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1s", "5s", "10s", "30s"])
        self.interval_combo.setCurrentText("5s")  # Default
        self.interval_combo.setFixedSize(50, 24)
        self.interval_combo.setToolTip("Refresh Interval")
        self.interval_combo.currentTextChanged.connect(self._on_interval_changed)
        self.interval_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.COLOR_INACTIVE};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                color: {self.COLOR_TEXT};
                font-size: 11px;
                padding: 2px 4px;
            }}
            QComboBox:hover {{
                border-color: #5d5d5d;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2d2d2d;
                color: {self.COLOR_TEXT};
                selection-background-color: #3d3d3d;
            }}
        """)
        layout.addWidget(self.interval_combo)

        # Active indicator
        self.indicator = QLabel()
        self.indicator.setFixedSize(8, 8)
        self.indicator.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.indicator)

    def _apply_toggle_style(self, is_active: bool):
        """Apply styling to toggle button based on state."""
        if is_active:
            self.toggle_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.COLOR_ACTIVE};
                    border: 1px solid {self.COLOR_ACTIVE};
                    border-radius: 4px;
                    color: #000000;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #00d4e4;
                }}
            """)
        else:
            self.toggle_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.COLOR_INACTIVE};
                    border: 1px solid #4d4d4d;
                    border-radius: 4px;
                    color: {self.COLOR_TEXT_INACTIVE};
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #4d4d4d;
                    border-color: {self.COLOR_ACTIVE};
                    color: {self.COLOR_TEXT};
                }}
            """)

    def _apply_indicator_style(self, is_active: bool):
        """Apply styling to indicator based on state."""
        if is_active:
            self.indicator.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.COLOR_ACTIVE};
                    border-radius: 4px;
                }}
            """)
        else:
            self.indicator.setStyleSheet(f"""
                QLabel {{
                    background-color: transparent;
                    border-radius: 4px;
                }}
            """)

    def _on_toggle_clicked(self):
        """Handle toggle button click."""
        self._is_active = not self._is_active
        self._apply_toggle_style(self._is_active)
        self._apply_indicator_style(self._is_active)
        self.toggled.emit(self._is_active)

    def _on_interval_changed(self, text: str):
        """Handle interval selection change."""
        # Extract seconds from text (e.g., "5s" -> 5)
        seconds = int(text.rstrip('s'))
        self.interval_changed.emit(seconds)

    def set_active(self, active: bool):
        """Set the active state programmatically."""
        self._is_active = active
        self._apply_toggle_style(active)
        self._apply_indicator_style(active)

    def is_active(self) -> bool:
        """Get current active state."""
        return self._is_active

    def get_interval(self) -> int:
        """Get current interval in seconds."""
        text = self.interval_combo.currentText()
        return int(text.rstrip('s'))

    def set_interval(self, seconds: int):
        """Set interval programmatically."""
        text = f"{seconds}s"
        index = self.interval_combo.findText(text)
        if index >= 0:
            self.interval_combo.setCurrentIndex(index)
