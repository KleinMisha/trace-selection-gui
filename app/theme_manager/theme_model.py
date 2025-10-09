"""
Model knows of the available themes and style sheets
"""

import json
from dataclasses import dataclass
from pathlib import Path
from string import Template

from app.state_variables import Theme


@dataclass
class ThemeModel:
    """Handles theme selection"""

    current_theme: Theme
    stylesheet_template: Path
    color_palette: dict[str, str] | None = None

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

        # tell typechecker (and developers) that color palette will be set by the load_palette() method.
        assert self.color_palette is not None

        template = Template(self.stylesheet_template.read_text())
        return template.substitute(self.color_palette)
