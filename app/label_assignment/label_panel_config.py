"""
Values required for this component

The main entry point will register this at the ConfigManager
"""

from dataclasses import dataclass

from app.type_definitions import Color


@dataclass
class LabelPanelConfig:
    light_off_color: Color = "white"
    light_on_color: Color = "green"
