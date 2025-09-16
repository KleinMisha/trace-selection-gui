"""
Controller: Listens to the View and handles communicating back to the Model and View. Communicates to the MainController and listens to the MainController.
"""

from typing import Callable, Protocol

from PyQt6.QtCore import QObject, pyqtSignal

from app.section_label_assignment.light_state import LightState
from app.section_label_assignment.sections_panel_model import Section


class Model(Protocol):
    """Abstraction of Model prescribing the parts the Controller needs/depends on existing"""

    @property
    def sections(self) -> list[Section]: ...
    @property
    def current_label(self) -> str: ...

    @property
    def current_section(self) -> Section: ...

    @property
    def current_is_assigned(self) -> bool: ...

    @property
    def available_labels(self) -> list[str]: ...

    def create_new_section(self) -> None: ...
    def remove_last_section(self) -> None: ...
    def set_start_section(self, value: int) -> None: ...
    def set_end_section(self, value: int) -> None: ...
    def reset_sections(
        self, section_labels: dict[tuple[int, int], list[str]]
    ) -> None: ...
    def assign_current_label(self) -> None: ...
    def unassign_current_label(self) -> None: ...
    def move_to_next_label(self) -> None: ...
    def move_to_previous_label(self) -> None: ...
    def move_to_next_section(self) -> None: ...
    def move_to_previous_section(self) -> None: ...
    def update_available_labels(self, updated_list: list[str]) -> None: ...
    def sections_to_dictionary(self) -> dict[tuple[int, int], list[str]]: ...
    def determine_section_boundaries(self) -> list[int]: ...


class View(Protocol):
    """Abstraction of View prescribing the parts the Controller needs/depends on existing"""

    def display_label(self, label: str) -> None: ...
    def toggle_indicator(self, state: LightState) -> None: ...
    def display_section_start(self, frame: int) -> None: ...
    def display_section_end(self, frame: int) -> None: ...

    def connect_assign_label(self, callback: Callable[[], None]) -> None: ...
    def connect_unassign_label(self, callback: Callable[[], None]) -> None: ...
    def connect_next_label(self, callback: Callable[[], None]) -> None: ...
    def connect_prev_label(self, callback: Callable[[], None]) -> None: ...
    def connect_next_section(self, callback: Callable[[], None]) -> None: ...
    def connect_prev_section(self, callback: Callable[[], None]) -> None: ...
    def connect_open_item_list(self, callback: Callable[[], None]) -> None: ...


class SectionsPanelController(QObject):
    _open_item_list_signal = pyqtSignal()

    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view

        # connect callbacks :: Listening to the View's signals
        self.view.connect_assign_label(self.handle_assign_label)
        self.view.connect_unassign_label(self.handle_unassign_label)
        self.view.connect_next_label(self.handle_move_to_next_label)
        self.view.connect_prev_label(self.handle_move_to_prev_label)
        self.view.connect_next_section(self.handle_move_to_next_section)
        self.view.connect_prev_section(self.handle_move_to_prev_section)
        self.view.connect_open_item_list(self.handle_open_item_list)

    def handle_assign_label(self) -> None:
        """Triggered when `add` button is clicked"""
        self.model.assign_current_label()
        self.view.toggle_indicator(LightState.ON)

    def handle_unassign_label(self) -> None:
        """Triggered when `remove` button is clicked"""
        self.model.unassign_current_label()
        self.view.toggle_indicator(LightState.OFF)

    def handle_move_to_next_label(self) -> None:
        """Triggered when `next label` button is clicked"""
        self.model.move_to_next_label()
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def handle_move_to_prev_label(self) -> None:
        """Triggered when `previous label` button is clicked"""
        self.model.move_to_previous_label()
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def handle_move_to_next_section(self) -> None:
        """Triggered when `next section` button is clicked"""
        self.model.move_to_next_section()

        if self.model.current_section.start_frame is not None:
            self.view.display_section_start(self.model.current_section.start_frame)

        if self.model.current_section.end_frame is not None:
            self.view.display_section_end(self.model.current_section.end_frame)

        self.view.toggle_indicator(self._determine_light_state())

    def handle_move_to_prev_section(self) -> None:
        """Triggered when `previous section` button is clicked"""
        self.model.move_to_previous_section()

        if self.model.current_section.start_frame is not None:
            self.view.display_section_start(self.model.current_section.start_frame)

        if self.model.current_section.end_frame is not None:
            self.view.display_section_end(self.model.current_section.end_frame)

        self.view.toggle_indicator(self._determine_light_state())

    def handle_open_item_list(self) -> None:
        """ "Informs the MainController the button has been pressed"""
        self._send_open_item_list_signal()

    # API for the MainController:
    def reset_for_new_trace(
        self, sections_new_trace: dict[tuple[int, int], list[str]]
    ) -> None:
        """Will be triggered from MainController: Reset the model's assigned labels when you change focus to a new trace"""
        self.model.reset_sections(sections_new_trace)

        if self.model.current_section.start_frame is not None:
            self.view.display_section_start(self.model.current_section.start_frame)

        if self.model.current_section.end_frame is not None:
            self.view.display_section_end(self.model.current_section.end_frame)

        self.view.toggle_indicator(self._determine_light_state())

    def update_available_labels(self, updated_list: list[str]) -> None:
        """Will be triggered from MainController: Adjust the set of available labels after using the ItemList window."""
        self.model.update_available_labels(updated_list)
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def set_start_section(self, value: int) -> None:
        self.model.set_start_section(value)
        self.view.display_section_start(value)

    def set_end_section(self, value: int) -> None:
        self.model.set_end_section(value)
        self.view.display_section_end(value)

    def get_section_labels(self) -> dict[tuple[int, int], list[str]]:
        """Such that the MainController can access this method on the component Model"""
        return self.model.sections_to_dictionary()

    def get_section_boundaries(self) -> list[int]:
        """Such that the MainController can access this method on the component Model"""
        return self.model.determine_section_boundaries()

    def get_available_labels(self) -> list[str]:
        return self.model.available_labels

    def connect_open_item_list(self, callback: Callable[[], None]) -> None:
        self._open_item_list_signal.connect(callback)

    # Used internally:
    def _send_open_item_list_signal(self) -> None:
        """Passes on the signal to the MainController"""
        self._open_item_list_signal.emit()

    def _determine_light_state(self) -> LightState:
        if self.model.current_is_assigned:
            return LightState.ON

        return LightState.OFF
