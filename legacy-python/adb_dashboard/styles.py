"""
Dark theme stylesheet for ADB Debug Dashboard.

Color palette based on design direction:
- Background: #1e1e1e
- Card Surface: #2d2d2d
- Accent: #0078d4
- Success: #4caf50
- Error: #f44336
- Warning: #ff9800
- Auto-refresh: #00bcd4 (cyan)
- Streaming: #ff9800 (amber)
- Primary Text: #e0e0e0
- Secondary Text: #9e9e9e

Sprint 3 additions:
- Consistent hover states
- Focus indicators for keyboard navigation
- Button press states
- Smooth transitions
"""

DARK_THEME_STYLESHEET = """
/* Global styles */
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* Main window */
QMainWindow {
    background-color: #1e1e1e;
}

/* Header widget */
HeaderWidget {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3d3d3d;
}

/* Header label */
QLabel#headerTitle {
    font-size: 18px;
    font-weight: bold;
    color: #e0e0e0;
}

/* Status indicator */
StatusIndicator {
    background-color: transparent;
}

QLabel#statusLabel {
    font-size: 12px;
    color: #9e9e9e;
}

/* Refresh button with improved states */
QPushButton#refreshButton {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 6px 12px;
    color: #e0e0e0;
    min-width: 70px;
}

QPushButton#refreshButton:hover {
    background-color: #4d4d4d;
    border-color: #0078d4;
}

QPushButton#refreshButton:pressed {
    background-color: #0078d4;
    border-color: #0078d4;
}

QPushButton#refreshButton:focus {
    border-color: #0078d4;
    outline: 2px solid #0078d4;
    outline-offset: 1px;
}

/* Command cards area */
QScrollArea {
    background-color: #1e1e1e;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: #1e1e1e;
}

/* Scrollbar styling with hover states */
QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #4d4d4d;
    min-height: 30px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5d5d5d;
}

QScrollBar::handle:vertical:pressed {
    background-color: #0078d4;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background-color: none;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #4d4d4d;
    min-width: 30px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5d5d5d;
}

QScrollBar::handle:horizontal:pressed {
    background-color: #0078d4;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background-color: none;
}

/* Output area */
OutputArea {
    background-color: #1e1e1e;
}

/* Output toolbar */
QWidget#outputToolbar {
    background-color: #2d2d2d;
}

QTextEdit#outputText {
    background-color: #0d0d0d;
    color: #c0c0c0;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 8px;
}

QTextEdit#outputText:focus {
    border-color: #0078d4;
}

/* Output toolbar buttons with focus states */
QPushButton#clearButton {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 6px 12px;
    color: #e0e0e0;
    min-width: 60px;
}

QPushButton#clearButton:hover {
    background-color: #4d4d4d;
    border-color: #5d5d5d;
}

QPushButton#clearButton:pressed {
    background-color: #0078d4;
    border-color: #0078d4;
}

QPushButton#clearButton:focus {
    border-color: #0078d4;
    outline: 2px solid #0078d4;
    outline-offset: 1px;
}

QPushButton#clearButton:disabled {
    background-color: #2d2d2d;
    color: #5d5d5d;
    border-color: #3d3d3d;
}

/* Auto-refresh controls combo box with focus state */
QComboBox {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
}

QComboBox:hover {
    border-color: #5d5d5d;
}

QComboBox:focus {
    border-color: #0078d4;
    outline: 2px solid #0078d4;
    outline-offset: 1px;
}

QComboBox::drop-down {
    border: none;
    width: 16px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #9e9e9e;
    margin-right: 4px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    selection-background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #4d4d4d;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #0078d4;
}

/* Tooltips */
QToolTip {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

/* Focus indicator for all interactive widgets */
QPushButton:focus,
QComboBox:focus,
QLineEdit:focus,
QTextEdit:focus {
    outline: 2px solid #0078d4;
    outline-offset: 1px;
}

/* Menu styling (if needed in future) */
QMenuBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border-bottom: 1px solid #3d3d3d;
}

QMenuBar::item {
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
}

QMenu::item {
    padding: 6px 24px;
}

QMenu::item:selected {
    background-color: #0078d4;
}

/* Message box styling */
QMessageBox {
    background-color: #2d2d2d;
}

QMessageBox QLabel {
    color: #e0e0e0;
}

/* Dialog styling */
QDialog {
    background-color: #2d2d2d;
    color: #e0e0e0;
}
"""
