"""
Main window for ADB Debug Dashboard.

Implements the two-panel layout with command cards and output area.
Handles all 10 commands, streaming, auto-refresh, export functionality,
settings persistence, and keyboard shortcuts.
"""

import logging
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QMessageBox,
    QFileDialog,
    QProgressDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QScreen, QShortcut

from .widgets.command_card import CommandCard
from .widgets.output_area import OutputArea
from .widgets.status_indicator import StatusIndicator
from .services.adb_service import ADBService
from .services.settings_service import SettingsService
from .models.command import get_commands, Command

logger = logging.getLogger(__name__)

# Application version
APP_VERSION = "0.3.0"

# Default APK directory
DEFAULT_APK_DIR = r"E:\workplace\apk"


class HeaderWidget(QWidget):
    """Header bar with app title, status indicator, and refresh button."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # App title with version
        title_label = QLabel(f"ADB Debug Dashboard v{APP_VERSION}")
        title_label.setObjectName("headerTitle")
        layout.addWidget(title_label)

        # Spacer
        layout.addStretch()

        # Root status indicator
        self.root_label = QLabel("")
        self.root_label.setStyleSheet("""
            QLabel {
                color: #9e9e9e;
                font-size: 11px;
                padding: 2px 6px;
                border-radius: 3px;
                background: transparent;
            }
        """)
        layout.addWidget(self.root_label)

        # Status indicator
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator)

        # Manage commands button
        self.manage_button = QPushButton("Manage")
        self.manage_button.setObjectName("manageButton")
        self.manage_button.setFixedWidth(70)
        self.manage_button.setToolTip("Add, edit, or delete commands")
        layout.addWidget(self.manage_button)

        # Drag mode toggle button
        self.drag_button = QPushButton("Reorder")
        self.drag_button.setObjectName("dragButton")
        self.drag_button.setFixedWidth(70)
        self.drag_button.setCheckable(True)
        self.drag_button.setToolTip("Toggle reorder mode to drag cards")
        self.drag_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
                border-color: #0078d4;
            }
        """)
        layout.addWidget(self.drag_button)

        # Compare mode toggle button
        self.compare_button = QPushButton("Compare")
        self.compare_button.setObjectName("compareButton")
        self.compare_button.setFixedWidth(70)
        self.compare_button.setCheckable(True)
        self.compare_button.setToolTip("Toggle compare mode to highlight changes")
        self.compare_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:checked {
                background-color: #00bcd4;
                color: white;
                border-color: #00bcd4;
            }
        """)
        layout.addWidget(self.compare_button)

        # Init Command button
        self.init_cmd_button = QPushButton("Init Cmd")
        self.init_cmd_button.setObjectName("initCmdButton")
        self.init_cmd_button.setFixedWidth(70)
        self.init_cmd_button.setToolTip("Convert init command format")
        self.init_cmd_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #0078d4;
            }
        """)
        layout.addWidget(self.init_cmd_button)

        # Install APK button
        self.install_button = QPushButton("Install APK")
        self.install_button.setObjectName("installButton")
        self.install_button.setFixedWidth(90)
        self.install_button.setToolTip("Install APK to connected device")
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: 1px solid #0078d4;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
        layout.addWidget(self.install_button)

        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setFixedWidth(80)
        self.refresh_button.setToolTip("Refresh device status (Ctrl+R)")
        layout.addWidget(self.refresh_button)

    def set_status(self, status: str, message: str = ""):
        """Update the device status indicator."""
        self.status_indicator.set_status(status, message)

    def set_root_status(self, has_root: bool, message: str = ""):
        """Update the root status indicator."""
        if has_root:
            self.root_label.setText("ROOT")
            self.root_label.setStyleSheet("""
                QLabel {
                    color: #4caf50;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 2px 6px;
                    border-radius: 3px;
                    background: #1b5e20;
                }
            """)
        else:
            self.root_label.setText("NO ROOT")
            self.root_label.setStyleSheet("""
                QLabel {
                    color: #f44336;
                    font-size: 11px;
                    padding: 2px 6px;
                    border-radius: 3px;
                    background: #4a1a1a;
                }
            """)
        if message:
            self.root_label.setToolTip(message)

    def get_status_indicator(self) -> StatusIndicator:
        """Get the status indicator widget."""
        return self.status_indicator


class MainWindow(QMainWindow):
    """Main application window with two-panel layout."""

    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    def __init__(self):
        super().__init__()

        # Initialize services
        self.adb_service = ADBService()
        self.settings_service = SettingsService()

        # Command execution state
        self.current_command: Command = None
        self.is_executing = False
        self.is_streaming = False
        self.is_auto_refreshing = False

        # Auto-refresh state
        self.auto_refresh_command: Command = None

        # Compare mode state
        self.is_compare_mode = False
        self.last_output = {}  # {command_id: output_text}

        # Load settings
        self._load_settings()

        # Setup UI
        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()

        # Initial device status check
        self._check_device_status()

    def _load_settings(self):
        """Load persisted settings."""
        settings = self.settings_service.load_settings()
        self._saved_geometry = settings.window

    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle(f"ADB Debug Dashboard v{APP_VERSION}")
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Restore window geometry from settings
        if self._saved_geometry:
            if self._saved_geometry.maximized:
                self.showMaximized()
            else:
                # Validate position is on screen
                width = self._saved_geometry.width
                height = self._saved_geometry.height
                x = self._saved_geometry.x
                y = self._saved_geometry.y

                # Check if position is valid (within any screen)
                valid_position = self._is_position_valid(x, y, width, height)

                if valid_position:
                    self.setGeometry(x, y, width, height)
                else:
                    # Default size if position is off-screen
                    self.resize(width, height)
        else:
            self.resize(1024, 700)

    def _is_position_valid(self, x: int, y: int, width: int, height: int) -> bool:
        """Check if window position is within available screen area."""
        from PyQt6.QtWidgets import QApplication
        screens = QApplication.screens()
        for screen in screens:
            geometry = screen.availableGeometry()
            # Check if at least part of the window is visible
            if (x < geometry.right() and x + width > geometry.left() and
                y < geometry.bottom() and y + height > geometry.top()):
                return True
        return False

    def _setup_ui(self):
        """Build the main UI layout."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)

        # Content area (two panels)
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)

        # Left panel: Command cards
        left_panel = self._create_command_panel()
        content_layout.addWidget(left_panel, stretch=1)

        # Right panel: Output area
        self.output_area = OutputArea(self.settings_service)
        content_layout.addWidget(self.output_area, stretch=2)

        main_layout.addWidget(content_widget)

    def _create_command_panel(self) -> QWidget:
        """Create the command cards panel with scroll area."""
        panel_widget = QWidget()
        panel_layout = QVBoxLayout(panel_widget)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Scroll content
        scroll_content = QWidget()
        scroll_content.setAcceptDrops(True)  # Enable drops on scroll content
        self.card_layout = QGridLayout(scroll_content)
        self.card_layout.setContentsMargins(8, 8, 8, 8)
        self.card_layout.setSpacing(12)
        self.card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create command cards
        self._create_command_cards()

        scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(scroll_area)

        return panel_widget

    def _create_command_cards(self):
        """Create and arrange all command cards in a 2-column grid."""
        self.command_cards = []
        commands = get_commands()

        for index, cmd in enumerate(commands):
            card = CommandCard(cmd, index=index)
            card.clicked.connect(self._on_card_clicked)
            card.auto_refresh_toggled.connect(self._on_auto_refresh_toggled)
            card.auto_refresh_interval_changed.connect(self._on_auto_refresh_interval_changed)
            card.dropped.connect(self._on_card_dropped)

            row = index // 2
            col = index % 2

            self.card_layout.addWidget(card, row, col)
            self.command_cards.append(card)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+S: Save output
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self._on_save_output)
        self.save_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)

        # Ctrl+C: Copy output
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.copy_shortcut.activated.connect(self._on_copy_output)
        self.copy_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)

        # Ctrl+R: Refresh device status
        self.refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.refresh_shortcut.activated.connect(self._check_device_status)
        self.refresh_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)

        # Escape: Stop operation
        self.stop_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.stop_shortcut.activated.connect(self._on_stop_requested)
        self.stop_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)

        # Ctrl+1 through Ctrl+0: Quick command access
        self.command_shortcuts = []
        commands = get_commands()
        for i in range(min(10, len(commands))):
            key = i + 1 if i < 9 else 0
            shortcut = QShortcut(QKeySequence(f"Ctrl+{key}"), self)
            shortcut.activated.connect(lambda checked=False, idx=i: self._execute_command_by_index(idx))
            shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
            self.command_shortcuts.append(shortcut)

    def _connect_signals(self):
        """Connect UI signals to handlers."""
        self.header.refresh_button.clicked.connect(self._check_device_status)
        self.header.manage_button.clicked.connect(self._on_manage_commands)
        self.header.drag_button.toggled.connect(self._on_drag_mode_toggled)
        self.header.compare_button.toggled.connect(self._on_compare_mode_toggled)
        self.header.init_cmd_button.clicked.connect(self._on_init_cmd)
        self.header.install_button.clicked.connect(self._on_install_apk)
        self.output_area.clear_requested.connect(self._on_clear_output)
        self.output_area.stop_requested.connect(self._on_stop_requested)
        self.adb_service.auto_refresh_manager.refresh_triggered.connect(self._on_auto_refresh_trigger)
        # Connect async device check signal
        self.adb_service.device_check_finished.connect(self._on_device_check_finished)

    def _on_compare_mode_toggled(self, checked: bool):
        """Toggle compare mode."""
        self.is_compare_mode = checked
        if checked:
            self.header.compare_button.setToolTip("Compare mode ON - Click same card twice to compare")
        else:
            self.header.compare_button.setToolTip("Toggle compare mode to highlight changes")
            # Clear stored outputs when disabling compare mode
            self.last_output.clear()

    def _on_drag_mode_toggled(self, checked: bool):
        """Toggle drag mode for all command cards."""
        for card in self.command_cards:
            card.set_drag_mode(checked)

        if checked:
            self.header.drag_button.setToolTip("Click to exit reorder mode")
        else:
            self.header.drag_button.setToolTip("Toggle reorder mode to drag cards")

    def _check_device_status(self):
        """Check and update device connection status (async, non-blocking)."""
        # Stop any ongoing operations first
        self._stop_all_operations()

        # Show checking status
        self.header.set_status("checking", "Checking...")
        self.header.set_root_status(False, "")

        # Check if ADB is available (quick check)
        if not self.adb_service.is_adb_available():
            self.header.set_status("error", "ADB not found")
            self.header.set_root_status(False, "ADB not available")
            self._disable_all_cards()
            return

        # Use async device check
        self.adb_service.check_device_async()

    def _on_device_check_finished(self, is_connected: bool, error_type: str, has_root: bool, root_message: str):
        """Handle async device check result."""
        if is_connected:
            device_id = self.adb_service.get_device_id()
            self.header.set_status("connected", device_id or "Device")
            self._enable_all_cards()
            self.header.set_root_status(has_root, root_message)
        elif error_type == "unauthorized":
            self.header.set_status("error", "Unauthorized")
            self.header.set_root_status(False, "Device unauthorized")
            self._disable_all_cards()
        elif error_type == "multiple":
            self.header.set_status("error", "Multiple devices")
            self.header.set_root_status(False, "Multiple devices")
            self._disable_all_cards()
        else:
            self.header.set_status("disconnected", "No device")
            self.header.set_root_status(False, "No device connected")
            self._disable_all_cards()

    def _disable_all_cards(self):
        """Disable all command cards."""
        for card in self.command_cards:
            card.set_enabled(False)
            card.set_auto_refreshing(False)

    def _enable_all_cards(self):
        """Enable all command cards."""
        for card in self.command_cards:
            card.set_enabled(True)

    def _stop_all_operations(self):
        """Stop any running operations."""
        # Stop streaming
        if self.is_streaming:
            self.adb_service.stop_streaming()
            # Reset card running state
            if self.current_command:
                card = self._get_card_for_command(self.current_command)
                if card:
                    card.set_running(False)
            self.is_streaming = False

        # Stop auto-refresh
        if self.is_auto_refreshing:
            self.adb_service.auto_refresh_manager.stop()
            self.is_auto_refreshing = False
            if self.auto_refresh_command:
                card = self._get_card_for_command(self.auto_refresh_command)
                if card:
                    card.set_auto_refreshing(False)
            self.auto_refresh_command = None

        # Cancel regular command
        if self.is_executing:
            self.adb_service.cancel_current_command()
            self.is_executing = False

        self.output_area.set_state("ready")

    def _get_card_for_command(self, command: Command) -> CommandCard:
        """Get the card widget for a command."""
        for card in self.command_cards:
            if card.command.id == command.id:
                return card
        return None

    def _execute_command_by_index(self, index: int):
        """Execute command by index (for keyboard shortcuts)."""
        commands = get_commands()
        if 0 <= index < len(commands):
            # Check if device is connected
            is_connected, _ = self.adb_service.check_device()
            if is_connected:
                self._on_card_clicked(commands[index])

    def _on_save_output(self):
        """Handle Ctrl+S shortcut."""
        self.output_area.save_output()

    def _on_copy_output(self):
        """Handle Ctrl+C shortcut."""
        self.output_area.copy_output()

    def _on_install_apk(self):
        """Handle Install APK button click."""
        import subprocess
        import os

        # Check if device is connected
        is_connected, _ = self.adb_service.check_device()
        if not is_connected:
            QMessageBox.warning(self, "No Device", "Please connect a device first.")
            return

        # Open file dialog to select APK
        start_dir = DEFAULT_APK_DIR if os.path.exists(DEFAULT_APK_DIR) else ""
        apk_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select APK to Install",
            start_dir,
            "APK Files (*.apk);;All Files (*)"
        )

        if not apk_path:
            return  # User cancelled

        # Get APK filename for display
        apk_name = os.path.basename(apk_path)

        # Show progress dialog
        progress = QProgressDialog(f"Installing {apk_name}...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Installing APK")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()

        # Force UI update
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        def do_install(extra_args=None):
            """Execute adb install command."""
            cmd = ["adb", "install"]
            if extra_args:
                cmd.extend(extra_args)
            cmd.extend(["-r", apk_path])

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return process.communicate(), process.returncode

        try:
            # First attempt: normal install
            (stdout, stderr), returncode = do_install()
            progress.setValue(50)

            # Check for deprecated SDK version error
            combined_output = stdout + stderr
            if "INSTALL_FAILED_DEPRECATED_SDK_VERSION" in combined_output:
                # Retry with bypass flag
                progress.setLabelText(f"Retrying with bypass flag...")
                QApplication.processEvents()
                logger.info("Retrying install with --bypass-low-target-sdk-block")
                (stdout, stderr), returncode = do_install(["--bypass-low-target-sdk-block"])

            progress.setValue(100)

            if returncode == 0:
                # Check for success in output
                if "Success" in stdout:
                    self.output_area.show_output(
                        f"Successfully installed: {apk_name}\n\n{stdout}",
                        "Install APK",
                        f"install -r {apk_name}"
                    )
                    self.output_area.set_state("completed")
                    QMessageBox.information(self, "Success", f"Successfully installed:\n{apk_name}")
                else:
                    # Some devices return success but with warning
                    self.output_area.show_output(
                        f"Installation completed:\n{stdout}",
                        "Install APK",
                        f"install -r {apk_name}"
                    )
                    self.output_area.set_state("completed")
            else:
                error_msg = stderr.strip() if stderr else stdout.strip()
                self.output_area.show_error(f"Installation failed:\n{error_msg}")
                self.output_area.set_state("error")
                QMessageBox.warning(self, "Install Failed", f"Failed to install APK:\n{error_msg}")

        except subprocess.TimeoutExpired:
            progress.setValue(100)
            self.output_area.show_error("Installation timed out")
            self.output_area.set_state("error")
            QMessageBox.warning(self, "Timeout", "Installation timed out. The APK may be too large.")
        except Exception as e:
            progress.setValue(100)
            self.output_area.show_error(f"Installation error: {str(e)}")
            self.output_area.set_state("error")
            QMessageBox.warning(self, "Error", f"Installation error:\n{str(e)}")
        finally:
            progress.close()

    def _on_manage_commands(self):
        """Handle manage commands button click."""
        from .widgets.command_manager_dialog import CommandManagerDialog
        from .models.command import get_commands, Command

        commands = get_commands()
        dialog = CommandManagerDialog(commands, self)

        if dialog.exec():
            changes = dialog.get_changes()
            self._apply_command_changes(changes)

    def _on_init_cmd(self):
        """Handle Init Cmd button click."""
        from .widgets.init_command_dialog import InitCommandDialog
        dialog = InitCommandDialog(self)
        dialog.exec()

    def _apply_command_changes(self, changes: dict):
        """Apply changes from command manager dialog."""
        import yaml
        from .services.config_service import ConfigService

        deleted_ids = changes.get('deleted_ids', set())
        modified_commands = changes.get('modified_commands', {})

        if not deleted_ids and not modified_commands:
            return

        config_service = ConfigService()
        config_path = config_service.get_config_path()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(content)

            if not data or 'commands' not in data:
                return

            # Apply deletions
            if deleted_ids:
                data['commands'] = [c for c in data['commands'] if c.get('id') not in deleted_ids]

            # Apply modifications
            for cmd_id, mods in modified_commands.items():
                if mods.get('is_new'):
                    # Add new command
                    data['commands'].append({
                        'id': cmd_id,
                        'label': mods['label'],
                        'shell_command': mods['shell_command'],
                        'is_clickable': True,
                        'category': mods['category'],
                        'auto_refresh_capable': mods['auto_refresh_capable'],
                        'requires_root': mods['requires_root']
                    })
                else:
                    # Update existing
                    for cmd in data['commands']:
                        if cmd.get('id') == cmd_id:
                            cmd['label'] = mods['label']
                            cmd['shell_command'] = mods['shell_command']
                            cmd['category'] = mods['category']
                            cmd['auto_refresh_capable'] = mods['auto_refresh_capable']
                            cmd['requires_root'] = mods['requires_root']
                            break

            # Write back
            with open(config_path, 'w', encoding='utf-8') as f:
                # Preserve header
                header_end = content.find('commands:')
                if header_end > 0:
                    f.write(content[:header_end])
                yaml.dump({'commands': data['commands']}, f, default_flow_style=False, sort_keys=False)

            # Reload UI
            self._reload_command_cards()

            logging.info(f"Applied changes: {len(deleted_ids)} deleted, {len(modified_commands)} modified")

        except Exception as e:
            logging.error(f"Failed to apply changes: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save changes: {e}")

    def _reload_command_cards(self, preserve_drag_mode: bool = False):
        """Reload all command cards from config."""
        from .models.command import load_commands
        from .widgets.command_card import CommandCard

        # Remember drag mode state
        drag_mode_was_enabled = preserve_drag_mode and self.header.drag_button.isChecked()

        # Clear existing cards
        for card in self.command_cards:
            card.deleteLater()
        self.command_cards.clear()

        # Reload commands
        from .models import command as cmd_module
        cmd_module._COMMANDS = None  # Reset cache
        commands = load_commands()

        # Recreate cards
        for index, cmd in enumerate(commands):
            card = CommandCard(cmd, index=index)
            card.clicked.connect(self._on_card_clicked)
            card.auto_refresh_toggled.connect(self._on_auto_refresh_toggled)
            card.auto_refresh_interval_changed.connect(self._on_auto_refresh_interval_changed)
            card.dropped.connect(self._on_card_dropped)

            row = index // 2
            col = index % 2

            self.card_layout.addWidget(card, row, col)
            self.command_cards.append(card)

            # Restore drag mode if needed
            if drag_mode_was_enabled:
                card.set_drag_mode(True)

        # Enable cards if device connected
        is_connected, _ = self.adb_service.check_device()
        if is_connected:
            for card in self.command_cards:
                card.set_enabled(True)

    def _on_card_dropped(self, source_id: str, target_id: str):
        """Handle card drop for reordering."""
        import yaml
        from .services.config_service import ConfigService

        config_service = ConfigService()
        config_path = config_service.get_config_path()

        # Remember drag mode state before reload
        drag_mode_was_enabled = self.header.drag_button.isChecked()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(content)

            if not data or 'commands' not in data:
                return

            commands = data['commands']

            # Find indices
            source_idx = None
            target_idx = None
            for i, cmd in enumerate(commands):
                if cmd.get('id') == source_id:
                    source_idx = i
                if cmd.get('id') == target_id:
                    target_idx = i

            if source_idx is None or target_idx is None:
                return

            # Swap positions
            commands[source_idx], commands[target_idx] = commands[target_idx], commands[source_idx]

            # Write back
            with open(config_path, 'w', encoding='utf-8') as f:
                header_end = content.find('commands:')
                if header_end > 0:
                    f.write(content[:header_end])
                yaml.dump({'commands': commands}, f, default_flow_style=False, sort_keys=False)

            # Reload UI (this will preserve drag mode)
            self._reload_command_cards(preserve_drag_mode=True)

            logging.info(f"Swapped commands: {source_id} <-> {target_id}")

        except Exception as e:
            logging.error(f"Failed to reorder commands: {e}")

    def _on_card_clicked(self, command: Command):
        """Handle command card click."""
        # Stop any ongoing operations first
        self._stop_all_operations()

        # Don't clear output - keep history

        # Store current command
        self.current_command = command

        # Handle based on command category
        if command.category == "streaming":
            self._execute_streaming_command(command)
        else:
            self._execute_standard_command(command)

    def _execute_standard_command(self, command: Command):
        """Execute a standard (non-streaming) command."""
        self.output_area.show_status(f"Executing: {command.label}...")
        self.output_area.set_state("running")
        self.is_executing = True

        # Mark card as running
        card = self._get_card_for_command(command)
        if card:
            card.set_running(True)

        # Determine if root is needed
        use_root = command.requires_root or self.adb_service.has_root()

        self.adb_service.execute_command(
            command.shell_command,
            on_success=self._on_command_success,
            on_error=self._on_command_error,
            use_root=use_root
        )

    def _execute_streaming_command(self, command: Command):
        """Execute a streaming command (getevent -l)."""
        # Clear and show command header
        self.output_area.clear_output()
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        header = f"[{timestamp}] {command.label}\nadb shell {command.shell_command}\n{'-'*60}\n"
        self.output_area.append_output(header)

        self.output_area.set_state("streaming")
        self.is_streaming = True

        # Mark card as running
        card = self._get_card_for_command(command)
        if card:
            card.set_running(True)

        self.adb_service.execute_streaming_command(
            command.shell_command,
            on_line=self._on_streaming_line,
            on_started=self._on_streaming_started,
            on_stopped=self._on_streaming_stopped,
            on_error=self._on_command_error
        )

    def _on_command_success(self, output: str):
        """Handle successful command execution."""
        self.is_executing = False

        # Reset card running state
        if self.current_command:
            card = self._get_card_for_command(self.current_command)
            if card:
                card.set_running(False)

        # Show output with command label and shell command
        command_label = self.current_command.label if self.current_command else ""
        shell_command = self.current_command.shell_command if self.current_command else ""

        # Handle compare mode
        if self.is_compare_mode and self.current_command:
            command_id = self.current_command.id
            if command_id in self.last_output:
                # Compare with previous output
                prev_output = self.last_output[command_id]
                self.output_area.show_compare_output(
                    prev_output, output, command_label, shell_command
                )
                # Update stored output
                self.last_output[command_id] = output
            else:
                # First time, just store and show
                self.last_output[command_id] = output
                self.output_area.show_output(output, command_label, shell_command)
                # Show hint for compare mode
                self.output_area.append_output("\n[Compare Mode] Click again to compare changes")
        else:
            self.output_area.show_output(output, command_label, shell_command)

        self.output_area.set_state("completed")

    def _on_command_error(self, error: str):
        """Handle command execution error."""
        self.is_executing = False
        self.is_streaming = False

        # Reset card running state
        if self.current_command:
            card = self._get_card_for_command(self.current_command)
            if card:
                card.set_running(False)

        self.output_area.show_error(error)
        self.output_area.set_state("error")

        # Stop auto-refresh on error
        if self.is_auto_refreshing:
            self._stop_auto_refresh()

    def _on_streaming_started(self):
        """Handle streaming command started."""
        pass  # Header already added in _execute_streaming_command

    def _on_streaming_line(self, line: str):
        """Handle streaming command output line."""
        self.output_area.append_output(line)

    def _on_streaming_stopped(self):
        """Handle streaming command stopped."""
        self.is_streaming = False

        if self.current_command:
            card = self._get_card_for_command(self.current_command)
            if card:
                card.set_running(False)

        self.output_area.set_state("completed")

    def _on_auto_refresh_toggled(self, active: bool):
        """Handle auto-refresh toggle."""
        sender_card = self.sender()
        if not isinstance(sender_card, CommandCard):
            return

        if active:
            # Stop any existing auto-refresh
            if self.is_auto_refreshing and self.auto_refresh_command:
                self._stop_auto_refresh()

            # Start new auto-refresh
            self._start_auto_refresh(sender_card.command)
        else:
            # Stop auto-refresh
            self._stop_auto_refresh()

    def _on_auto_refresh_interval_changed(self, seconds: int):
        """Handle auto-refresh interval change."""
        self.adb_service.auto_refresh_manager.set_interval(seconds)

    def _start_auto_refresh(self, command: Command):
        """Start auto-refresh for a command."""
        self.is_auto_refreshing = True
        self.auto_refresh_command = command

        # Update UI
        card = self._get_card_for_command(command)
        if card:
            card.set_auto_refreshing(True)

        # Set interval from card
        if card:
            self.adb_service.auto_refresh_manager.set_interval(card.get_auto_refresh_interval())

        # Execute immediately
        self._execute_auto_refresh_command()

        # Start timer
        self.adb_service.auto_refresh_manager.start()

        self.output_area.set_state("auto_refresh")

    def _stop_auto_refresh(self):
        """Stop auto-refresh."""
        self.is_auto_refreshing = False
        self.adb_service.auto_refresh_manager.stop()

        if self.auto_refresh_command:
            card = self._get_card_for_command(self.auto_refresh_command)
            if card:
                card.set_auto_refreshing(False)

        self.auto_refresh_command = None
        self.output_area.set_state("ready")

    def _on_auto_refresh_trigger(self):
        """Handle auto-refresh timer trigger."""
        if self.is_auto_refreshing and self.auto_refresh_command:
            # Skip if still executing previous command
            if self.is_executing or self.is_streaming:
                return

            self._execute_auto_refresh_command()

    def _execute_auto_refresh_command(self):
        """Execute the auto-refresh command."""
        if not self.auto_refresh_command:
            return

        self.is_executing = True

        # Check device status first
        is_connected, _ = self.adb_service.check_device()
        if not is_connected:
            self._stop_auto_refresh()
            self.output_area.show_error("Device disconnected")
            self.output_area.set_state("error")
            self._check_device_status()
            return

        self.adb_service.execute_command(
            self.auto_refresh_command.shell_command,
            on_success=self._on_auto_refresh_success,
            on_error=self._on_auto_refresh_error
        )

    def _on_auto_refresh_success(self, output: str):
        """Handle successful auto-refresh execution."""
        self.is_executing = False
        # Show output with command info for auto-refresh
        if self.auto_refresh_command:
            self.output_area.show_output(output, self.auto_refresh_command.label, self.auto_refresh_command.shell_command)
        else:
            self.output_area.show_output(output)

    def _on_auto_refresh_error(self, error: str):
        """Handle auto-refresh execution error."""
        self.is_executing = False
        self._stop_auto_refresh()
        self.output_area.show_error(error)
        self.output_area.set_state("error")

    def _on_stop_requested(self):
        """Handle stop button click or Escape shortcut."""
        self._stop_all_operations()
        self.output_area.clear_output()
        self.output_area.set_state("ready")

    def _on_clear_output(self):
        """Handle clear output request."""
        # Stop any ongoing operations
        self._stop_all_operations()
        self.output_area.set_state("ready")

    def _save_window_settings(self):
        """Save current window geometry to settings."""
        if self.isMaximized():
            self.settings_service.update_window_settings(
                width=self._saved_geometry.width if self._saved_geometry else 1024,
                height=self._saved_geometry.height if self._saved_geometry else 700,
                x=self._saved_geometry.x if self._saved_geometry else 100,
                y=self._saved_geometry.y if self._saved_geometry else 100,
                maximized=True
            )
        else:
            geometry = self.geometry()
            self.settings_service.update_window_settings(
                width=geometry.width(),
                height=geometry.height(),
                x=geometry.x(),
                y=geometry.y(),
                maximized=False
            )

    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up any running operations
        self._stop_all_operations()

        # Save window settings
        self._save_window_settings()

        super().closeEvent(event)
