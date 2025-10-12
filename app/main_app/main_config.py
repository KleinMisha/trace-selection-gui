"""
Values required for the main app component

The main entry point will register this at the ConfigManager
"""

from dataclasses import dataclass, field
from pathlib import Path

from app.type_definitions import Color


@dataclass
class MainConfig:
    """
    NOTE: Default values are purely for (unit)tests, as when running the application, values will be read from file first.
    """

    unsaved_changes_on_color: Color = "coral"
    unsaved_changes_off_color: Color = "white"

    # todo: change to more convenient format to edit in config file later?
    keyboard_shortcuts: dict[str, tuple[str, str]] = field(
        default_factory=lambda: {
            "actionOpen": ("Open...", "Ctrl+O"),
            "actionSave": ("Save...", "Ctrl+S"),
            "actionSaveAs": ("Save as...", "Ctrl+Shift+S"),
        }
    )

    # output file paths (can be used to speed up workflow slightly: avoids needing to go through dialogue window every time)
    default_path_to_labels: Path = Path("")
    default_path_to_section_labels: Path = Path("")
