"""
Values required for this component

The main entry point will register this at the ConfigManager
"""

from dataclasses import dataclass
from typing import Any, Self, Type

from app.theme_types import Color


@dataclass
class InterActivePlotConfig:
    min_time: float = 0.0
    max_time: float = 3600.0
    min_height: float = -1.0
    max_height: float = 1.0

    vertical_line_color: Color = "skyblue"
    data_line_color: Color = "black"

    @classmethod
    def from_raw(cls: Type[Self], settings: dict[str, Any]) -> Self:
        """In this case the entries in the config file directly match the signature of this class"""
        return cls(**settings)
