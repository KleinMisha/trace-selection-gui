"""
Controller handles receiving/sending messages from the View.
Makes the Model update the actual data
Tells the View to update what is displayed.
"""

from typing import Callable, Protocol


class View(Protocol):
    """'GUI package agnostic interface for the displayed UI"""

    def display_list(self, labels: list[str]) -> None:
        """Updates the displayed list of items"""

    def on_add_label(self, handler: Callable[[str], None]) -> None:
        """Connect the controller's function to the button or whatever input component"""

    def on_remove_label(self, handler: Callable[[str], None]) -> None:
        """Connect the controller's function to the button or whatever input component"""


class Model(Protocol):
    """TODO: Remove later. This part I do not think needs to be abstract at this level."""

    def add_label(self, name: str) -> None: ...
    def remove_label(self, name: str) -> None: ...
    def get_labels(self) -> list[str]: ...


class LabelListController:
    def __init__(self, model: Model, view: View) -> None:
        # dependency injection:
        self.model = model
        self.view = view

        # set up connections:
        self.view.on_add_label(self.handle_add_label)
        self.view.on_remove_label(self.handle_remove_label)

        # initialize the view:
        self.update_view()

    def handle_add_label(self, name: str) -> None:
        self.model.add_label(name)
        self.update_view()

    def handle_remove_label(self, name: str) -> None:
        self.model.remove_label(name)
        self.update_view()

    def update_view(self) -> None:
        current_labels = self.model.get_labels()
        self.view.display_list(current_labels)
