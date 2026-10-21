"""
Settings service for ADB Debug Dashboard.

Handles persistence of user preferences including window geometry and file paths.
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


@dataclass
class WindowSettings:
    """Window geometry settings."""
    width: int = 1024
    height: int = 700
    x: int = 100
    y: int = 100
    maximized: bool = False


@dataclass
class FileSettings:
    """File-related settings."""
    last_save_directory: str = ""


@dataclass
class Settings:
    """Application settings container."""
    window: WindowSettings = field(default_factory=WindowSettings)
    file: FileSettings = field(default_factory=FileSettings)
    version: int = 1


class SettingsService:
    """Service for managing application settings persistence."""

    CONFIG_DIR = "config"
    SETTINGS_FILE = "settings.yaml"

    # Constraints for window geometry
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    MAX_WIDTH = 4096
    MAX_HEIGHT = 2160

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the settings service.

        Args:
            base_path: Base path for settings files. If None, uses the package directory.
        """
        if base_path:
            self._base_path = base_path
        else:
            # Default to the adb_dashboard package directory
            self._base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self._settings_path = os.path.join(self._base_path, self.CONFIG_DIR, self.SETTINGS_FILE)
        self._settings: Optional[Settings] = None

    def load_settings(self) -> Settings:
        """
        Load settings from the YAML file.

        Returns:
            Settings object with loaded or default values.
        """
        if yaml is None:
            logger.warning("PyYAML not installed, using default settings")
            return Settings()

        if not os.path.exists(self._settings_path):
            logger.info(f"Settings file not found at {self._settings_path}, using defaults")
            return Settings()

        try:
            with open(self._settings_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data:
                logger.warning("Empty settings file, using defaults")
                return Settings()

            self._settings = self._parse_settings(data)
            return self._settings

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}, using defaults")
            return Settings()
        except Exception as e:
            logger.error(f"Error loading settings: {e}, using defaults")
            return Settings()

    def _parse_settings(self, data: dict) -> Settings:
        """
        Parse settings from the loaded dictionary.

        Args:
            data: Parsed YAML dictionary

        Returns:
            Settings object
        """
        settings = Settings()

        # Parse window settings
        window_data = data.get("window", {})
        if isinstance(window_data, dict):
            settings.window = WindowSettings(
                width=self._clamp(
                    window_data.get("width", 1024),
                    self.MIN_WIDTH, self.MAX_WIDTH
                ),
                height=self._clamp(
                    window_data.get("height", 700),
                    self.MIN_HEIGHT, self.MAX_HEIGHT
                ),
                x=window_data.get("x", 100),
                y=window_data.get("y", 100),
                maximized=window_data.get("maximized", False)
            )

        # Parse file settings
        file_data = data.get("file", {})
        if isinstance(file_data, dict):
            last_dir = file_data.get("last_save_directory", "")
            if last_dir and os.path.isdir(last_dir):
                settings.file.last_save_directory = last_dir
            else:
                settings.file.last_save_directory = ""

        # Parse version
        settings.version = data.get("version", 1)

        return settings

    def save_settings(self, settings: Settings):
        """
        Save settings to the YAML file.

        Args:
            settings: Settings object to save
        """
        if yaml is None:
            logger.warning("PyYAML not installed, cannot save settings")
            return

        # Ensure config directory exists
        config_dir = os.path.dirname(self._settings_path)
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create config directory: {e}")
                return

        data = {
            "window": {
                "width": settings.window.width,
                "height": settings.window.height,
                "x": settings.window.x,
                "y": settings.window.y,
                "maximized": settings.window.maximized
            },
            "file": {
                "last_save_directory": settings.file.last_save_directory
            },
            "version": settings.version
        }

        try:
            with open(self._settings_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            self._settings = settings
            logger.debug("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def get_last_save_directory(self) -> str:
        """
        Get the last used directory for file save dialog.

        Returns:
            Last save directory path, or empty string if not set.
        """
        if self._settings:
            return self._settings.file.last_save_directory
        return ""

    def set_last_save_directory(self, path: str):
        """
        Update the last used save directory.

        Args:
            path: Directory path to save
        """
        if self._settings is None:
            self._settings = Settings()

        # Store only the directory, not the file path
        if os.path.isfile(path):
            path = os.path.dirname(path)

        if os.path.isdir(path):
            self._settings.file.last_save_directory = path
            self.save_settings(self._settings)

    def get_window_settings(self) -> WindowSettings:
        """
        Get the current window settings.

        Returns:
            WindowSettings object
        """
        if self._settings:
            return self._settings.window
        return WindowSettings()

    def update_window_settings(self, width: int, height: int, x: int, y: int, maximized: bool = False):
        """
        Update window geometry settings.

        Args:
            width: Window width
            height: Window height
            x: Window X position
            y: Window Y position
            maximized: Whether window is maximized
        """
        if self._settings is None:
            self._settings = Settings()

        self._settings.window = WindowSettings(
            width=self._clamp(width, self.MIN_WIDTH, self.MAX_WIDTH),
            height=self._clamp(height, self.MIN_HEIGHT, self.MAX_HEIGHT),
            x=x,
            y=y,
            maximized=maximized
        )
        self.save_settings(self._settings)

    def get_settings_path(self) -> str:
        """Get the path to the settings file."""
        return self._settings_path

    @staticmethod
    def _clamp(value: int, min_val: int, max_val: int) -> int:
        """Clamp a value between min and max."""
        return max(min_val, min(max_val, value))
