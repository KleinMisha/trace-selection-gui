"""
Values required for the main app component

The main entry point will register this at the ConfigManager
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self, Type

from app.keyboard_shortcuts import clean_shortcut
from app.main_app.main_shortcut_items import MainShortcutID as ShortcutID
from app.theme_types import Color


@dataclass
class MainConfig:
    """
    NOTE: Default values are purely for (unit)tests, as when running the application, values will be read from file first.
    """

    # colors
    color_unsaved_changes: Color = "coral"
    color_no_unsaved_changes: Color = "white"

    # keyboard shortcuts
    keyboard_shortcut_menu_file_open: str = "Ctrl+O"
    keyboard_shortcut_menu_file_save: str = "Ctrl+S"
    keyboard_shortcut_menu_file_save_as: str = "Ctrl+Shift+S"
    keyboard_shortcut_next_trace: str = "Ctrl+Right"
    keyboard_shortcut_previous_trace: str = "Ctrl+Left"

    # output file paths (can be used to speed up workflow slightly: avoids needing to go through dialogue window every time)
    default_path_to_labels: Path = Path("")
    default_path_to_section_labels: Path = Path("")

    @classmethod
    def from_raw(cls: Type[Self], settings: dict[str, Any]) -> Self:
        """specify how to parse the dictionary of JSON / TOML data supplied. Allows the user to provide values in a more user-friendly manner."""
        colors = settings["colors"]
        shortcuts = {
            key: clean_shortcut(shortcut)
            for key, shortcut in settings["keyboard_shortcuts"].items()
        }
        paths = settings["default_file_paths"]
        return cls(
            color_unsaved_changes=colors["unsaved_changes"],
            color_no_unsaved_changes=colors["no_unsaved_changes"],
            keyboard_shortcut_menu_file_open=shortcuts["menu.file.open"],
            keyboard_shortcut_menu_file_save=shortcuts["menu.file.save"],
            keyboard_shortcut_menu_file_save_as=shortcuts["menu.file.save_as"],
            keyboard_shortcut_next_trace=shortcuts["next_trace"],
            keyboard_shortcut_previous_trace=shortcuts["previous_trace"],
            default_path_to_labels=Path(paths["labels"]),
            default_path_to_section_labels=Path(paths["section_labels"]),
        )

    # API for MainController
    def get_shortcuts(self) -> dict[ShortcutID, str]:
        """dictionary of all keyboard shortcuts for this component"""
        return {
            ShortcutID.MENU_FILE_OPEN: self.keyboard_shortcut_menu_file_open,
            ShortcutID.MENU_FILE_SAVE: self.keyboard_shortcut_menu_file_save,
            ShortcutID.MENU_FILE_SAVE_AS: self.keyboard_shortcut_menu_file_save_as,
            ShortcutID.NEXT_TRACE: self.keyboard_shortcut_next_trace,
            ShortcutID.PREVIOUS_TRACE: self.keyboard_shortcut_previous_trace,
        }
