"""
Controller handles receiving/sending messages from the View.
Makes the Model update the actual data
Tells the View to update what is displayed.
"""

from typing import Callable, Protocol


class View(Protocol):
    """The View listens to user input. The View sends signals to the Controller, and can receive the following commands from the Controller"""

    def display_list(self, labels: list[str]) -> None:
        """Updates the displayed list of items"""

    def connect_add_item(self, callback: Callable[[str], None]) -> None:
        """Connect emitted signal from the View's ._emit_add_item() method to the controller-side function that now actually updates things"""

    def connect_remove_item(self, callback: Callable[[str], None]) -> None:
        """Connect emitted signal from the View's ._emit_remove_item() method to the controller-side function that now actually updates things"""


class Model(Protocol):
    """The Model stores the actual data, and can perform actual operations on them. The Controller can instruct the model to perform these operations."""

    def add_item(self, name: str) -> None: ...
    def remove_item(self, name: str) -> None: ...
    def get_items(self) -> list[str]: ...


class ItemListController:
    """
    The controller handles signals received from the View and implements all the GUI logic.
    The Controller actually processes the incoming signal into an action performed on the model and then tells the view to see this change affect it on screen.
    """

    def __init__(self, model: Model, view: View) -> None:
        # dependency injection:
        self.model = model
        self.view = view

        # set up connections:
        self.view.connect_add_item(self.handle_add_label)
        self.view.connect_remove_item(self.handle_remove_label)

        # initialize the view:
        self.update_view()

    def handle_add_label(self, name: str) -> None:
        """
        Handles the signal "add item <name>" . When the view emits this signal, this method will tell the model to update, and then the view to refresh
        """
        self.model.add_item(name)
        self.update_view()

    def handle_remove_label(self, name: str) -> None:
        """
        Handles the signal "remove item <name>" . When the view emits this signal, this method will tell the model to update, and then the view to refresh
        """
        self.model.remove_item(name)
        self.update_view()

    def update_view(self) -> None:
        current_labels = self.model.get_items()
        self.view.display_list(current_labels)
