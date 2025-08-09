"""
View: All the user-facing parts go here. View is responsible for displaying the list of items
"""

from typing import Callable

from label_list_app_layout import Ui_LabelListWidget
from PyQt6.QtWidgets import QWidget


class PyQtView(QWidget, Ui_LabelListWidget):
    """All PyQt specific aspects"""

    def __init__(self, title: str | None = None) -> None:
        super().__init__()
        self._title = title
        self.build_ui()

        # These will be set by controller
        self._add_handler = None
        self._remove_handler = None
        self.add_button.clicked.connect(self._send_add_signal)
        self.remove_button.clicked.connect(self._send_remove_signal)

    def build_ui(self) -> None:
        """Build the UI from the compiled `.ui` file (converted into Python file.)"""
        # Have the title configurable when instantiating the View to be able to re-use it for both trace labels and section labels
        self.setWindowTitle(self._title)
        self.setupUi(self)

    def display_list(self, labels: list[str]) -> None:
        """Updates the displayed list of items"""
        self.list_box.clear()
        self.list_box.addItems(labels)

    def on_add_label(self, handler: Callable[[str], None]) -> None:
        """Connect the controller's function to the button or whatever input component"""
        self._add_handler = handler

    def on_remove_label(self, handler: Callable[[str], None]) -> None:
        """Connect the controller's function to the button or whatever input component"""
        self._remove_handler = handler

    def _send_add_signal(self) -> None:
        if self._add_handler:
            user_entry = self.input_label.text()
            self._add_handler(user_entry)
            self.input_label.clear()

    def _send_remove_signal(self) -> None:
        if self._remove_handler:
            user_selection = self.list_box.currentItem()
            if user_selection:
                self._remove_handler(user_selection.text())
