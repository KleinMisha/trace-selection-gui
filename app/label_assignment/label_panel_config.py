"""
Values required for this component

The main entry point will register this at the ConfigManager
"""

from dataclasses import dataclass
from typing import Sequence, TypeAlias, Union

# Type hint for anything that is a proper color input.
Color: TypeAlias = Union[
    str,  # "red", "#FF00FF", "0.5", "C0"
    tuple[float, float, float],  # RGB
    tuple[float, float, float, float],  # RGBA
    Sequence[float],  # list/array of floats
]


@dataclass
class LabelPanelConfig:
    light_off_color: Color = "white"
    light_on_color: Color = "green"
