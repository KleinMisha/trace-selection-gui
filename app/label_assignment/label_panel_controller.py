"""
Controller: Handle communication with its own View and Model as well as with the MainController
"""

from typing import Any, Callable, Protocol

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.keyboard_shortcuts import AcceptsShortCut, assign_shortcut
from app.label_assignment.label_panel_config import LabelPanelConfig
from app.label_assignment.label_panel_shortcut_items import (
    LabelPanelShortcutID as ShortcutID,
)
from app.state_variables import LightState
from app.theme_types import Color


class Model(Protocol):
    """Abstraction of Model that makes the Controller independent of specific implementation thereof"""

    @property
    def assigned_labels(self) -> list[str]: ...

    @property
    def available_labels(self) -> list[str]: ...

    @property
    def current_label(self) -> str: ...

    @property
    def current_is_assigned(self) -> bool: ...

    @property
    def has_labels(self) -> bool: ...

    def assign_current_label(self) -> None: ...
    def unassign_current_label(self) -> None: ...
    def move_to_next(self) -> None: ...
    def move_to_previous(self) -> None: ...
    def reset_assigned_labels(self, labels_new_trace: list[str]) -> None: ...
    def update_available_labels(self, updated_list: list[str]) -> None: ...


class View(Protocol):
    """Abstraction of View that makes the Controller independent of the specific implementation thereof"""

    def display_label(self, label: str) -> None: ...
    def toggle_indicator(self, state: LightState) -> None: ...
    def connect_assign_label(self, callback: Callable[[], None]) -> None: ...
    def connect_unassign_label(self, callback: Callable[[], None]) -> None: ...
    def connect_next_label(self, callback: Callable[[], None]) -> None: ...
    def connect_prev_label(self, callback: Callable[[], None]) -> None: ...
    def connect_open_item_list(self, callback: Callable[[], None]) -> None: ...
    def set_indicator_colors(self, color_on: Color, color_off: Color) -> None: ...
    def get_shortcut_targets(self) -> dict[ShortcutID, AcceptsShortCut]: ...


class LabelPanelController(QObject):
    _open_item_list_signal = pyqtSignal()

    def __init__(self, model: Model, view: View, config: LabelPanelConfig) -> None:
        super().__init__()
        self.model = model
        self.view = view
        self.config = config

        # apply initial settings:
        self.apply_config()

        # connect callbacks : Listening to the View's signals
        self.view.connect_assign_label(self.handle_assign_label)
        self.view.connect_unassign_label(self.handle_unassign_label)
        self.view.connect_next_label(self.handle_move_to_next)
        self.view.connect_prev_label(self.handle_move_to_previous)
        self.view.connect_open_item_list(self.handle_open_item_list)

    def handle_assign_label(self) -> None:
        """Triggered when 'add' button is clicked"""
        if not self.model.has_labels:
            # break out of this function when there are no labels at the start
            return

        self.model.assign_current_label()
        self.view.toggle_indicator(LightState.ON)

    def handle_unassign_label(self) -> None:
        """Triggered when 'remove' button is clicked"""
        if not self.model.has_labels:
            # break out of this function when there are no labels at the start
            return
        self.model.unassign_current_label()
        self.view.toggle_indicator(LightState.OFF)

    def handle_move_to_next(self) -> None:
        """Triggered when 'next' button is clicked"""
        if not self.model.has_labels:
            # break out of this function when there are no labels at the start
            return
        self.model.move_to_next()
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def handle_move_to_previous(self) -> None:
        """Triggered when 'previous' button is clicked"""
        if not self.model.has_labels:
            # break out of this function when there are no labels at the start
            return
        self.model.move_to_previous()
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def handle_open_item_list(self) -> None:
        """ "Informs the MainController the button has been pressed"""
        self._send_open_item_list_signal()

    # API for the MainController:
    def apply_config(self) -> None:
        """apply settings to model and view"""

        # set colors for light indicator:
        self.view.set_indicator_colors(
            color_on=self.config.color_indicator_on,
            color_off=self.config.color_indicator_off,
        )

        # setup shortcuts
        shortcuts = self.config.get_shortcuts()
        shortcut_targets = self.view.get_shortcut_targets()
        for key in ShortcutID:
            assign_shortcut(shortcut_targets[key], shortcuts[key])

    def reset_for_new_trace(self, labels_new_trace: list[str]) -> None:
        """Will be triggered from MainController: Reset the model's assigned labels when you change focus to a new trace"""
        self.model.reset_assigned_labels(labels_new_trace)
        self.view.toggle_indicator(self._determine_light_state())

    def update_available_labels(self, updated_list: list[str]) -> None:
        """Will be triggered from MainController: Adjust the set of available labels after using the ItemList window."""
        if not self.model.has_labels:
            return

        self.model.update_available_labels(updated_list)
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def get_assigned_labels(self) -> list[str]:
        return self.model.assigned_labels

    def get_available_labels(self) -> list[str]:
        return self.model.available_labels

    def connect_open_item_list(self, callback: Callable[[], None]) -> None:
        self._open_item_list_signal.connect(callback)

    def update_config(self, new_config_values: dict[str, Any]) -> None:
        """Change configuration/settings using the provided dictionary of values the user wants to alter."""
        for key, value in new_config_values.items():
            setattr(self.config, key, value)

    # Used internally:
    def _send_open_item_list_signal(self) -> None:
        """Passes on the signal to the MainController"""
        self._open_item_list_signal.emit()

    def _determine_light_state(self) -> LightState:
        if self.model.has_labels and self.model.current_is_assigned:
            return LightState.ON

        return LightState.OFF
