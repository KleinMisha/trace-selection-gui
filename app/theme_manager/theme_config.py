"""
Configurable values relating to the theme to be chosen
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self, Type

from app.theme_types import ThemeMode


@dataclass
class ThemeConfig:
    themes_dir: Path = Path(__file__).parent / "themes"
    template_stylesheet: Path = Path(__file__) / "themes" / "base.qss"
    default_mode: ThemeMode = ThemeMode.LIGHT

    @classmethod
    def from_raw(cls: Type[Self], settings: dict[str, Any]) -> Self:
        """specify how to parse the dictionary of JSON / TOML data supplied. Allows the user to provide values in a more user-friendly manner."""
        default_mode = (
            ThemeMode.LIGHT
            if settings["default_theme"].lower() == "light"
            else ThemeMode.DARK
        )
        return cls(
            themes_dir=Path(settings["themes_dir"]),
            default_mode=default_mode,
            template_stylesheet=Path(settings["template_stylesheet"]),
        )
