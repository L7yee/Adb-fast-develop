"""
Command card widget for ADB Debug Dashboard.

A clickable card that represents an ADB shell command.
Features keyboard shortcut hints, hover states, focus indicators, and drag-drop reordering.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QMimeData, QPoint, QEvent
from PyQt6.QtGui import QCursor, QDrag, QPixmap, QPainter

from ..models.command import Command
from .auto_refresh_controls import AutoRefreshControls


class CommandCard(QWidget):
    """
    A card widget representing an ADB shell command.

    Features:
    - Rounded corners with border
    - Hover state with accent border
    - Disabled state for non-clickable commands
    - Visual feedback for execution state
    - Auto-refresh controls for applicable commands
    - Keyboard shortcut hints
    - Focus indicators for accessibility
    - Drag-drop reordering
    """

    clicked = pyqtSignal(object)  # Emits the command when clicked (use object to avoid type registration)
    auto_refresh_toggled = pyqtSignal(bool)  # Emitted when auto-refresh is toggled
    auto_refresh_interval_changed = pyqtSignal(int)  # Emitted when interval changes
    drag_started = pyqtSignal(object)  # Emits the card when drag starts
    dropped = pyqtSignal(object, object)  # Emits (source_id, target_id) when drop occurs

    # Color constants matching design-direction.md
    COLOR_CARD = "#2d2d2d"
    COLOR_CARD_HOVER = "#3d3d3d"
    COLOR_CARD_RUNNING = "#3a3a3a"
    COLOR_DISABLED = "#252525"
    COLOR_ACCENT = "#0078d4"
    COLOR_RUNNING = "#ff9800"  # Amber for running state
    COLOR_STREAMING = "#ff9800"  # Amber for streaming
    COLOR_AUTO_REFRESH = "#00bcd4"  # Cyan for auto-refresh
    COLOR_TEXT_PRIMARY = "#e0e0e0"
    COLOR_TEXT_SECONDARY = "#9e9e9e"
    COLOR_TEXT_DISABLED = "#5d5d5d"
    COLOR_BORDER = "#3d3d3d"
    COLOR_BORDER_DISABLED = "#2d2d2d"
    COLOR_FOCUS = "#0078d4"
    COLOR_DRAG = "#1565c0"

    MIME_TYPE = "application/x-command-card"

    def __init__(self, command: Command, index: int = -1, parent=None):
        super().__init__(parent)
        self.command = command
        self._index = index
        self._is_enabled = command.is_clickable
        self._is_hovering = False
        self._is_running = False
        self._is_auto_refreshing = False
        self._drag_start_pos = None
        self._is_dragging = False
        self._drag_mode_enabled = False  # Drag mode flag

        self._setup_ui()
        self._apply_style()

    def set_drag_mode(self, enabled: bool):
        """Enable or disable drag mode."""
        self._drag_mode_enabled = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.setAcceptDrops(True)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setAcceptDrops(False)

    def _setup_ui(self):
        """Build the card UI layout."""
        # Set fixed size for consistency
        self.setFixedHeight(70)
        self.setMinimumWidth(180)

        # Enable focus for keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(4)

        # Top row: label and auto-refresh controls
        top_row = QWidget()
        top_row.setStyleSheet("background: transparent;")
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)

        # Command label
        self.label = QLabel(self.command.label)
        self.label.setObjectName("cardLabel")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        top_layout.addWidget(self.label)

        top_layout.addStretch()

        # Auto-refresh controls (if applicable)
        self.auto_refresh_controls = None
        if self.command.auto_refresh_capable:
            self.auto_refresh_controls = AutoRefreshControls()
            self.auto_refresh_controls.toggled.connect(self._on_auto_refresh_toggled)
            self.auto_refresh_controls.interval_changed.connect(self._on_interval_changed)
            top_layout.addWidget(self.auto_refresh_controls)

        main_layout.addWidget(top_row)

        # Category tag (small secondary text)
        self.category_label = QLabel(self._get_category_display())
        self.category_label.setObjectName("categoryLabel")
        self.category_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.category_label)

        main_layout.addStretch()

        # Set cursor and tooltip for clickable state
        self._update_cursor()
        self._update_tooltip()

    def _get_category_display(self) -> str:
        """Get display text for category."""
        category = self.command.category.capitalize()
        if self.command.category == "streaming":
            return f"{category} (Real-time)"
        elif self.command.category == "action":
            return f"{category} (Launch)"
        return category

    def _update_tooltip(self):
        """Update tooltip with keyboard shortcut hint."""
        tooltip = f"Click to execute: {self.command.label}"
        if self._index >= 0 and self._index < 10:
            key = self._index + 1 if self._index < 9 else 0
            tooltip += f"\nShortcut: Ctrl+{key}"
        self.setToolTip(tooltip)

    def set_index(self, index: int):
        """Set the command index for keyboard shortcut hints."""
        self._index = index
        self._update_tooltip()

    def _apply_style(self):
        """Apply styling based on enabled/disabled state."""
        if self._is_enabled:
            border_color = self.COLOR_BORDER
            if self._is_running:
                border_color = self.COLOR_RUNNING
            elif self._is_auto_refreshing:
                border_color = self.COLOR_AUTO_REFRESH

            self.setStyleSheet(f"""
                CommandCard {{
                    background-color: {self.COLOR_CARD};
                    border: 2px solid {border_color};
                    border-radius: 6px;
                }}
                CommandCard:hover {{
                    background-color: {self.COLOR_CARD_HOVER};
                    border-color: {self.COLOR_ACCENT};
                }}
                CommandCard:focus {{
                    border-color: {self.COLOR_FOCUS};
                    outline: 2px solid {self.COLOR_FOCUS};
                    outline-offset: 1px;
                }}
                QLabel#cardLabel {{
                    background-color: transparent;
                    color: {self.COLOR_TEXT_PRIMARY};
                    font-size: 14px;
                    font-weight: 500;
                }}
                QLabel#categoryLabel {{
                    background-color: transparent;
                    color: {self.COLOR_TEXT_SECONDARY};
                    font-size: 11px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                CommandCard {{
                    background-color: {self.COLOR_DISABLED};
                    border: 2px solid {self.COLOR_BORDER_DISABLED};
                    border-radius: 6px;
                }}
                QLabel#cardLabel {{
                    background-color: transparent;
                    color: {self.COLOR_TEXT_DISABLED};
                    font-size: 14px;
                    font-weight: 500;
                }}
                QLabel#categoryLabel {{
                    background-color: transparent;
                    color: {self.COLOR_TEXT_DISABLED};
                    font-size: 11px;
                }}
            """)

    def _update_cursor(self):
        """Update cursor based on enabled state."""
        if self._is_enabled:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ForbiddenCursor))

    def set_enabled(self, enabled: bool):
        """Enable or disable the card."""
        self._is_enabled = enabled
        self._apply_style()
        self._update_cursor()

    def set_running(self, running: bool):
        """Set the running state for visual feedback."""
        self._is_running = running
        self._apply_style()

    def set_auto_refreshing(self, active: bool):
        """Set the auto-refresh active state for visual feedback."""
        self._is_auto_refreshing = active
        self._apply_style()
        if self.auto_refresh_controls:
            self.auto_refresh_controls.set_active(active)

    def is_auto_refreshing(self) -> bool:
        """Check if auto-refresh is active."""
        return self._is_auto_refreshing

    def get_auto_refresh_interval(self) -> int:
        """Get the auto-refresh interval in seconds."""
        if self.auto_refresh_controls:
            return self.auto_refresh_controls.get_interval()
        return 5  # Default

    def _on_auto_refresh_toggled(self, active: bool):
        """Handle auto-refresh toggle."""
        self._is_auto_refreshing = active
        self._apply_style()
        self.auto_refresh_toggled.emit(active)

    def _on_interval_changed(self, seconds: int):
        """Handle interval change."""
        self.auto_refresh_interval_changed.emit(seconds)

    def mousePressEvent(self, event):
        """Handle mouse press for click events and drag start."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._drag_mode_enabled:
                # In drag mode: start drag
                self._drag_start_pos = event.position()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            elif self._is_enabled:
                # Normal mode: emit click
                self.clicked.emit(self.command)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for drag operation."""
        if not self._drag_mode_enabled:
            super().mouseMoveEvent(event)
            return

        if self._drag_start_pos is None:
            super().mouseMoveEvent(event)
            return

        # Check if moved enough to start drag
        distance = (event.position() - self._drag_start_pos).manhattanLength()
        if distance < 15:  # Minimum drag distance
            super().mouseMoveEvent(event)
            return

        # Start drag
        self._is_dragging = True
        self.grabMouse()  # Grab mouse to receive all events

        # Raise this card to top
        self.raise_()

        # Visual feedback
        self._apply_drag_highlight(True)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if self._drag_mode_enabled and self._is_dragging:
            self.releaseMouse()
            self._is_dragging = False
            self._apply_drag_highlight(False)

            # Find the card under the mouse and swap
            target_card = self._find_card_under_mouse(event.globalPosition().toPoint())
            if target_card and target_card != self:
                self.dropped.emit(self.command.id, target_card.command.id)

            self._drag_start_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif self._drag_mode_enabled:
            self._drag_start_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)

        super().mouseReleaseEvent(event)

    def _find_card_under_mouse(self, global_pos):
        """Find the command card under the given global position."""
        from PyQt6.QtWidgets import QApplication

        widget = QApplication.widgetAt(global_pos)
        while widget:
            if isinstance(widget, CommandCard) and widget != self:
                return widget
            widget = widget.parent()
        return None

    def _apply_drag_highlight(self, highlight: bool):
        """Apply visual highlight during drag-over."""
        if highlight:
            self.setStyleSheet(self.styleSheet().replace(
                f"border: 2px solid {self.COLOR_ACCENT};",
                f"border: 3px solid {self.COLOR_DRAG};"
            ).replace(
                f"border: 1px solid {self.COLOR_BORDER};",
                f"border: 3px solid {self.COLOR_DRAG};"
            ))
        else:
            self._apply_style()

    def keyPressEvent(self, event):
        """Handle key press for Enter/Return to execute."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Space) and self._is_enabled:
            self.clicked.emit(self.command)
        else:
            super().keyPressEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter for hover state."""
        self._is_hovering = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave for hover state."""
        self._is_hovering = False
        super().leaveEvent(event)

    def focusInEvent(self, event):
        """Handle focus in for accessibility."""
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event):
        """Handle focus out for accessibility."""
        super().focusOutEvent(event)
        self.update()
