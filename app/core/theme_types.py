"""
Everything relating to theme-dependencies
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Sequence, TypeAlias, Union, runtime_checkable

# Type hint for anything that is a proper color input.
Color: TypeAlias = Union[
    str,  # "red", "#FF00FF", "0.5", "C0"
    tuple[float, float, float],  # RGB
    tuple[float, float, float, float],  # RGBA
    Sequence[float],  # list/array of floats
]


class ThemeMode(Enum):
    """Available themes: color palettes are stored in `app/theme_manager/themes/{NAME}.json`"""

    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True)
class Theme:
    """
    A data container with all theme-dependent information
    ----
    Color palettes are stored in `app/theme_manager/themes/{NAME}.json`
    """

    name: str
    primary: Color
    secondary: Color
    accent: Color
    accent_dark: Color
    background: Color
    neutral_accent: Color
    text: Color
    text_box: Color


@runtime_checkable
class SupportsThemeChanges(Protocol):
    """
    A controller that can change colors based on the selected theme
    ----
    main application will use this to determine which components need to listen to the selected theme.

    """

    def apply_theme(self, theme: Theme) -> None:
        """
        Use the colors defined in the theme to call appropriate methods on it's View.
        ---
        May use overwrites defined in the component's Config
        """
