"""
Status indicator widget for ADB Debug Dashboard.

Shows device connection status with colored indicator.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

from ..services.adb_service import DeviceStatus


class StatusIndicator(QWidget):
    """
    Device status indicator with colored dot and label.

    States:
    - Connected: Green dot with device ID
    - Disconnected: Gray dot with "Disconnected"
    - Error: Red dot with error message
    """

    # Color constants
    COLOR_CONNECTED = "#4caf50"
    COLOR_DISCONNECTED = "#9e9e9e"
    COLOR_ERROR = "#f44336"
    COLOR_CHECKING = "#ff9800"  # Amber for checking
    COLOR_TEXT = "#e0e0e0"
    COLOR_TEXT_SECONDARY = "#9e9e9e"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._status = DeviceStatus.DISCONNECTED
        self._message = ""
        self._setup_ui()

    def _setup_ui(self):
        """Build the status indicator UI layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Status dot (colored circle)
        self.dot = QLabel()
        self.dot.setFixedSize(12, 12)
        self.dot.setStyleSheet(f"""
            QLabel {{
                background-color: {self.COLOR_DISCONNECTED};
                border-radius: 6px;
            }}
        """)
        layout.addWidget(self.dot)

        # Status label
        self.label = QLabel("Disconnected")
        self.label.setObjectName("statusLabel")
        layout.addWidget(self.label)

    def set_status(self, status: str, message: str = ""):
        """
        Update the status indicator.

        Args:
            status: "connected", "disconnected", or "error"
            message: Optional message to display
        """
        self._status = status
        self._message = message

        if status == "connected":
            self.dot.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.COLOR_CONNECTED};
                    border-radius: 6px;
                }}
            """)
            display_text = message if message else "Connected"
            self.label.setText(display_text)
            self.label.setStyleSheet(f"""
                QLabel {{
                    color: {self.COLOR_CONNECTED};
                    font-size: 12px;
                }}
            """)

        elif status == "disconnected":
            self.dot.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.COLOR_DISCONNECTED};
                    border-radius: 6px;
                }}
            """)
            self.label.setText("Disconnected")
            self.label.setStyleSheet(f"""
                QLabel {{
                    color: {self.COLOR_TEXT_SECONDARY};
                    font-size: 12px;
                }}
            """)

        elif status == "error":
            self.dot.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.COLOR_ERROR};
                    border-radius: 6px;
                }}
            """)
            display_text = message if message else "Error"
            self.label.setText(display_text)
            self.label.setStyleSheet(f"""
                QLabel {{
                    color: {self.COLOR_ERROR};
                    font-size: 12px;
                }}
            """)

        elif status == "checking":
            self.dot.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.COLOR_CHECKING};
                    border-radius: 6px;
                }}
            """)
            display_text = message if message else "Checking..."
            self.label.setText(display_text)
            self.label.setStyleSheet(f"""
                QLabel {{
                    color: {self.COLOR_CHECKING};
                    font-size: 12px;
                }}
            """)

    def get_status(self) -> str:
        """Get the current status."""
        return self._status
