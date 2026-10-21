"""
Configuration service for ADB Debug Dashboard.

Handles loading and validating command definitions from YAML config files.
"""

import os
import logging
from typing import List, Optional
from dataclasses import dataclass

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


@dataclass
class Command:
    """Represents an ADB shell command."""

    id: str
    label: str
    shell_command: str
    is_clickable: bool
    category: str  # "read", "action", or "streaming"
    auto_refresh_capable: bool = False
    requires_root: bool = False  # Whether this command needs root access


class ConfigService:
    """Service for loading and validating command configuration from YAML."""

    CONFIG_DIR = "config"
    COMMANDS_FILE = "commands.yaml"

    # Valid categories
    VALID_CATEGORIES = {"read", "streaming", "action"}

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the config service.

        Args:
            base_path: Base path for config files. If None, uses the package directory.
        """
        if base_path:
            self._base_path = base_path
        else:
            # Default to the adb_dashboard package directory
            self._base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self._config_path = os.path.join(self._base_path, self.CONFIG_DIR, self.COMMANDS_FILE)

    def load_commands(self) -> List[Command]:
        """
        Load commands from the YAML configuration file.

        Returns:
            List of Command objects. Returns default commands if config is invalid or missing.
        """
        if yaml is None:
            logger.warning("PyYAML not installed, using default commands")
            return self.get_default_commands()

        if not os.path.exists(self._config_path):
            logger.info(f"Config file not found at {self._config_path}, using default commands")
            return self.get_default_commands()

        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config:
                logger.warning("Empty config file, using default commands")
                return self.get_default_commands()

            return self._parse_commands(config)

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}, using default commands")
            return self.get_default_commands()
        except Exception as e:
            logger.error(f"Error loading config: {e}, using default commands")
            return self.get_default_commands()

    def _parse_commands(self, config: dict) -> List[Command]:
        """
        Parse commands from the loaded config dictionary.

        Args:
            config: Parsed YAML config dictionary

        Returns:
            List of Command objects
        """
        commands = []
        seen_ids = set()

        raw_commands = config.get("commands", [])

        if not isinstance(raw_commands, list):
            logger.warning("'commands' should be a list, using default commands")
            return self.get_default_commands()

        for i, cmd_data in enumerate(raw_commands):
            if not isinstance(cmd_data, dict):
                logger.warning(f"Command at index {i} is not a dictionary, skipping")
                continue

            # Validate required fields
            cmd_id = cmd_data.get("id")
            if not cmd_id:
                logger.warning(f"Command at index {i} missing 'id', skipping")
                continue

            if cmd_id in seen_ids:
                logger.warning(f"Duplicate command id '{cmd_id}', skipping")
                continue

            label = cmd_data.get("label")
            if not label:
                logger.warning(f"Command '{cmd_id}' missing 'label', using id as label")
                label = cmd_id

            shell_command = cmd_data.get("shell_command")
            if not shell_command:
                logger.warning(f"Command '{cmd_id}' missing 'shell_command', skipping")
                continue

            # Validate and default category
            category = cmd_data.get("category", "read")
            if category not in self.VALID_CATEGORIES:
                logger.warning(f"Command '{cmd_id}' has invalid category '{category}', defaulting to 'read'")
                category = "read"

            # Parse auto_refresh_capable
            auto_refresh = bool(cmd_data.get("auto_refresh_capable", False))

            # Parse requires_root
            requires_root = bool(cmd_data.get("requires_root", False))

            # Streaming commands should not have auto_refresh
            if category == "streaming" and auto_refresh:
                logger.info(f"Streaming command '{cmd_id}' cannot have auto_refresh, setting to false")
                auto_refresh = False

            commands.append(Command(
                id=cmd_id,
                label=label,
                shell_command=shell_command,
                is_clickable=True,
                category=category,
                auto_refresh_capable=auto_refresh,
                requires_root=requires_root
            ))

            seen_ids.add(cmd_id)

        if not commands:
            logger.warning("No valid commands found in config, using default commands")
            return self.get_default_commands()

        logger.info(f"Loaded {len(commands)} commands from config")
        return commands

    def validate_config(self) -> tuple:
        """
        Validate the configuration file.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if yaml is None:
            return False, "PyYAML not installed"

        if not os.path.exists(self._config_path):
            return False, f"Config file not found at {self._config_path}"

        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config:
                return False, "Config file is empty"

            if "commands" not in config:
                return False, "Missing 'commands' section"

            if not isinstance(config["commands"], list):
                return False, "'commands' should be a list"

            return True, "Valid"

        except yaml.YAMLError as e:
            return False, f"YAML syntax error: {e}"
        except Exception as e:
            return False, f"Error reading config: {e}"

    def get_config_path(self) -> str:
        """Get the path to the configuration file."""
        return self._config_path

    @staticmethod
    def get_default_commands() -> List[Command]:
        """
        Return hardcoded default commands as fallback.

        These are used when the config file is missing or invalid.
        """
        return [
            # Auto-refresh capable read commands
            Command(
                id="memory_info",
                label="Memory Info",
                shell_command="cat /proc/meminfo",
                is_clickable=True,
                category="read",
                auto_refresh_capable=True
            ),
            Command(
                id="brightness",
                label="Brightness",
                shell_command="cat /sys/class/leds/lcd-backlight/brightness",
                is_clickable=True,
                category="read",
                auto_refresh_capable=True
            ),
            Command(
                id="gpio_status",
                label="GPIO Status",
                shell_command="cat /sys/kernel/debug/gpio",
                is_clickable=True,
                category="read",
                auto_refresh_capable=True
            ),
            Command(
                id="interrupt_info",
                label="Interrupt Info",
                shell_command="cat /proc/interrupts",
                is_clickable=True,
                category="read",
                auto_refresh_capable=True
            ),
            # Standard read commands
            Command(
                id="serial_port_info",
                label="Serial Port Info",
                shell_command="cat /proc/tty/driver/serial",
                is_clickable=True,
                category="read",
                auto_refresh_capable=False
            ),
            Command(
                id="audio_register",
                label="Audio Register Info",
                shell_command="cat /sys/kernel/debug/mtksocaudio",
                is_clickable=True,
                category="read",
                auto_refresh_capable=False
            ),
            # Streaming command
            Command(
                id="get_events",
                label="Get Events",
                shell_command="getevent -l",
                is_clickable=True,
                category="streaming",
                auto_refresh_capable=False
            ),
            # Action commands
            Command(
                id="unisoc_engineer_mode",
                label="Unisoc Engineer Mode",
                shell_command="am start -n com.sprd.engineermode/.EngineerModeActivity",
                is_clickable=True,
                category="action",
                auto_refresh_capable=False
            ),
            Command(
                id="mtk_engineer_mode",
                label="MTK Engineer Mode",
                shell_command="am start com.mediatek.engineermode/com.mediatek.engineermode.EngineerMode",
                is_clickable=True,
                category="action",
                auto_refresh_capable=False
            ),
            Command(
                id="mtk_debug_logger",
                label="MTK DebugLogger",
                shell_command="am start com.debug.loggerui/com.debug.loggerui.MainActivity",
                is_clickable=True,
                category="action",
                auto_refresh_capable=False
            ),
        ]
