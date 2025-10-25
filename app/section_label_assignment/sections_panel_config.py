"""
Values required for this component

The main entry point will register this at the ConfigManager
"""

from dataclasses import dataclass
from typing import Any, Self, Type

from app.keyboard_shortcuts import clean_shortcut
from app.section_label_assignment.sections_panel_shortcut_items import (
    SectionsPanelShortcutID as ShortcutID,
)
from app.type_definitions import Color


@dataclass
class SectionsPanelConfig:
    """
    NOTE: Default values are purely for (unit)tests, as when running the application, values will be read from file first.
    """

    # colors
    color_indicator_off: Color = "white"
    color_indicator_on: Color = "green"

    # keyboard shortcuts
    keyboard_shortcut_assign_label: str = "Alt++"
    keyboard_shortcut_unassign_label: str = "Alt+-"
    keyboard_shortcut_next_label: str = "Alt+Up"
    keyboard_shortcut_previous_label: str = "Alt+Down"
    keyboard_shortcut_next_section: str = "Alt+Shift+Up"
    keyboard_shortcut_previous_section: str = "Alt+Shift+Down"

    @classmethod
    def from_raw(cls: Type[Self], settings: dict[str, Any]) -> Self:
        """specify how to parse the dictionary of JSON / TOML data supplied. Allows the user to provide values in a more user-friendly manner."""
        colors = settings["colors"]
        shortcuts = {
            key: clean_shortcut(shortcut)
            for key, shortcut in settings["keyboard_shortcuts"].items()
        }
        return cls(
            color_indicator_off=colors["unassigned"],
            color_indicator_on=colors["assigned"],
            keyboard_shortcut_assign_label=shortcuts["assign_label"],
            keyboard_shortcut_unassign_label=shortcuts["unassign_label"],
            keyboard_shortcut_next_label=shortcuts["next_label"],
            keyboard_shortcut_previous_label=shortcuts["previous_label"],
            keyboard_shortcut_next_section=shortcuts["next_section"],
            keyboard_shortcut_previous_section=shortcuts["previous_section"],
        )

    def get_shortcuts(self) -> dict[ShortcutID, str]:
        """dictionary of all keyboard shortcuts for this component"""
        return {
            ShortcutID.ASSIGN: self.keyboard_shortcut_assign_label,
            ShortcutID.UNASSIGN: self.keyboard_shortcut_unassign_label,
            ShortcutID.NEXT_LABEL: self.keyboard_shortcut_next_label,
            ShortcutID.PREVIOUS_LABEL: self.keyboard_shortcut_previous_label,
            ShortcutID.NEXT_SECTION: self.keyboard_shortcut_next_section,
            ShortcutID.PREVIOUS_SECTION: self.keyboard_shortcut_previous_section,
        }
