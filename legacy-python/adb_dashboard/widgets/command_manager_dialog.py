"""
Command manager dialog for ADB Debug Dashboard.

Allows users to view, edit, and delete commands.
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
    QListWidget,
    QListWidgetItem,
    QWidget,
    QMessageBox,
    QSplitter,
)
from PyQt6.QtCore import Qt
from typing import List, Optional


class CommandManagerDialog(QDialog):
    """Dialog for managing commands (view, edit, delete)."""

    # Color constants
    COLOR_BACKGROUND = "#2d2d2d"
    COLOR_INPUT_BG = "#1e1e1e"
    COLOR_TEXT = "#e0e0e0"
    COLOR_TEXT_SECONDARY = "#9e9e9e"
    COLOR_ACCENT = "#0078d4"
    COLOR_BUTTON = "#3d3d3d"
    COLOR_BUTTON_HOVER = "#4d4d4d"
    COLOR_DELETE = "#c62828"

    def __init__(self, commands: List, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Commands")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        self._commands = commands
        self._current_command = None
        self._deleted_ids = set()
        self._modified_commands = {}
        self._is_adding_new = False  # Track if we're adding a new command
        self._setup_ui()

    def _setup_ui(self):
        """Build the dialog UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

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
            QListWidget {{
                background-color: {self.COLOR_INPUT_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 8px;
            }}
            QListWidget::item:selected {{
                background-color: {self.COLOR_ACCENT};
            }}
            QListWidget::item:hover {{
                background-color: #3d3d3d;
            }}
        """)

        # Left panel: Command list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)

        list_label = QLabel("Commands:")
        left_layout.addWidget(list_label)

        self.command_list = QListWidget()
        self.command_list.currentRowChanged.connect(self._on_command_selected)
        left_layout.addWidget(self.command_list)

        # Add new button
        add_btn = QPushButton("+ Add New")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_ACCENT};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1084d8;
            }}
        """)
        add_btn.clicked.connect(self._on_add_new)
        left_layout.addWidget(add_btn)

        # Right panel: Edit form
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)

        edit_label = QLabel("Edit Command:")
        right_layout.addWidget(edit_label)

        # Label
        label_label = QLabel("Label:")
        right_layout.addWidget(label_label)
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Display name")
        right_layout.addWidget(self.label_input)

        # Shell Command
        cmd_label = QLabel("ADB Shell Command:")
        right_layout.addWidget(cmd_label)
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("e.g., cat /proc/meminfo")
        right_layout.addWidget(self.command_input)

        # Category
        category_label = QLabel("Command Type:")
        right_layout.addWidget(category_label)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["read", "action", "streaming"])
        right_layout.addWidget(self.category_combo)

        # Checkboxes
        self.auto_refresh_checkbox = QCheckBox("Supports Auto-Refresh")
        right_layout.addWidget(self.auto_refresh_checkbox)

        self.root_checkbox = QCheckBox("Requires Root Access")
        right_layout.addWidget(self.root_checkbox)

        right_layout.addStretch()

        # Action buttons
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_ACCENT};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #1084d8;
            }}
            QPushButton:disabled {{
                background-color: #3d3d3d;
                color: #5d5d5d;
            }}
        """)
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setEnabled(False)
        btn_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_DELETE};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #e53935;
            }}
            QPushButton:disabled {{
                background-color: #3d3d3d;
                color: #5d5d5d;
            }}
        """)
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)

        right_layout.addLayout(btn_layout)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_BUTTON};
                color: {self.COLOR_TEXT};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.COLOR_BUTTON_HOVER};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        right_layout.addWidget(close_btn)

        # Add panels to splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 450])

        layout.addWidget(splitter)

        # Populate list
        self._populate_list()

    def _populate_list(self):
        """Populate the command list."""
        self.command_list.clear()
        for cmd in self._commands:
            if cmd.id not in self._deleted_ids:
                item = QListWidgetItem(cmd.label)
                item.setData(Qt.ItemDataRole.UserRole, cmd.id)
                self.command_list.addItem(item)

    def _on_command_selected(self, row: int):
        """Handle command selection."""
        if row < 0:
            self._clear_form()
            return

        # Reset adding new state when selecting existing command
        self._is_adding_new = False
        self.save_btn.setText("Save Changes")

        item = self.command_list.item(row)
        cmd_id = item.data(Qt.ItemDataRole.UserRole)

        # Find command
        cmd = None
        for c in self._commands:
            if c.id == cmd_id:
                cmd = c
                break

        if not cmd:
            return

        self._current_command = cmd

        # Check if we have modified version
        if cmd_id in self._modified_commands:
            modified = self._modified_commands[cmd_id]
            self.label_input.setText(modified.get('label', cmd.label))
            self.command_input.setText(modified.get('shell_command', cmd.shell_command))
            self.category_combo.setCurrentText(modified.get('category', cmd.category))
            self.auto_refresh_checkbox.setChecked(modified.get('auto_refresh_capable', cmd.auto_refresh_capable))
            self.root_checkbox.setChecked(modified.get('requires_root', cmd.requires_root))
        else:
            self.label_input.setText(cmd.label)
            self.command_input.setText(cmd.shell_command)
            self.category_combo.setCurrentText(cmd.category)
            self.auto_refresh_checkbox.setChecked(cmd.auto_refresh_capable)
            self.root_checkbox.setChecked(cmd.requires_root)

        self.save_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def _clear_form(self):
        """Clear the edit form."""
        self.label_input.clear()
        self.command_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.auto_refresh_checkbox.setChecked(False)
        self.root_checkbox.setChecked(False)
        self.save_btn.setEnabled(False)
        self.save_btn.setText("Save Changes")
        self.delete_btn.setEnabled(False)
        self._current_command = None
        self._is_adding_new = False

    def _on_save(self):
        """Save changes to current command or add new command."""
        import re

        label = self.label_input.text().strip()
        command = self.command_input.text().strip()

        if not label or not command:
            QMessageBox.warning(self, "Warning", "Label and command are required.")
            return

        if self._is_adding_new:
            # Adding a new command
            cmd_id = re.sub(r'[^a-z0-9_]', '_', label.lower())
            cmd_id = re.sub(r'_+', '_', cmd_id).strip('_')

            # Check for duplicate
            existing_ids = {c.id for c in self._commands}
            if cmd_id in existing_ids or cmd_id in self._deleted_ids:
                # Make unique
                counter = 1
                while f"{cmd_id}_{counter}" in existing_ids:
                    counter += 1
                cmd_id = f"{cmd_id}_{counter}"

            # Add to modified commands (as new)
            self._modified_commands[cmd_id] = {
                'id': cmd_id,
                'label': label,
                'shell_command': command,
                'category': self.category_combo.currentText(),
                'auto_refresh_capable': self.auto_refresh_checkbox.isChecked(),
                'requires_root': self.root_checkbox.isChecked(),
                'is_new': True
            }

            # Add to list
            item = QListWidgetItem(label + " (new)")
            item.setData(Qt.ItemDataRole.UserRole, cmd_id)
            self.command_list.addItem(item)
            self.command_list.setCurrentRow(self.command_list.count() - 1)

            # Reset adding new state
            self._is_adding_new = False
            self.save_btn.setText("Save Changes")
            self.delete_btn.setEnabled(True)

            QMessageBox.information(self, "Added", f"New command '{label}' added. Click 'Close' to apply all changes.")
            return

        # Saving existing command
        if not self._current_command:
            return

        # Store modification
        self._modified_commands[self._current_command.id] = {
            'label': label,
            'shell_command': command,
            'category': self.category_combo.currentText(),
            'auto_refresh_capable': self.auto_refresh_checkbox.isChecked(),
            'requires_root': self.root_checkbox.isChecked()
        }

        # Update list item text
        current_row = self.command_list.currentRow()
        item = self.command_list.item(current_row)
        item.setText(label)

        QMessageBox.information(self, "Saved", f"Changes saved for '{label}'")

    def _on_delete(self):
        """Delete current command."""
        if not self._current_command:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete command '{self._current_command.label}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._deleted_ids.add(self._current_command.id)
            self._populate_list()
            self._clear_form()

    def _on_add_new(self):
        """Prepare form for adding a new command."""
        self._is_adding_new = True
        self._current_command = None

        # Clear the form for new entry
        self.label_input.clear()
        self.command_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.auto_refresh_checkbox.setChecked(False)
        self.root_checkbox.setChecked(False)

        # Clear selection in list
        self.command_list.clearSelection()

        # Enable save button for new command
        self.save_btn.setEnabled(True)
        self.save_btn.setText("Add Command")
        self.delete_btn.setEnabled(False)

        # Focus on label input
        self.label_input.setFocus()

    def get_changes(self) -> dict:
        """Get all changes made."""
        return {
            'deleted_ids': self._deleted_ids.copy(),
            'modified_commands': self._modified_commands.copy()
        }
