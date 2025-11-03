"""
View: All the user-facing parts go here. View is responsible for displaying the list of items
"""

from typing import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QWidget

from app.item_list.item_list_app_layout_ui import Ui_ItemListWidget


class PyQtView(QWidget, Ui_ItemListWidget):
    """All PyQt specific aspects"""

    # PyQt's way of pub/sub messages from your view to the controller and back. Built-in system to connect emitted signal to a function (below)
    _add_item_signal = pyqtSignal(str)
    _remove_item_signal = pyqtSignal(str)
    _close_window_signal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None, title: str | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self.build_ui()

        self.add_button.clicked.connect(self._send_add_signal)
        self.remove_button.clicked.connect(self._send_remove_signal)

        # enable using ENTER key to add a new label
        self.input_label.returnPressed.connect(self._send_add_signal)

    def build_ui(self) -> None:
        """Build the UI from the compiled `.ui` file (converted into Python file.)"""
        # Have the title configurable when instantiating the View to be able to re-use it for both trace labels and section labels
        self.setWindowTitle(self._title)
        self.setupUi(self)

        # button design according to theme:
        self.add_button.setProperty("role", "apply")
        self.remove_button.setProperty("role", "undo")

    def display_list(self, labels: list[str]) -> None:
        """Updates the displayed list of items"""
        self.list_box.clear()
        self.list_box.addItems(labels)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        """Overwrite the builtin method from PyQt that emits a signal whenever you close the window (by any of the methods)"""
        self._send_close_window_signal()
        super().closeEvent(a0)

    def connect_add_item(self, callback: Callable[[str], None]) -> None:
        """Connect the emitted signal  from this View to the be inserted as input for the function of the controller"""
        self._add_item_signal.connect(callback)

    def connect_remove_item(self, callback: Callable[[str], None]) -> None:
        """Connect the controller's function to the button or whatever input component"""
        self._remove_item_signal.connect(callback)

    def connect_close_window(self, callback: Callable[[], None]) -> None:
        self._close_window_signal.connect(callback)

    def _send_add_signal(self) -> None:
        user_entry = self.input_label.text()
        self._add_item_signal.emit(user_entry)
        self.input_label.clear()

    def _send_remove_signal(self) -> None:
        user_selection = self.list_box.currentItem()
        if user_selection:
            self._remove_item_signal.emit(user_selection.text())

    def _send_close_window_signal(self) -> None:
        self._close_window_signal.emit()
