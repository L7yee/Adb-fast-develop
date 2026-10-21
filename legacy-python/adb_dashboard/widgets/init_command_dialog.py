"""
Init command format converter dialog for ADB Debug Dashboard.

Converts raw hex init_data/init_command into the full packet format:
  [prefix] 00 00 [length] [data]

Each line of input is converted independently.
Rules:
- 2-byte data uses short prefix (default 15)
- 3+ byte data uses long prefix (default 39)
- 00 00 is a fixed delay field
- Length is 1 byte representing the data byte count
- Short and long prefix values are user-configurable
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QApplication,
    QButtonGroup,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class InitCommandDialog(QDialog):
    """Dialog for converting init command hex data to packet format."""

    COLOR_BACKGROUND = "#2d2d2d"
    COLOR_INPUT_BG = "#1e1e1e"
    COLOR_OUTPUT_BG = "#0d0d0d"
    COLOR_TEXT = "#e0e0e0"
    COLOR_TEXT_SECONDARY = "#9e9e9e"
    COLOR_ACCENT = "#0078d4"
    COLOR_BUTTON = "#3d3d3d"
    COLOR_BUTTON_HOVER = "#4d4d4d"
    COLOR_ERROR = "#f44336"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Init Command Converter")
        self.setMinimumSize(550, 500)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.COLOR_BACKGROUND};
            }}
            QLabel {{
                color: {self.COLOR_TEXT};
                font-size: 13px;
            }}
            QLineEdit, QTextEdit {{
                background-color: {self.COLOR_INPUT_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {self.COLOR_ACCENT};
            }}
        """)

        # Input section
        input_label = QLabel("Input Data (one command per line, hex space-separated):")
        layout.addWidget(input_label)

        self.input_field = QTextEdit()
        self.input_field.setFont(QFont("Consolas", 13))
        self.input_field.setPlaceholderText(
            "e.g.\n"
            "B9 83 12 2B 55 00\n"
            "E9 C4\n"
            "D9 D3"
        )
        self.input_field.setMaximumHeight(150)
        self.input_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.COLOR_INPUT_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.input_field)

        # Prefix config row
        prefix_layout = QHBoxLayout()
        prefix_layout.setSpacing(12)

        short_label = QLabel("Short prefix (2-byte):")
        prefix_layout.addWidget(short_label)

        self.short_prefix_input = QLineEdit("15")
        self.short_prefix_input.setFixedWidth(60)
        self.short_prefix_input.setMaxLength(2)
        self.short_prefix_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prefix_layout.addWidget(self.short_prefix_input)

        prefix_layout.addSpacing(20)

        long_label = QLabel("Long prefix (3+ byte):")
        prefix_layout.addWidget(long_label)

        self.long_prefix_input = QLineEdit("39")
        self.long_prefix_input.setFixedWidth(60)
        self.long_prefix_input.setMaxLength(2)
        self.long_prefix_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prefix_layout.addWidget(self.long_prefix_input)

        prefix_layout.addStretch()
        layout.addLayout(prefix_layout)

        # Convert buttons
        convert_layout = QHBoxLayout()
        convert_layout.setSpacing(12)

        self.btn_plain = QPushButton("Convert → Hex")
        self.btn_plain.setToolTip("Output: 39 00 00 06 B9 83 12 2B 55 00")
        self.btn_plain.setStyleSheet(f"""
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
            QPushButton:pressed {{
                background-color: #006cbd;
            }}
        """)
        self.btn_plain.clicked.connect(lambda: self._on_convert(fmt="plain"))
        convert_layout.addWidget(self.btn_plain)

        self.btn_cstyle = QPushButton("Convert → 0x")
        self.btn_cstyle.setToolTip("Output: 0x39, 0x00, 0x00, 0x06, 0xB9, ...")
        self.btn_cstyle.setStyleSheet(f"""
            QPushButton {{
                background-color: #00897b;
                color: white;
                border: 1px solid #00897b;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00a693;
            }}
            QPushButton:pressed {{
                background-color: #00695c;
            }}
        """)
        self.btn_cstyle.clicked.connect(lambda: self._on_convert(fmt="cstyle"))
        convert_layout.addWidget(self.btn_cstyle)

        layout.addLayout(convert_layout)

        # Output section
        output_label = QLabel("Output:")
        layout.addWidget(output_label)

        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setFont(QFont("Consolas", 13))
        self.output_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.COLOR_OUTPUT_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.output_field)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFixedWidth(80)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet(f"""
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
            QPushButton:disabled {{
                background-color: #252525;
                color: #5d5d5d;
                border-color: #3d3d3d;
            }}
        """)
        self.copy_btn.clicked.connect(self._on_copy)
        btn_layout.addWidget(self.copy_btn)

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(80)
        close_btn.setStyleSheet(f"""
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
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _parse_hex_line(self, text: str) -> list[int]:
        """Parse a single space-separated hex line into byte list."""
        text = text.strip()
        if not text:
            raise ValueError("Empty line")

        parts = text.split()
        bytes_list = []
        for i, part in enumerate(parts):
            if len(part) != 2:
                raise ValueError(f"Invalid byte at position {i + 1}: '{part}' (must be 2 hex digits)")
            try:
                val = int(part, 16)
            except ValueError:
                raise ValueError(f"Invalid hex at position {i + 1}: '{part}'")
            if val < 0 or val > 255:
                raise ValueError(f"Value out of range at position {i + 1}: '{part}'")
            bytes_list.append(val)

        return bytes_list

    def _validate_prefix(self, text: str, name: str) -> int:
        """Validate a prefix hex value. Returns int or raises ValueError."""
        text = text.strip()
        if not text:
            raise ValueError(f"{name} prefix is empty")
        try:
            val = int(text, 16)
        except ValueError:
            raise ValueError(f"{name} prefix '{text}' is not valid hex")
        if val < 0 or val > 255:
            raise ValueError(f"{name} prefix must be 00-FF")
        return val

    def _format_result(self, result: list[int], fmt: str) -> str:
        """Format byte list to string based on output format."""
        if fmt == "cstyle":
            return ", ".join(f"0x{b:02X}" for b in result) + ","
        return " ".join(f"{b:02X}" for b in result)

    def _on_convert(self, fmt: str = "plain"):
        """Convert each input line independently. fmt: 'plain' or 'cstyle'."""
        raw = self.input_field.toPlainText()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]

        if not lines:
            self._show_error("No input data")
            return

        try:
            short_prefix = self._validate_prefix(self.short_prefix_input.text(), "Short")
            long_prefix = self._validate_prefix(self.long_prefix_input.text(), "Long")
        except ValueError as e:
            self._show_error(str(e))
            return

        output_lines = []
        for i, line in enumerate(lines):
            try:
                data_bytes = self._parse_hex_line(line)
            except ValueError as e:
                self._show_error(f"Line {i + 1}: {e}")
                return

            byte_count = len(data_bytes)
            prefix = short_prefix if byte_count == 2 else long_prefix
            result = [prefix, 0x00, 0x00, byte_count] + data_bytes
            output_lines.append(self._format_result(result, fmt))

        self.output_field.setText("\n".join(output_lines))
        self.output_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.COLOR_OUTPUT_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }}
        """)
        self.copy_btn.setEnabled(True)

    def _show_error(self, message: str):
        """Display an error in the output field."""
        self.output_field.setText(f"Error: {message}")
        self.output_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.COLOR_OUTPUT_BG};
                color: {self.COLOR_ERROR};
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }}
        """)
        self.copy_btn.setEnabled(False)

    def _on_copy(self):
        """Copy output to clipboard."""
        text = self.output_field.toPlainText().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
