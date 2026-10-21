"""
Add command dialog for ADB Debug Dashboard.

Allows users to dynamically add new ADB commands.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QWidget,
)
from PyQt6.QtCore import Qt


class AddCommandDialog(QDialog):
    """Dialog for adding a new ADB command."""

    # Color constants
    COLOR_BACKGROUND = "#2d2d2d"
    COLOR_INPUT_BG = "#1e1e1e"
    COLOR_TEXT = "#e0e0e0"
    COLOR_TEXT_SECONDARY = "#9e9e9e"
    COLOR_ACCENT = "#0078d4"
    COLOR_BUTTON = "#3d3d3d"
    COLOR_BUTTON_HOVER = "#4d4d4d"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Command")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Apply dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.COLOR_BACKGROUND};
            }}
            QLabel {{
                color: {self.COLOR_TEXT};
                font-size: 13px;
            }}
            QLineEdit, QComboBox {{
                background-color: {self.COLOR_INPUT_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {self.COLOR_ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.COLOR_INPUT_BG};
                color: {self.COLOR_TEXT};
                selection-background-color: {self.COLOR_ACCENT};
            }}
            QCheckBox {{
                color: {self.COLOR_TEXT};
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)

        # Command Label
        label_label = QLabel("Command Label:")
        layout.addWidget(label_label)

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("e.g., CPU Temperature")
        layout.addWidget(self.label_input)

        # Shell Command
        cmd_label = QLabel("ADB Shell Command:")
        layout.addWidget(cmd_label)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("e.g., cat /sys/class/thermal/thermal_zone0/temp")
        layout.addWidget(self.command_input)

        # Category
        category_label = QLabel("Command Type:")
        layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["read", "action", "streaming"])
        self.category_combo.setToolTip(
            "read: Standard command that returns output\n"
            "action: Launches an activity (no output expected)\n"
            "streaming: Continuous output like getevent"
        )
        layout.addWidget(self.category_combo)

        # Auto-refresh capable
        self.auto_refresh_checkbox = QCheckBox("Supports Auto-Refresh")
        self.auto_refresh_checkbox.setToolTip(
            "Enable for commands that show changing values\n"
            "(e.g., memory info, brightness)"
        )
        layout.addWidget(self.auto_refresh_checkbox)

        # Requires root
        self.root_checkbox = QCheckBox("Requires Root Access")
        self.root_checkbox.setToolTip(
            "Enable for commands that need root/su permission\n"
            "(e.g., reading debug files in /sys/kernel/debug)"
        )
        layout.addWidget(self.root_checkbox)

        # Spacer
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(80)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_BUTTON};
                color: {self.COLOR_TEXT};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.COLOR_BUTTON_HOVER};
            }}
        """)
        button_layout.addWidget(cancel_button)

        add_button = QPushButton("Add")
        add_button.setFixedWidth(80)
        add_button.clicked.connect(self._on_add_clicked)
        add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_ACCENT};
                color: white;
                border: 1px solid {self.COLOR_ACCENT};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1084d8;
            }}
        """)
        button_layout.addWidget(add_button)

        layout.addLayout(button_layout)

    def _on_add_clicked(self):
        """Validate and accept the dialog."""
        label = self.label_input.text().strip()
        command = self.command_input.text().strip()

        if not label:
            self.label_input.setFocus()
            return

        if not command:
            self.command_input.setFocus()
            return

        self.accept()

    def get_command_data(self) -> dict:
        """Get the command data from the dialog."""
        import re
        label = self.label_input.text().strip()
        # Generate ID from label (lowercase, replace spaces with underscores)
        cmd_id = re.sub(r'[^a-z0-9_]', '_', label.lower())
        cmd_id = re.sub(r'_+', '_', cmd_id).strip('_')

        return {
            'id': cmd_id,
            'label': label,
            'shell_command': self.command_input.text().strip(),
            'is_clickable': True,
            'category': self.category_combo.currentText(),
            'auto_refresh_capable': self.auto_refresh_checkbox.isChecked(),
            'requires_root': self.root_checkbox.isChecked()
        }
