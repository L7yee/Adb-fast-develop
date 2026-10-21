"""
ADB service layer for device detection and command execution.

Handles:
- Device detection via `adb devices` command
- Shell command execution via `adb shell <command>`
- Asynchronous/non-blocking command execution
- Streaming command execution for getevent
- Error handling with actionable guidance
"""

import subprocess
import re
from enum import Enum
from typing import Callable, Optional, Tuple
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QTimer


class DeviceStatus(Enum):
    """Device connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class ErrorMessage:
    """
    Improved error messages with actionable guidance.

    Each error type includes:
    - A short title
    - Detailed guidance on how to resolve the issue
    """

    ADB_NOT_FOUND = (
        "ADB is not installed or not in PATH",
        "To fix this:\n"
        "1. Install Android SDK Platform Tools\n"
        "2. Add the platform-tools directory to your system PATH\n"
        "3. Verify with 'adb version' in a command prompt\n"
        "4. Restart the application after installing"
    )

    DEVICE_NOT_CONNECTED = (
        "Device not connected",
        "To fix this:\n"
        "1. Connect your Android device via USB cable\n"
        "2. Enable USB debugging in Developer Options on your device\n"
        "3. Accept the USB debugging authorization prompt on your device\n"
        "4. Try a different USB cable or port if needed"
    )

    DEVICE_UNAUTHORIZED = (
        "Device unauthorized",
        "To fix this:\n"
        "1. Check your device screen for an authorization prompt\n"
        "2. Tap 'Allow' to grant USB debugging access\n"
        "3. Enable 'Always allow from this computer' for convenience\n"
        "4. Reconnect the device if the prompt doesn't appear"
    )

    PERMISSION_DENIED = (
        "Permission denied",
        "To fix this:\n"
        "1. Ensure USB debugging is authorized on your device\n"
        "2. Check the authorization prompt on your device screen\n"
        "3. The command may require root access on some devices\n"
        "4. Try 'adb root' if you have a rooted device"
    )

    COMMAND_TIMEOUT = (
        "Command timed out",
        "The device may be unresponsive. Try:\n"
        "1. Disconnect and reconnect the device\n"
        "2. Restart the ADB server: 'adb kill-server' then 'adb start-server'\n"
        "3. Reboot the device if it's frozen\n"
        "4. Try a simpler command first to test connectivity"
    )

    ACTIVITY_NOT_FOUND = (
        "Activity not found",
        "This app or feature may not be installed on your device.\n"
        "The engineer mode app varies by device manufacturer:\n"
        "- Unisoc Engineer Mode: Available on Unisoc/Spreadtrum chipsets\n"
        "- MTK Engineer Mode: Available on MediaTek chipsets\n"
        "- MTK DebugLogger: May require separate installation"
    )

    EMPTY_OUTPUT = (
        "No output received",
        "The command completed but returned no data.\n"
        "This could mean:\n"
        "1. The file or resource does not exist on this device\n"
        "2. The path is different on this Android version\n"
        "3. You may need root access to read this file\n"
        "4. The feature is not supported on this device"
    )

    FILE_NOT_FOUND = (
        "File or resource not found",
        "The requested file or resource does not exist on the device.\n"
        "This is common for:\n"
        "- Audio register files (device-specific paths)\n"
        "- GPIO debug files (may require root)\n"
        "- Device-specific engineer mode apps"
    )

    MULTIPLE_DEVICES = (
        "Multiple devices connected",
        "This application supports only one device at a time.\n"
        "To fix this:\n"
        "1. Disconnect all but one device\n"
        "2. Or use 'adb devices' to identify which to disconnect"
    )

    @classmethod
    def format(cls, error_type: Tuple[str, str]) -> str:
        """Format an error type tuple into a displayable message."""
        title, guidance = error_type
        return f"{title}\n\n{guidance}"


class CommandWorker(QThread):
    """Worker thread for executing ADB commands."""

    success = pyqtSignal(str)  # Emits command output
    error = pyqtSignal(str)    # Emits error message

    COMMAND_TIMEOUT = 30  # seconds

    def __init__(self, shell_command: str, use_root: bool = False, parent=None):
        super().__init__(parent)
        self.shell_command = shell_command
        self.use_root = use_root

    def run(self):
        """Execute the ADB shell command in a background thread."""
        try:
            # Build full command
            if self.use_root:
                # Use su for root access
                # Different Android su implementations have different syntax
                # Try: su 0 -c "command" (works on most devices)
                full_command = f'adb shell "su 0 {self.shell_command}"'
            else:
                full_command = f"adb shell {self.shell_command}"

            # Execute with timeout
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.COMMAND_TIMEOUT,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    self.success.emit(output)
                else:
                    self.error.emit(ErrorMessage.format(ErrorMessage.EMPTY_OUTPUT))
            else:
                # Analyze the error for better messaging
                error_msg = self._analyze_error(result.stderr, result.returncode)
                self.error.emit(error_msg)

        except subprocess.TimeoutExpired:
            self.error.emit(ErrorMessage.format(ErrorMessage.COMMAND_TIMEOUT))
        except Exception as e:
            self.error.emit(f"Execution error: {str(e)}")

    def _analyze_error(self, stderr: str, returncode: int) -> str:
        """Analyze error output and return actionable message."""
        stderr_lower = stderr.lower() if stderr else ""

        # Check for specific error patterns
        if "permission denied" in stderr_lower:
            return ErrorMessage.format(ErrorMessage.PERMISSION_DENIED)
        elif "not found" in stderr_lower:
            if "activity" in stderr_lower or "am start" in stderr_lower:
                return ErrorMessage.format(ErrorMessage.ACTIVITY_NOT_FOUND)
            return ErrorMessage.format(ErrorMessage.FILE_NOT_FOUND)
        elif "no such file" in stderr_lower:
            return ErrorMessage.format(ErrorMessage.FILE_NOT_FOUND)
        elif "error: device unauthorized" in stderr_lower:
            return ErrorMessage.format(ErrorMessage.DEVICE_UNAUTHORIZED)
        elif "error: device not found" in stderr_lower or "error: no devices" in stderr_lower:
            return ErrorMessage.format(ErrorMessage.DEVICE_NOT_CONNECTED)

        # Default error message
        error_msg = stderr.strip() if stderr else f"Command failed with code {returncode}"
        return f"Error: {error_msg}"


class StreamingCommandWorker(QThread):
    """Worker thread for streaming ADB commands like getevent -l."""

    line_received = pyqtSignal(str)  # Emits each line as received
    started_signal = pyqtSignal()
    stopped_signal = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, shell_command: str, parent=None):
        super().__init__(parent)
        self.shell_command = shell_command
        self._process = None
        self._is_running = False

    def run(self):
        """Execute command and stream output line by line."""
        try:
            full_command = f"adb shell {self.shell_command}"
            self._is_running = True
            self.started_signal.emit()

            # Use subprocess.Popen for streaming
            self._process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            # Read stdout line by line
            if self._process.stdout:
                while self._is_running:
                    line = self._process.stdout.readline()
                    if not line:
                        break
                    if self._is_running:
                        self.line_received.emit(line.rstrip('\n'))

            self.stopped_signal.emit()

        except Exception as e:
            if self._is_running:
                self.error.emit(f"Streaming error: {str(e)}")

        self._is_running = False

    def stop(self):
        """Terminate the streaming process."""
        self._is_running = False
        if self._process:
            try:
                self._process.kill()
            except Exception:
                pass


class DeviceCheckWorker(QThread):
    """Worker thread for checking device status (non-blocking)."""

    finished = pyqtSignal(bool, str, bool, str)  # (is_connected, error_type, has_root, root_message)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        """Check device and root status in background."""
        is_connected = False
        error_type = ""
        has_root = False
        root_message = ""

        try:
            # Check adb devices
            result = subprocess.run(
                "adb devices",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                devices = []
                unauthorized = []

                for line in lines[1:]:
                    line = line.strip()
                    if line and '\t' in line:
                        device_id, status = line.split('\t', 1)
                        if status == 'device':
                            devices.append(device_id)
                        elif status == 'unauthorized':
                            unauthorized.append(device_id)

                if len(devices) == 1:
                    is_connected = True
                    # Check root status
                    has_root, root_message = self._check_root()
                elif len(unauthorized) > 0:
                    error_type = "unauthorized"
                elif len(devices) > 1:
                    error_type = "multiple"
            else:
                error_type = "adb_error"

        except subprocess.TimeoutExpired:
            error_type = "timeout"
        except Exception as e:
            error_type = str(e)

        self.finished.emit(is_connected, error_type, has_root, root_message)

    def _check_root(self):
        """Check root status."""
        try:
            result = subprocess.run(
                "adb shell id",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if "uid=0" in result.stdout:
                return True, "Running as root (uid=0)"

            # Try su
            result2 = subprocess.run(
                "adb shell su 0 id",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if "uid=0" in result2.stdout:
                return True, "Root access via su"

            return False, "No root access"

        except Exception:
            return False, "Root check failed"


class AutoRefreshManager(QObject):
    """Manages auto-refresh polling for commands."""

    refresh_triggered = pyqtSignal()  # Emitted when refresh should occur

    # Available intervals in seconds
    INTERVALS = [1, 5, 10, 30]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_timeout)
        self._interval_ms = 5000  # Default 5 seconds
        self._is_active = False

    def set_interval(self, seconds: int):
        """Set refresh interval in seconds."""
        if seconds in self.INTERVALS:
            self._interval_ms = seconds * 1000
            if self._is_active:
                self._timer.setInterval(self._interval_ms)

    def get_interval(self) -> int:
        """Get current interval in seconds."""
        return self._interval_ms // 1000

    def start(self):
        """Start auto-refresh timer."""
        if not self._is_active:
            self._is_active = True
            self._timer.start(self._interval_ms)

    def stop(self):
        """Stop auto-refresh timer."""
        self._is_active = False
        self._timer.stop()

    def is_active(self) -> bool:
        """Return whether auto-refresh is active."""
        return self._is_active

    def _on_timer_timeout(self):
        """Handle timer timeout."""
        if self._is_active:
            self.refresh_triggered.emit()


class ADBService(QObject):
    """Service for ADB device detection and command execution."""

    # Signal for async device check result
    device_check_finished = pyqtSignal(bool, str, bool, str)  # (is_connected, error_type, has_root, root_message)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._device_id: Optional[str] = None
        self._current_worker: Optional[CommandWorker] = None
        self._streaming_worker: Optional[StreamingCommandWorker] = None
        self._device_check_worker: Optional[DeviceCheckWorker] = None
        self.auto_refresh_manager = AutoRefreshManager(self)
        self._has_root = False

    def is_adb_available(self) -> bool:
        """Check if ADB is installed and in PATH."""
        try:
            result = subprocess.run(
                "adb version",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_device_async(self):
        """Check device status asynchronously (non-blocking)."""
        if self._device_check_worker and self._device_check_worker.isRunning():
            return  # Already checking

        self._device_check_worker = DeviceCheckWorker(self)
        self._device_check_worker.finished.connect(self._on_device_check_finished)
        self._device_check_worker.start()

    def _on_device_check_finished(self, is_connected: bool, error_type: str, has_root: bool, root_message: str):
        """Handle async device check result."""
        if is_connected:
            # Get device ID from adb devices output
            try:
                result = subprocess.run(
                    "adb devices",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if '\tdevice' in line:
                        self._device_id = line.split('\t')[0]
                        break
            except Exception:
                pass
        else:
            self._device_id = None

        self._has_root = has_root
        self.device_check_finished.emit(is_connected, error_type, has_root, root_message)

    def request_root(self) -> Tuple[bool, str]:
        """
        Request root access on the device.

        First tries 'adb root', then falls back to 'adb shell su -c id'.

        Returns:
            Tuple of (success, message)
        """
        if not self._device_id:
            return False, "No device connected"

        # Method 1: Try adb root (works on userdebug/eng builds)
        try:
            result = subprocess.run(
                "adb root",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            # Check if root was successful
            if "restarting adbd as root" in result.stdout or "already running as root" in result.stdout:
                self._has_root = True
                return True, "Root access granted via adb root"

            # If adb root failed, try su
            if "cannot run as root" in result.stdout or "adbd cannot run as root" in result.stdout:
                # Method 2: Try su command
                result2 = subprocess.run(
                    "adb shell su -c id",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if "uid=0" in result2.stdout:
                    self._has_root = True
                    return True, "Root access granted via su"
                else:
                    return False, "Device not rooted or su permission denied"

            # Check current user
            result3 = subprocess.run(
                "adb shell id",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if "uid=0" in result3.stdout:
                self._has_root = True
                return True, "Already running as root"

            return False, "Root access denied"

        except subprocess.TimeoutExpired:
            return False, "Root request timed out"
        except Exception as e:
            return False, f"Root request failed: {str(e)}"

    def has_root(self) -> bool:
        """Check if root access is available."""
        return self._has_root

    def check_root_status(self) -> Tuple[bool, str]:
        """
        Check current root status without requesting.

        Returns:
            Tuple of (has_root, method)
        """
        try:
            # Check if running as root
            result = subprocess.run(
                "adb shell id",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if "uid=0" in result.stdout:
                self._has_root = True
                return True, "Running as root (uid=0)"

            # Check if su is available
            result2 = subprocess.run(
                "adb shell 'which su 2>/dev/null || echo not_found'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if "not_found" not in result2.stdout and result2.stdout.strip():
                return False, "su available but not root"

            return False, "No root access"

        except Exception as e:
            return False, str(e)

    def check_device(self) -> Tuple[bool, str]:
        """
        Run 'adb devices' and check for connected device.

        Returns:
            Tuple of (is_connected, error_message)
            - is_connected: True if exactly one authorized device is connected
            - error_message: Error message if check failed, empty string otherwise
        """
        try:
            result = subprocess.run(
                "adb devices",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False, "Failed to run adb devices"

            # Parse output
            lines = result.stdout.strip().split('\n')
            devices = []
            unauthorized = []

            for line in lines[1:]:  # Skip header line
                line = line.strip()
                if line and '\t' in line:
                    device_id, status = line.split('\t', 1)
                    if status == 'device':
                        devices.append(device_id)
                    elif status == 'unauthorized':
                        unauthorized.append(device_id)

            if len(devices) == 1:
                self._device_id = devices[0]
                return True, ""
            elif len(unauthorized) > 0:
                self._device_id = None
                return False, "unauthorized"
            elif len(devices) > 1:
                self._device_id = None
                return False, "multiple"
            else:
                self._device_id = None
                return False, ""

        except Exception as e:
            self._device_id = None
            return False, str(e)

    def get_device_id(self) -> Optional[str]:
        """Get the connected device ID if available."""
        return self._device_id

    def get_device_status(self) -> DeviceStatus:
        """Check if a device is connected and return status."""
        if not self.is_adb_available():
            return DeviceStatus.ERROR

        is_connected, _ = self.check_device()
        if is_connected:
            return DeviceStatus.CONNECTED
        else:
            return DeviceStatus.DISCONNECTED

    def execute_command(
        self,
        shell_command: str,
        on_success: Callable[[str], None],
        on_error: Callable[[str], None],
        use_root: bool = False
    ):
        """
        Execute an ADB shell command asynchronously.
        Results are delivered via callbacks to prevent UI blocking.

        Args:
            shell_command: The shell command to execute
            on_success: Callback for successful execution
            on_error: Callback for error
            use_root: If True, execute with su -c (root access)
        """
        # Check device status first with detailed error reporting
        if not self.is_adb_available():
            on_error(ErrorMessage.format(ErrorMessage.ADB_NOT_FOUND))
            return

        is_connected, error_type = self.check_device()
        if not is_connected:
            if error_type == "unauthorized":
                on_error(ErrorMessage.format(ErrorMessage.DEVICE_UNAUTHORIZED))
            elif error_type == "multiple":
                on_error(ErrorMessage.format(ErrorMessage.MULTIPLE_DEVICES))
            else:
                on_error(ErrorMessage.format(ErrorMessage.DEVICE_NOT_CONNECTED))
            return

        # Cancel any running worker
        self.cancel_current_command()

        # Create and start new worker
        self._current_worker = CommandWorker(shell_command, use_root=use_root)
        self._current_worker.success.connect(on_success)
        self._current_worker.error.connect(on_error)
        self._current_worker.start()

    def execute_streaming_command(
        self,
        shell_command: str,
        on_line: Callable[[str], None],
        on_started: Callable[[], None],
        on_stopped: Callable[[], None],
        on_error: Callable[[str], None]
    ):
        """
        Execute a streaming ADB shell command.
        Output lines are delivered via on_line callback.
        """
        # Check device status first
        if not self.is_adb_available():
            on_error(ErrorMessage.format(ErrorMessage.ADB_NOT_FOUND))
            return

        is_connected, error_type = self.check_device()
        if not is_connected:
            if error_type == "unauthorized":
                on_error(ErrorMessage.format(ErrorMessage.DEVICE_UNAUTHORIZED))
            elif error_type == "multiple":
                on_error(ErrorMessage.format(ErrorMessage.MULTIPLE_DEVICES))
            else:
                on_error(ErrorMessage.format(ErrorMessage.DEVICE_NOT_CONNECTED))
            return

        # Cancel any running streaming worker
        self.stop_streaming()

        # Create and start new streaming worker
        self._streaming_worker = StreamingCommandWorker(shell_command)
        self._streaming_worker.line_received.connect(on_line)
        self._streaming_worker.started_signal.connect(on_started)
        self._streaming_worker.stopped_signal.connect(on_stopped)
        self._streaming_worker.error.connect(on_error)
        self._streaming_worker.start()

    def stop_streaming(self):
        """Stop any active streaming command."""
        if self._streaming_worker and self._streaming_worker.isRunning():
            self._streaming_worker.stop()
            self._streaming_worker = None

    def is_streaming(self) -> bool:
        """Check if a streaming command is active."""
        return self._streaming_worker is not None and self._streaming_worker.isRunning()

    def cancel_current_command(self):
        """Cancel any currently executing command."""
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.terminate()
            self._current_worker.wait()
            self._current_worker = None

    def is_executing(self) -> bool:
        """Check if any command is currently executing."""
        return (self._current_worker is not None and self._current_worker.isRunning())
