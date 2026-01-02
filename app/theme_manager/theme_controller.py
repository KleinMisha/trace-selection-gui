"""
Controller: Handles toggling between styles / loading them from files, etc.
"""

from pathlib import Path
from typing import Callable, Protocol

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from app.core.theme_types import Color, Theme, ThemeMode
from app.theme_manager.theme_config import ThemeConfig

# Todo: Move constants into a configuration file
THEMES_DIR = Path(__file__).parent / "themes"


class Model(Protocol):
    """API for the ThemeModel"""

    current_theme: ThemeMode
    color_palette: dict[str, Color]
    stylesheet_template: Path

    def load_palette(self) -> None: ...
    def construct_stylesheet(self) -> str: ...
    def create_theme(self) -> Theme: ...


class View(Protocol):
    """API for the ThemeView"""

    def connect_dark_mode(self, callback: Callable[[bool], None]) -> None: ...


class ThemeController(QObject):
    """Adds 'global' appearance selection to the application"""

    _selected_theme_signal = pyqtSignal(Theme)

    def __init__(self, model: Model, view: View, config: ThemeConfig) -> None:
        super().__init__()
        self.model = model
        self.view = view
        self.config = config

        # connect callbacks :: Listening to the View's signals
        self.view.connect_dark_mode(self.handle_dark_mode_toggle)

    # handling signals from the View
    def handle_dark_mode_toggle(self, turn_on: bool) -> None:
        """update the theme/stylesheet in the model. The view will already change appearance (using checkbox widget)"""
        new_theme_mode = ThemeMode.DARK if turn_on else ThemeMode.LIGHT
        self.model.current_theme = new_theme_mode
        self._apply_theme()

        # pass on information to main application:
        new_theme = self.model.create_theme()
        self._send_selected_theme_signal(new_theme)

    # known to the main controller:
    def connect_selected_theme_signal(self, callback: Callable[[Theme], None]) -> None:
        self._selected_theme_signal.connect(callback)

    def get_and_apply_default_theme(self) -> Theme:
        """use theme specified in configuration file"""
        self.model.current_theme = self.config.default_mode
        self._apply_theme()
        return self.model.create_theme()

    # internal logic
    def _apply_theme(self) -> None:
        """
        Change theme on the QApplication level
        ----
        Individual Views will be responsible for additional colors to be set in accordance with a theme.
        """

        # if the app is running, read the "Qt style sheet (QSS)" and apply it at the top level
        app = QApplication.instance()
        if isinstance(app, QApplication):
            self.model.load_palette()
            qss_contents = self.model.construct_stylesheet()
            app.setStyleSheet(qss_contents)

    # send signals to MainController
    def _send_selected_theme_signal(self, theme: Theme) -> None:
        self._selected_theme_signal.emit(theme)
