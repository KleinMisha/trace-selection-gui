"""
View: user-facing logic. Can adjust display of the current label,
toggle on/off indicator showing if current label is included, listen to user's request to add/remove labels, etc.
"""

import re
from typing import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.label_assignment.label_assignment_view_ui import Ui_LabelAssignment
from app.label_assignment.light_state import LightState

# TODO: Move into configuration file!!
COLOR_OFF = "white"
COLOR_ON = "green"


class LabelPanelView(QWidget, Ui_LabelAssignment):
    _assign_label_signal = pyqtSignal()
    _unassign_label_signal = pyqtSignal()
    _next_label_signal = pyqtSignal()
    _prev_label_signal = pyqtSignal()
    _open_item_list_signal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.build_ui()

        # connect listening to user input:
        self.assignButton.clicked.connect(self._send_assign_label_signal)
        self.unassignButton.clicked.connect(self._send_unassign_label_signal)
        self.NextButton.clicked.connect(self._send_next_label_signal)
        self.previousButton.clicked.connect(self._send_prev_label_signal)
        self.itemlistButton.clicked.connect(self._send_open_item_list_signal)

    # UI-logic
    def build_ui(self) -> None:
        self.setupUi(self)

    def display_label(self, label: str) -> None:
        self.CurrentLabel.setText(label)

    def toggle_indicator(self, state: LightState) -> None:
        """
        Adjust the part in the stylesheet that determines the background color of the label.
        NOTE: This 'light' is simply 'a text label without any text displayed'
        """
        if state == LightState.ON:
            color = COLOR_ON
        elif state == LightState.OFF:
            color = COLOR_OFF

        # find the background-color option in the string and replace it with desired color
        current_styling = self.IndicatorAdded.styleSheet()
        background_color = "background-color\s*:\s*[^;]+;"
        new_styling = re.sub(
            pattern=background_color,
            repl=f"background-color: {color};",
            string=current_styling,
        )
        self.IndicatorAdded.setStyleSheet(new_styling)

    # Connect callbacks of controller to emitted signals
    def connect_assign_label(self, callback: Callable[[], None]) -> None:
        self._assign_label_signal.connect(callback)

    def connect_unassign_label(self, callback: Callable[[], None]) -> None:
        self._unassign_label_signal.connect(callback)

    def connect_next_label(self, callback: Callable[[], None]) -> None:
        self._next_label_signal.connect(callback)

    def connect_prev_label(self, callback: Callable[[], None]) -> None:
        self._prev_label_signal.connect(callback)

    def connect_open_item_list(self, callback: Callable[[], None]) -> None:
        """Connect a callback from the controller that will simply 're-emit'/pass on the signal to the MainController"""
        self._open_item_list_signal.connect(callback)

    # emit signals when triggered by user's input
    def _send_assign_label_signal(self) -> None:
        """when the 'add' button is pressed"""
        self._assign_label_signal.emit()

    def _send_unassign_label_signal(self) -> None:
        """when the 'remove' button is pressed"""
        self._unassign_label_signal.emit()

    def _send_next_label_signal(self) -> None:
        """When the 'next' button is pressed"""
        self._next_label_signal.emit()

    def _send_prev_label_signal(self) -> None:
        """When the 'previous' button is pressed"""
        self._prev_label_signal.emit()

    def _send_open_item_list_signal(self) -> None:
        """When the 'manage labels' button is pressed"""
        self._open_item_list_signal.emit()
