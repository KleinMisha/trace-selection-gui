"""
Protocols for the Controllers of individual components that define everything needed for the MainController to control them.


NOTE: Here you define stripped-down versions of the controllers with only those methods strictly needed for the MainController.
"""

from typing import Callable, Iterable, Protocol, runtime_checkable


class Trace(Protocol):
    """
    ? Unsure if this belongs in here. Should only be part of the data Model, but it does feel as the simplest way of implementing the 'reset' on the plot.
    """

    t: Iterable[float]
    z: Iterable[float]
    labels: list[str]
    sections: dict[tuple[int, int], list[str]]


@runtime_checkable
class ItemListController(Protocol):
    def connect_window_closed_signal(
        self, callback: Callable[[list[str]], None]
    ) -> None: ...


@runtime_checkable
class InteractivePlotController(Protocol):
    """#TODO: When you change focus to a new trace, need a way of triggering plotting a new Trace"""

    def connect_line_added_to_plot(self, callback: Callable[[float], None]) -> None: ...
    def connect_line_removed_from_plot(self, callback: Callable[[], None]) -> None: ...
    def reset_for_new_trace(self, trace: Trace) -> None: ...


@runtime_checkable
class LabelPanelController(Protocol):
    def reset_for_new_trace(self, labels_new_trace: list[str]) -> None:
        """Reset the model's assigned labels when you change focus to a new trace"""

    def update_available_labels(self, updated_list: list[str]) -> None:
        """Adjust the set of available labels after using the ItemList window."""


@runtime_checkable
class SectionsPanelController(Protocol):
    def reset_for_new_trace(
        self, sections_new_trace: dict[tuple[int, int], list[str]]
    ) -> None:
        """Reset the model's assigned labels when you change focus to a new trace"""

    def update_available_labels(self, updated_list: list[str]) -> None:
        """Will be triggered from MainController: Adjust the set of available labels after using the ItemList window."""
