"""
Values required for this component

The main entry point will register this at the ConfigManager
"""

from dataclasses import dataclass
from typing import Any, Self, Type

from app.theme_types import Color


@dataclass
class InterActivePlotConfig:
    max_time: float | None = 3600.0
    min_time: float | None = 0.0
    min_height: float | None = -1.0
    max_height: float | None = 1.0

    vertical_line_color: Color | None = None
    data_line_color: Color | None = None

    @classmethod
    def from_raw(cls: Type[Self], settings: dict[str, Any]) -> Self:
        """In this case the entries in the config file directly match the signature of this class"""
        return cls(**settings)
