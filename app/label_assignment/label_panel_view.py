"""
View: user-facing logic. Can adjust display of the current label,
toggle on/off indicator showing if current label is included, listen to user's request to add/remove labels, etc.
"""

import re
from typing import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.keyboard_shortcuts import AcceptsShortCut
from app.label_assignment.label_assignment_view_ui import Ui_LabelAssignment
from app.label_assignment.label_panel_shortcut_items import (
    LabelPanelShortcutID as ShortcutID,
)
from app.state_variables import LightState
from app.theme_types import Color


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

        # store the colors to toggle the indicator light (allows responding to theme adjustments / configuration value changes)
        # NOTE: These defaults are purely here for testing the View by itself (now does not require a config to work)
        self._light_on_color: Color = "white"
        self._light_off_color: Color = "green"

    # UI-logic
    def build_ui(self) -> None:
        self.setupUi(self)

        # Design according to theme:
        self.assignButton.setProperty("role", "apply")
        self.unassignButton.setProperty("role", "undo")
        self.NextButton.setProperty("role", "neutral")
        self.previousButton.setProperty("role", "neutral")
        self.itemlistButton.setProperty("role", "neutral")

    def display_label(self, label: str) -> None:
        self.CurrentLabel.setText(label)

    def set_indicator_colors(self, color_on: Color, color_off: Color) -> None:
        """set the colors for the indicator when the light is turned on/off. Will be eventually called upon theme changes"""
        self._light_on_color = color_on
        self._light_off_color = color_off

    def toggle_indicator(self, state: LightState) -> None:
        """
        Adjust the part in the stylesheet that determines the background color of the label.
        NOTE: This 'light' is simply 'a text label without any text displayed'
        """

        if state == LightState.ON:
            color = self._light_on_color
        elif state == LightState.OFF:
            color = self._light_off_color

        # find the background-color option in the string and replace it with desired color
        current_styling = self.IndicatorAdded.styleSheet()
        background_color = "background-color\s*:\s*[^;]+;"
        new_styling = re.sub(
            pattern=background_color,
            repl=f"background-color: {color};",
            string=current_styling,
        )
        self.IndicatorAdded.setStyleSheet(new_styling)

    def get_shortcut_targets(self) -> dict[ShortcutID, AcceptsShortCut]:
        """Dictionary with all Qt Actions and Widgets to which a shortcut should get assigned."""
        return {
            ShortcutID.ASSIGN: self.assignButton,
            ShortcutID.UNASSIGN: self.unassignButton,
            ShortcutID.NEXT: self.NextButton,
            ShortcutID.PREVIOUS: self.previousButton,
        }

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
