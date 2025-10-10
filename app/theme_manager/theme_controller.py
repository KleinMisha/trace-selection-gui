"""
Controller: Handles toggling between styles / loading them from files, etc.
"""

from pathlib import Path
from typing import Callable, Protocol

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication

from app.state_variables import Theme

# Todo: Move constants into a configuration file
THEMES_DIR = Path(__file__).parent / "themes"


class Model(Protocol):
    """API for the ThemeModel"""

    current_theme: Theme
    color_palette: dict[str, str] | None
    stylesheet_template: Path

    def load_palette(self) -> None: ...
    def construct_stylesheet(self) -> str: ...


class View(Protocol):
    """API for the ThemeView"""

    def connect_dark_mode(self, callback: Callable[[bool], None]) -> None: ...


class ThemeController(QObject):
    """Adds 'global' appearance selection to the application"""

    def __init__(self, model: Model, view: View) -> None:
        super().__init__()
        self.model = model
        self.view = view

        # connect callbacks :: Listening to the View's signals
        self.view.connect_dark_mode(self.handle_dark_mode_toggle)

    # handling signals from the View
    def handle_dark_mode_toggle(self, turn_on: bool) -> None:
        """update the theme/stylesheet in the model. The view will already change appearance (using checkbox widget)"""
        new_theme = Theme.DARK if turn_on else Theme.LIGHT
        self.model.current_theme = new_theme
        self.apply_theme()

    # internal logic
    def apply_theme(self) -> None:
        """
        Change theme on the QApplication level
        ----
        Stylesheets assigned to individual widgets will overwrite these global stylings
        """

        # if the app is running, read the "Qt style sheet (QSS)" and apply it at the top level
        app = QApplication.instance()
        if isinstance(app, QApplication):
            self.model.load_palette()
            qss_contents = self.model.construct_stylesheet()
            app.setStyleSheet(qss_contents)
