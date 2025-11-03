"""
Model knows of the available themes and style sheets
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from string import Template

from app.theme_types import Color, Theme, ThemeMode


@dataclass
class ThemeModel:
    """Handles theme selection"""

    current_theme: ThemeMode
    stylesheet_template: Path
    color_palette: dict[str, Color] = field(default_factory=dict)

    def create_theme(self) -> Theme:
        """use the palette information to create the Theme object (the information send by the Controller to other parts of App, via MainApp)"""
        return Theme(name=self.current_theme.value, **self.color_palette)

    def load_palette(self) -> None:
        """Load the color palette from the JSON file"""

        # Assumes file naming based on the theme variable
        palette_file = (
            Path(__file__).parent / "themes" / f"{self.current_theme.value}.json"
        )
        with open(palette_file, "r", encoding="utf-8") as palette_json:
            self.color_palette = json.load(palette_json)

    def construct_stylesheet(self) -> str:
        """Add the colors from the selected palette into the base style sheet"""
        if not self.color_palette:
            self.load_palette()
        template = Template(self.stylesheet_template.read_text())
        return template.substitute(self.color_palette)
