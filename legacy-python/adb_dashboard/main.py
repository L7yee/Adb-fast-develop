"""
ADB Debug Dashboard - Main entry point.

Launch the PyQt6 application for ADB shell command execution.
Sprint 3: Includes application icon, version display, and settings management.
"""

import sys
import os
import logging
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import QSize, Qt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Application version
APP_VERSION = "0.3.0"
APP_NAME = "ADB Debug Dashboard"


def exception_hook(exc_type, exc_value, exc_tb):
    """Global exception handler to catch and log crashes."""
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.critical(f"Uncaught exception:\n{error_msg}")

    # Show error dialog if possible
    try:
        QMessageBox.critical(
            None,
            "Application Error",
            f"An error occurred:\n\n{exc_value}\n\nSee log for details."
        )
    except:
        pass

    sys.exit(1)


def create_default_icon() -> QIcon:
    """
    Create a default application icon programmatically.

    Creates a simple icon with an "ADB" text on a dark background
    with an accent border. This ensures the app always has an icon
    even without external resource files.

    Returns:
        QIcon with the generated icon
    """
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background color (dark theme)
    bg_color = QColor(45, 45, 45)  # #2d2d2d
    accent_color = QColor(0, 120, 212)  # #0078d4

    # Draw rounded rectangle background
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(bg_color)
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 8, 8)

    # Draw accent border
    painter.setPen(accent_color)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(accent_color)
    painter.drawRoundedRect(2, 2, size - 5, size - 5, 8, 8)

    # Draw "ADB" text
    font = QFont("Segoe UI", 18, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor(224, 224, 224))  # #e0e0e0

    # Center the text
    text = "ADB"
    text_rect = painter.fontMetrics().boundingRect(text)
    x = (size - text_rect.width()) // 2
    y = (size + text_rect.height()) // 2 - 4  # -4 for baseline adjustment
    painter.drawText(x, y, text)

    painter.end()

    return QIcon(pixmap)


def get_application_icon() -> QIcon:
    """
    Get the application icon.

    Tries to load from file first, falls back to generated icon.

    Returns:
        QIcon for the application
    """
    # Try to load icon from file
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.png')
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        if not icon.isNull():
            return icon

    # Fall back to generated icon
    return create_default_icon()


def main():
    """Application entry point."""
    # Install global exception handler
    sys.excepthook = exception_hook

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("ADB Debug Tools")

    # Set application icon
    icon = get_application_icon()
    app.setWindowIcon(icon)

    # Apply dark theme styling
    from .styles import DARK_THEME_STYLESHEET
    app.setStyleSheet(DARK_THEME_STYLESHEET)

    # Import and create main window (after app is configured)
    from .main_window import MainWindow

    # Create and show main window
    try:
        window = MainWindow()

        # Set window icon explicitly
        window.setWindowIcon(icon)

        window.show()

        # Log startup
        logging.info(f"{APP_NAME} v{APP_VERSION} started")
    except Exception as e:
        logging.exception(f"Failed to create main window: {e}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Error", f"Failed to start application:\n{e}")
        sys.exit(1)

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
