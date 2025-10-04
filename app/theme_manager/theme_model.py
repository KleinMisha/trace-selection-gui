"""
Model knows of the available themes and style sheets
"""

from dataclasses import dataclass
from pathlib import Path

from app.state_variables import Theme


@dataclass
class ThemeModel:
    """Handles theme selection"""

    current_theme: Theme = Theme.LIGHT
    stylesheet_file: Path | None = None
