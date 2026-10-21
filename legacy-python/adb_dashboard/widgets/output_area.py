"""
Output area widget for ADB Debug Dashboard.

A terminal-style text area for displaying command output with toolbar.
Supports save/copy functionality with directory persistence.
"""

import os
import logging
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QSizePolicy,
    QFileDialog,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QWheelEvent

# Debug flag for zoom functionality
DEBUG_ZOOM = True

logger = logging.getLogger(__name__)


class ZoomableTextEdit(QTextEdit):
    """QTextEdit with Ctrl+wheel zoom support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._font_size = 13  # Track font size explicitly
        self._min_font_size = 8
        self._max_font_size = 32
        # Store style properties
        self._bg_color = "#0d0d0d"
        self._text_color = "#c0c0c0"
        self._border_color = "#3d3d3d"
        # Apply initial style
        self._apply_style()
        if DEBUG_ZOOM:
            logger.info(f"ZoomableTextEdit initialized, font_size={self._font_size}")

    def _apply_style(self):
        """Apply the current style with font size."""
        style = f"""QTextEdit {{
            background-color: {self._bg_color};
            color: {self._text_color};
            font-size: {self._font_size}px;
            font-family: 'Consolas', 'Courier New', monospace;
            border: 1px solid {self._border_color};
            border-radius: 4px;
            padding: 8px;
        }}"""
        super().setStyleSheet(style)
        if DEBUG_ZOOM:
            logger.info(f"Applied style with font_size={self._font_size}")

    def setStyleSheet(self, style: str):
        """Override setStyleSheet to extract colors and re-apply with font size."""
        # Extract colors from the provided stylesheet
        import re

        # Parse background-color
        bg_match = re.search(r'background-color:\s*([^;]+);', style)
        if bg_match:
            self._bg_color = bg_match.group(1).strip()

        # Parse color (text color)
        color_match = re.search(r'(?<!background-)color:\s*([^;]+);', style)
        if color_match:
            self._text_color = color_match.group(1).strip()

        # Parse border color
        border_match = re.search(r'border:\s*\d+px\s+solid\s+([^;]+);', style)
        if border_match:
            self._border_color = border_match.group(1).strip()

        # Re-apply style with current font size
        self._apply_style()

        if DEBUG_ZOOM:
            logger.info(f"setStyleSheet: extracted bg={self._bg_color}, color={self._text_color}, font_size={self._font_size}")

    def wheelEvent(self, event: QWheelEvent):
        """Handle wheel event with Ctrl+zoom support."""
        modifiers = event.modifiers()

        if DEBUG_ZOOM:
            logger.info(f"wheelEvent triggered, modifiers={modifiers}, Ctrl={bool(modifiers & Qt.KeyboardModifier.ControlModifier)}, delta={event.angleDelta().y()}")

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+wheel: zoom font
            delta = event.angleDelta().y()

            if delta > 0:
                new_size = min(self._font_size + 1, self._max_font_size)
            else:
                new_size = max(self._font_size - 1, self._min_font_size)

            if DEBUG_ZOOM:
                logger.info(f"Ctrl+wheel detected: delta={delta}, old_size={self._font_size}, new_size={new_size}")

            if new_size != self._font_size:
                self._font_size = new_size
                self._apply_style()
            # Accept the event to prevent further processing
            event.accept()
        else:
            # Normal scroll
            super().wheelEvent(event)

    def setFont(self, font: QFont):
        """Override setFont to track font size."""
        super().setFont(font)
        # Update tracked size from font
        if font.pointSize() > 0:
            self._font_size = font.pointSize()

    def setFontSize(self, size: int):
        """Set the font size."""
        size = max(self._min_font_size, min(size, self._max_font_size))
        self._font_size = size
        self._apply_font()

    def getFontSize(self) -> int:
        """Get the current font size."""
        return self._font_size


class OutputArea(QWidget):
    """
    Output display area with terminal-style text area.

    Features:
    - Monospace font for terminal aesthetic
    - Dark background
    - Read-only text display
    - Toolbar with Save, Copy, Stop, Clear buttons
    - Execution state feedback (Ready, Running, Completed, Error)
    - Save directory persistence via settings service
    """

    clear_requested = pyqtSignal()  # Emitted when user clicks clear
    stop_requested = pyqtSignal()   # Emitted when user clicks stop

    # Color constants
    COLOR_BACKGROUND = "#1e1e1e"
    COLOR_OUTPUT_BG = "#0d0d0d"
    COLOR_TEXT = "#c0c0c0"
    COLOR_STATUS = "#9e9e9e"
    COLOR_ERROR = "#f44336"
    COLOR_RUNNING = "#ff9800"  # Amber
    COLOR_COMPLETED = "#4caf50"  # Green
    COLOR_TOOLBAR_BG = "#2d2d2d"
    COLOR_BUTTON = "#3d3d3d"
    COLOR_BUTTON_HOVER = "#4d4d4d"
    COLOR_BUTTON_DISABLED = "#2d2d2d"
    COLOR_BUTTON_TEXT = "#e0e0e0"
    COLOR_BUTTON_TEXT_DISABLED = "#5d5d5d"

    def __init__(self, settings_service=None, parent=None):
        super().__init__(parent)
        self._has_output = False
        self._current_state = "ready"  # ready, running, completed, error
        self._settings_service = settings_service
        self._setup_ui()

    def _setup_ui(self):
        """Build the output area UI layout."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QWidget()
        toolbar.setObjectName("outputToolbar")
        toolbar.setStyleSheet(f"background-color: {self.COLOR_TOOLBAR_BG};")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(12)

        # Output label
        output_label = QLabel("Output")
        output_label.setStyleSheet(f"""
            QLabel {{
                color: #e0e0e0;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }}
        """)
        toolbar_layout.addWidget(output_label)

        # State label
        self.state_label = QLabel("Ready")
        self.state_label.setObjectName("stateLabel")
        self._apply_state_style("ready")
        toolbar_layout.addWidget(self.state_label)

        toolbar_layout.addStretch()

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Save output to file (Ctrl+S)")
        self.save_button.setFixedWidth(70)
        self.save_button.clicked.connect(self._on_save_clicked)
        self._apply_button_style(self.save_button, enabled=False)
        toolbar_layout.addWidget(self.save_button)

        # Copy button
        self.copy_button = QPushButton("Copy")
        self.copy_button.setToolTip("Copy output to clipboard (Ctrl+C)")
        self.copy_button.setFixedWidth(70)
        self.copy_button.clicked.connect(self._on_copy_clicked)
        self._apply_button_style(self.copy_button, enabled=False)
        toolbar_layout.addWidget(self.copy_button)

        # Stop button (initially hidden)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setToolTip("Stop current operation (Escape)")
        self.stop_button.setFixedWidth(70)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self._apply_stop_button_style(enabled=True)
        self.stop_button.setVisible(False)
        toolbar_layout.addWidget(self.stop_button)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setToolTip("Clear output")
        self.clear_button.setFixedWidth(70)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        self._apply_button_style(self.clear_button, enabled=True)
        toolbar_layout.addWidget(self.clear_button)

        layout.addWidget(toolbar)

        # Output text area (with Ctrl+wheel zoom support)
        self.text_area = ZoomableTextEdit()
        self.text_area.setObjectName("outputText")
        self.text_area.setReadOnly(True)
        self.text_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Set focus policy for keyboard shortcuts
        self.text_area.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Set monospace font
        font = QFont("Consolas", 13)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_area.setFont(font)

        # Set size policy
        self.text_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        layout.addWidget(self.text_area)

    def _apply_button_style(self, button: QPushButton, enabled: bool):
        """Apply styling to toolbar button with hover and pressed states."""
        if enabled:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.COLOR_BUTTON};
                    border: 1px solid #4d4d4d;
                    border-radius: 4px;
                    color: {self.COLOR_BUTTON_TEXT};
                    font-size: 12px;
                    padding: 4px 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.COLOR_BUTTON_HOVER};
                    border-color: #5d5d5d;
                }}
                QPushButton:pressed {{
                    background-color: #0078d4;
                    border-color: #0078d4;
                }}
                QPushButton:focus {{
                    border-color: #0078d4;
                    outline: none;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.COLOR_BUTTON_DISABLED};
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    color: {self.COLOR_BUTTON_TEXT_DISABLED};
                    font-size: 12px;
                    padding: 4px 8px;
                }}
            """)
        button.setEnabled(enabled)

    def _apply_stop_button_style(self, enabled: bool):
        """Apply styling to stop button (always visible when shown)."""
        if enabled:
            self.stop_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #c62828;
                    border: 1px solid #e53935;
                    border-radius: 4px;
                    color: {self.COLOR_BUTTON_TEXT};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 4px 8px;
                }}
                QPushButton:hover {{
                    background-color: #e53935;
                    border-color: #f44336;
                }}
                QPushButton:pressed {{
                    background-color: #b71c1c;
                }}
            """)
        self.stop_button.setEnabled(enabled)

    def _apply_state_style(self, state: str):
        """Apply styling to state label based on state."""
        styles = {
            "ready": ("Ready", "#9e9e9e"),
            "running": ("Running...", "#ff9800"),
            "streaming": ("Streaming...", "#ff9800"),
            "auto_refresh": ("Auto-Refresh", "#00bcd4"),
            "completed": ("Completed", "#4caf50"),
            "error": ("Error", "#f44336"),
        }
        text, color = styles.get(state, ("Ready", "#9e9e9e"))
        self.state_label.setText(text)
        self.state_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                padding: 2px 8px;
                border: 1px solid {color};
                border-radius: 10px;
            }}
        """)

    def _update_button_states(self):
        """Update button enabled states based on output content."""
        self._apply_button_style(self.save_button, self._has_output)
        self._apply_button_style(self.copy_button, self._has_output)

    def show_output(self, output: str, command_label: str = "", shell_command: str = ""):
        """Display command output in the text area, appending to history."""
        # Add separator and timestamp for new command
        from datetime import datetime
        from PyQt6.QtGui import QTextCharFormat
        timestamp = datetime.now().strftime("%H:%M:%S")

        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Reset to normal format (clear any previous formatting)
        normal_format = QTextCharFormat()
        cursor.setCharFormat(normal_format)

        # Add separator if there's existing content
        if self._has_output:
            cursor.insertText("\n" + "="*60 + "\n")

        # Add command header
        if command_label:
            cursor.insertText(f"[{timestamp}] {command_label}\n")
            # Show the full adb shell command
            if shell_command:
                cursor.insertText(f"adb shell {shell_command}\n")
            cursor.insertText("-"*60 + "\n")

        cursor.insertText(output + "\n")
        self.text_area.setTextCursor(cursor)

        self._has_output = True
        self._update_button_states()
        # Scroll to bottom to show latest output
        self.text_area.ensureCursorVisible()

    def show_compare_output(self, prev_output: str, curr_output: str, command_label: str = "", shell_command: str = ""):
        """Display comparison between previous and current output with highlighted changes."""
        import difflib
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Add separator if there's existing content
        if self._has_output:
            cursor.insertText("\n" + "="*60 + "\n")

        # Add command header
        if command_label:
            cursor.insertText(f"[{timestamp}] {command_label} (COMPARE)\n")
            if shell_command:
                cursor.insertText(f"adb shell {shell_command}\n")
            cursor.insertText("-"*60 + "\n")

        # Compare line by line
        prev_lines = prev_output.splitlines()
        curr_lines = curr_output.splitlines()

        # Use SequenceMatcher for better diff
        matcher = difflib.SequenceMatcher(None, prev_lines, curr_lines)

        from PyQt6.QtGui import QTextCharFormat, QColor

        added_format = QTextCharFormat()
        added_format.setBackground(QColor("#1b5e20"))  # Dark green background
        added_format.setForeground(QColor("#4caf50"))  # Green text

        removed_format = QTextCharFormat()
        removed_format.setBackground(QColor("#4a1a1a"))  # Dark red background
        removed_format.setForeground(QColor("#f44336"))  # Red text

        added_count = 0
        removed_count = 0

        # Only show changed lines
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Lines were replaced - show removed and added
                for line in prev_lines[i1:i2]:
                    cursor.insertText("- ", removed_format)
                    cursor.insertText(line + "\n", removed_format)
                    removed_count += 1
                for line in curr_lines[j1:j2]:
                    cursor.insertText("+ ", added_format)
                    cursor.insertText(line + "\n", added_format)
                    added_count += 1
            elif tag == 'delete':
                # Lines were removed
                for line in prev_lines[i1:i2]:
                    cursor.insertText("- ", removed_format)
                    cursor.insertText(line + "\n", removed_format)
                    removed_count += 1
            elif tag == 'insert':
                # Lines were added
                for line in curr_lines[j1:j2]:
                    cursor.insertText("+ ", added_format)
                    cursor.insertText(line + "\n", added_format)
                    added_count += 1
            # 'equal' tags are skipped - don't show unchanged lines

        # Add summary
        cursor.insertText("-"*60 + "\n")
        if added_count or removed_count:
            cursor.insertText(f"[Compare] {added_count} added, {removed_count} removed\n")
        else:
            cursor.insertText("[Compare] No changes detected\n")

        self.text_area.setTextCursor(cursor)
        self._has_output = True
        self._update_button_states()
        self.text_area.ensureCursorVisible()

    def append_output(self, text: str):
        """Append text to the output area (for streaming)."""
        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text + "\n")
        self.text_area.setTextCursor(cursor)
        self._has_output = True
        self._update_button_states()
        # Auto-scroll to bottom for streaming
        self.text_area.ensureCursorVisible()

    def show_status(self, message: str):
        """Show a status message (e.g., "Executing...")."""
        self.text_area.setPlainText(message)
        self._has_output = False
        self._update_button_states()
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.COLOR_OUTPUT_BG};
                color: {self.COLOR_STATUS};
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
            }}
        """)

    def show_error(self, error: str):
        """Display an error message."""
        self.text_area.setPlainText(error)
        self._has_output = True
        self._update_button_states()
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.COLOR_OUTPUT_BG};
                color: {self.COLOR_ERROR};
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
            }}
        """)

    def set_state(self, state: str):
        """Set the execution state for feedback."""
        self._current_state = state
        self._apply_state_style(state)

        # Show/hide stop button for streaming/auto-refresh
        if state in ("running", "streaming", "auto_refresh"):
            self.stop_button.setVisible(True)
        else:
            self.stop_button.setVisible(False)

    def clear_output(self):
        """Clear the output text area."""
        self.text_area.clear()
        self._has_output = False
        self._update_button_states()
        # Reset to normal style
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.COLOR_OUTPUT_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
            }}
        """)

    def has_output(self) -> bool:
        """Check if there is output content."""
        return self._has_output

    def get_output(self) -> str:
        """Get the current output text."""
        return self.text_area.toPlainText()

    def save_output(self):
        """Save output to file (called via Ctrl+S shortcut)."""
        if not self._has_output:
            return
        self._do_save()

    def copy_output(self):
        """Copy output to clipboard (called via Ctrl+C shortcut)."""
        if self._has_output:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.get_output())

    def _on_save_clicked(self):
        """Handle save button click."""
        if not self._has_output:
            return
        self._do_save()

    def _do_save(self):
        """Perform the save operation."""
        # Get last save directory from settings
        start_dir = ""
        if self._settings_service:
            start_dir = self._settings_service.get_last_save_directory()

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Output",
            start_dir,
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.get_output())

                # Update last save directory
                if self._settings_service:
                    self._settings_service.set_last_save_directory(file_path)

            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")

    def _on_copy_clicked(self):
        """Handle copy button click."""
        self.copy_output()

    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.stop_requested.emit()

    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.clear_output()
        self.clear_requested.emit()
