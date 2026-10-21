"""
Command model for ADB Debug Dashboard.

Defines the data structure for ADB shell commands.
Commands are loaded from the YAML configuration file.
"""

from dataclasses import dataclass
from typing import List


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


def load_commands() -> List[Command]:
    """
    Load commands from the configuration file.

    Returns:
        List of Command objects from config, or defaults if config is invalid.
    """
    from ..services.config_service import ConfigService
    config_service = ConfigService()
    return config_service.load_commands()


# For backwards compatibility, provide COMMANDS as module-level variable
# This will be loaded lazily on first access
_COMMANDS: List[Command] = None


def get_commands() -> List[Command]:
    """
    Get the list of commands, loading from config if not already loaded.

    Returns:
        List of Command objects
    """
    global _COMMANDS
    if _COMMANDS is None:
        _COMMANDS = load_commands()
    return _COMMANDS


# Module-level COMMANDS for backwards compatibility
# This property allows the existing code to work without changes
class _CommandsProxy:
    """Proxy object that loads commands on first access."""

    def __iter__(self):
        return iter(get_commands())

    def __getitem__(self, index):
        return get_commands()[index]

    def __len__(self):
        return len(get_commands())

    def __repr__(self):
        return repr(get_commands())


COMMANDS = _CommandsProxy()
