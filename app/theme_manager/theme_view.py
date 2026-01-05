"""
View: User-facing components. First implementation is a simple toggle button.
"""

from typing import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.theme_manager.theme_view_ui import Ui_ThemeView


class ThemeView(QWidget, Ui_ThemeView):
    """first version is just a simple toggle button."""

    _dark_mode_signal = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.build_ui()

        # connect listening to user input
        self.themeToggle.toggled.connect(self._send_dark_mode_signal)

    def build_ui(self) -> None:
        self.setupUi(self)

    def toggle(self, turn_on: bool) -> None:
        """Convenience method to change state of the toggle once. Hides implementation details from the Controller."""
        self.themeToggle.setChecked(turn_on)

    # Connect callbacks of controller to emitted signals
    def connect_dark_mode(self, callback: Callable[[bool], None]) -> None:
        self._dark_mode_signal.connect(callback)

    def _send_dark_mode_signal(self, turn_on: bool) -> None:
        """Re-emit builtin signal to the controller"""
        self._dark_mode_signal.emit(turn_on)
