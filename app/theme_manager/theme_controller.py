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
    stylesheet_file: Path | None


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
        qss_file = THEMES_DIR / f"{new_theme.value}.qss"

        self.model.current_theme = new_theme
        self.model.stylesheet_file = qss_file
        self._apply_theme()

    # internal logic
    def _apply_theme(self) -> None:
        """
        Change theme on the QApplication level
        ----
        Stylesheets assigned to individual widgets will overwrite these global stylings
        """

        # todo: Check what to do: This should intentionally break the app? This should never be called if no style sheet is known. This is similar to the MissingExperimentError
        # ? or raise some kind of file warning if the file is not known?
        if self.model.stylesheet_file is None:
            return

        # if the app is running, read the "Qt style sheet (QSS)" and apply it at the top level
        app = QApplication.instance()
        if isinstance(app, QApplication):
            qss_contents = self.model.stylesheet_file.read_text()
            app.setStyleSheet(qss_contents)
