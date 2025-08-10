"""
View: All the user-facing parts go here. View is responsible for displaying the list of items
"""

from typing import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from trace_selection.label_list_app.label_list_app_layout import Ui_LabelListWidget


class PyQtView(QWidget, Ui_LabelListWidget):
    """All PyQt specific aspects"""

    # PyQt's way of pub/sub messages from your view to the controller and back. Built-in system to connect emitted signal to a function (below)
    add_label_signal = pyqtSignal(str)
    remove_label_signal = pyqtSignal(str)

    def __init__(self, title: str | None = None) -> None:
        super().__init__()
        self._title = title
        self.build_ui()

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

    def connect_add_item(self, callback: Callable[[str], None]) -> None:
        """Connect the emitted signal  from this View to the be inserted as input for the function of the controller"""
        self.add_label_signal.connect(callback)

    def connect_remove_item(self, callback: Callable[[str], None]) -> None:
        """Connect the controller's function to the button or whatever input component"""
        self.remove_label_signal.connect(callback)

    def _send_add_signal(self) -> None:
        user_entry = self.input_label.text()
        self.add_label_signal.emit(user_entry)
        self.input_label.clear()

    def _send_remove_signal(self) -> None:
        user_selection = self.list_box.currentItem()
        if user_selection:
            self.remove_label_signal.emit(user_selection.text())
