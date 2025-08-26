"""
Controller: Handle communication with its own View and Model as well as with the MainController
"""

from typing import Callable, Protocol

from app.label_assignment.light_state import LightState


class Model(Protocol):
    """Abstraction of Model that makes the Controller independent of specific implementation thereof"""

    @property
    def current_label(self) -> str: ...

    @property
    def current_is_assigned(self) -> bool: ...

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


class LabelPanelController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view

        # connect callbacks :: Listening to the View's signals
        self.view.connect_assign_label(self.handle_assign_label)
        self.view.connect_unassign_label(self.handle_unassign_label)
        self.view.connect_next_label(self.handle_move_to_next)
        self.view.connect_prev_label(self.handle_move_to_previous)

    def handle_assign_label(self) -> None:
        """Triggered when 'add' button is clicked"""
        self.model.assign_current_label()
        self.view.toggle_indicator(LightState.ON)

    def handle_unassign_label(self) -> None:
        """Triggered when 'remove' button is clicked"""
        self.model.unassign_current_label()
        self.view.toggle_indicator(LightState.OFF)

    def handle_move_to_next(self) -> None:
        """Triggered when 'next' button is clicked"""
        self.model.move_to_next()
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def handle_move_to_previous(self) -> None:
        """Triggered when 'previous' button is clicked"""
        self.model.move_to_previous()
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    # API for the MainController:
    def reset_for_new_trace(self, labels_new_trace: list[str]) -> None:
        """Will be triggered from MainController: Reset the model's assigned labels when you change focus to a new trace"""
        self.model.reset_assigned_labels(labels_new_trace)
        self.view.toggle_indicator(self._determine_light_state())

    def update_available_labels(self, updated_list: list[str]) -> None:
        """Will be triggered from MainController: Adjust the set of available labels after using the ItemList window."""
        self.model.update_available_labels(updated_list)
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    # Used internally:
    def _determine_light_state(self) -> LightState:
        if self.model.current_is_assigned:
            return LightState.ON

        return LightState.OFF
