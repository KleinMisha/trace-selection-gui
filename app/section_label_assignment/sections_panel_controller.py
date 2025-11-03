"""
Controller: Listens to the View and handles communicating back to the Model and View. Communicates to the MainController and listens to the MainController.
"""

from typing import Any, Callable, Optional, Protocol

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.keyboard_shortcuts import AcceptsShortCut, assign_shortcut
from app.core.state_variables import LightState
from app.section_label_assignment.sections_panel_config import SectionsPanelConfig
from app.section_label_assignment.sections_panel_model import Section
from app.section_label_assignment.sections_panel_shortcut_items import (
    SectionsPanelShortcutID as ShortcutID,
)
from app.theme_types import Color


class Model(Protocol):
    """Abstraction of Model prescribing the parts the Controller needs/depends on existing"""

    @property
    def sections(self) -> list[Section]: ...

    @property
    def current_section_index(self) -> int: ...

    @property
    def current_label(self) -> str: ...

    @property
    def current_section(self) -> Section: ...

    @property
    def current_is_assigned(self) -> bool: ...

    @property
    def available_labels(self) -> list[str]: ...

    @property
    def has_labels(self) -> bool: ...

    @property
    def has_sections(self) -> bool: ...

    @property
    def current_section_has_start(self) -> bool: ...

    @property
    def current_section_has_end(self) -> bool: ...

    @property
    def current_section_start_frame(self) -> int | None: ...

    @property
    def current_section_end_frame(self) -> int | None: ...

    def create_new_section(self) -> None: ...
    def remove_last_section(self) -> None: ...
    def set_start_section(self, value: Optional[int]) -> None: ...
    def set_end_section(self, value: Optional[int]) -> None: ...
    def reset_sections(
        self, section_labels: dict[tuple[int, int], list[str]]
    ) -> None: ...
    def assign_current_label(self) -> None: ...
    def unassign_current_label(self) -> None: ...
    def move_to_next_label(self) -> None: ...
    def move_to_previous_label(self) -> None: ...
    def move_to_next_section(self) -> None: ...
    def move_to_previous_section(self) -> None: ...
    def jump_to_section(self, target: int) -> None: ...
    def update_available_labels(self, updated_list: list[str]) -> None: ...
    def sections_to_dictionary(self) -> dict[tuple[int, int], list[str]]: ...


class View(Protocol):
    """Abstraction of View prescribing the parts the Controller needs/depends on existing"""

    def display_label(self, label: str) -> None: ...
    def toggle_indicator(self, state: LightState) -> None: ...
    def display_section_start(self, frame: Optional[int]) -> None: ...
    def display_section_end(self, frame: Optional[int]) -> None: ...

    def connect_assign_label(self, callback: Callable[[], None]) -> None: ...
    def connect_unassign_label(self, callback: Callable[[], None]) -> None: ...
    def connect_next_label(self, callback: Callable[[], None]) -> None: ...
    def connect_prev_label(self, callback: Callable[[], None]) -> None: ...
    def connect_next_section(self, callback: Callable[[], None]) -> None: ...
    def connect_prev_section(self, callback: Callable[[], None]) -> None: ...
    def connect_open_item_list(self, callback: Callable[[], None]) -> None: ...
    def set_indicator_colors(self, color_on: Color, color_off: Color) -> None: ...
    def get_shortcut_targets(self) -> dict[ShortcutID, AcceptsShortCut]: ...


class SectionsPanelController(QObject):
    _open_item_list_signal = pyqtSignal()

    def __init__(self, model: Model, view: View, config: SectionsPanelConfig) -> None:
        super().__init__()
        self.model = model
        self.view = view
        self.config = config

        # apply initial settings:
        self.apply_config()

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
        if not self.model.has_labels or not self.model.has_sections:
            # break out of this function when there are no labels at the start
            return
        self.model.assign_current_label()
        self.view.toggle_indicator(LightState.ON)

    def handle_unassign_label(self) -> None:
        """Triggered when `remove` button is clicked"""
        if not self.model.has_labels or not self.model.has_sections:
            # break out of this function when there are no labels at the start
            return
        self.model.unassign_current_label()
        self.view.toggle_indicator(LightState.OFF)

    def handle_move_to_next_label(self) -> None:
        """Triggered when `next label` button is clicked"""

        if not self.model.has_labels:
            # break out of this function when there are no labels at the start
            return

        self.model.move_to_next_label()
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def handle_move_to_prev_label(self) -> None:
        """Triggered when `previous label` button is clicked"""

        if not self.model.has_labels:
            # break out of this function when there are no labels at the start
            return

        self.model.move_to_previous_label()
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def handle_move_to_next_section(self) -> None:
        """Triggered when `next section` button is clicked"""

        if not self.model.has_sections:
            # break out of this function when there are no sections at the start
            return

        self.model.move_to_next_section()
        self.view.display_section_start(self.model.current_section_start_frame)
        self.view.display_section_end(self.model.current_section_end_frame)
        self.view.toggle_indicator(self._determine_light_state())

    def handle_move_to_prev_section(self) -> None:
        """Triggered when `previous section` button is clicked"""

        if not self.model.has_sections:
            # break out of this function when there are no sections at the start
            return

        self.model.move_to_previous_section()
        self.view.display_section_start(self.model.current_section_start_frame)
        self.view.display_section_end(self.model.current_section_end_frame)
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

    def reset_for_new_trace(
        self, sections_new_trace: dict[tuple[int, int], list[str]]
    ) -> None:
        """Will be triggered from MainController: Reset the model's assigned labels when you change focus to a new trace"""
        self.model.reset_sections(sections_new_trace)
        number_available_sections = len(sections_new_trace.keys())
        self.model.jump_to_section(number_available_sections)
        self.view.display_section_start(self.model.current_section_start_frame)
        self.view.display_section_end(self.model.current_section_end_frame)
        self.view.toggle_indicator(self._determine_light_state())

    def update_available_labels(self, updated_list: list[str]) -> None:
        """Will be triggered from MainController: Adjust the set of available labels after using the ItemList window."""
        if not self.model.has_labels:
            return

        self.model.update_available_labels(updated_list)
        self.view.display_label(self.model.current_label)
        self.view.toggle_indicator(self._determine_light_state())

    def set_start_section(self, value: Optional[int] = None) -> None:
        self.model.set_start_section(value)
        self.view.display_section_start(value)

    def set_end_section(self, value: Optional[int] = None) -> None:
        self.model.set_end_section(value)
        self.view.display_section_end(value)

    def get_available_labels(self) -> list[str]:
        """Such that the MainController can access this method on the component Model"""
        return self.model.available_labels

    def current_section_has_start_frame(self) -> bool:
        """Such that the MainController can access this method on the component Model"""
        return self.model.current_section_has_start

    def current_section_has_end_frame(self) -> bool:
        """Such that the MainController can access this method on the component Model"""
        return self.model.current_section_has_end

    def create_new_section_current_trace(self) -> None:
        """Such that the MainController can access this method on the component Model"""
        return self.model.create_new_section()

    def remove_last_section_from_current_trace(self) -> None:
        """Such that the MainController can access this method on the component Model"""
        return self.model.remove_last_section()

    def jump_to_section_by_index(self, target: int) -> None:
        """Such that the MainController can access this method on the component Model"""
        return self.model.jump_to_section(target)

    def get_number_of_sections_current_trace(self) -> int:
        """Needed when the MainController wants to shift focus to the final section (the newly created one) of the current trace"""
        return len(self.model.sections)

    def get_current_section_index(self) -> int:
        """Such that the MainController can access this method on the component Model"""
        return self.model.current_section_index

    def connect_open_item_list(self, callback: Callable[[], None]) -> None:
        self._open_item_list_signal.connect(callback)

    def get_section_labels(self) -> dict[tuple[int, int], list[str]]:
        """Such that the MainController can access this method on the component Model"""
        return self.model.sections_to_dictionary()

    def update_config(self, new_config_values: dict[str, Any]) -> None:
        """Change configuration/settings using the provided dictionary of values the user wants to alter."""
        for key, value in new_config_values.items():
            setattr(self.config, key, value)

    # Used internally:
    def _send_open_item_list_signal(self) -> None:
        """Passes on the signal to the MainController"""
        self._open_item_list_signal.emit()

    def _determine_light_state(self) -> LightState:
        if self.model.has_sections and self.model.current_is_assigned:
            return LightState.ON

        return LightState.OFF
