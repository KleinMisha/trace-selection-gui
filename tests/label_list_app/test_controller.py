"""
Test that the controller correctly handles incoming signals from a mock View, and updates a mock Model accordingly.

NOTE: Currently, these tests are quite trivial for the simple widget. Doing this as a stepping stone for the full app / to learn how this would be done for more complex situations
"""

from typing import Callable

from trace_selection.label_list_app.label_list_controller import LabelListController


class MockView:
    """A Mock view that can just receive messages / instructions from the controller"""

    def __init__(self) -> None:
        self.received_signals = []
        self.connections = []

    def display_list(self, labels: list[str]) -> None:
        self.received_signals = []
        for label in labels:
            self.received_signals.append(label)

    def connect_add_item(self, callback: Callable[[str], None]) -> None:
        self.connections.append(f"Connect {callback.__name__} as 'add label' callback")

    def connect_remove_item(self, callback: Callable[[str], None]) -> None:
        self.connections.append(
            f"Connect {callback.__name__} as 'remove label' callback"
        )


class MockModel:
    """A Mock model that can just receive messages / instructions from the controller"""

    def __init__(self) -> None:
        self.received_signals = []

    def add_label(self, name: str) -> None:
        self.received_signals.append(f"Add '{name}' to list of labels")

    def remove_label(self, name: str) -> None:
        self.received_signals.append(f"Remove '{name}' from list of labels")

    def get_labels(self) -> list[str]:
        return self.received_signals


def test_handle_add_item() -> None:
    """The View detects the add button has been clicked! Does the controller correctly update the Model and the View?"""
    view = MockView()
    model = MockModel()
    controller = LabelListController(model, view)

    controller.handle_add_label("good")
    assert "Add 'good' to list of labels" in model.received_signals
    assert "Add 'good' to list of labels" in view.received_signals


def test_handle_remove_item() -> None:
    """The View detects the remove button has been clicked! Does the controller correctly update the Model and the View?"""
    view = MockView()
    model = MockModel()
    controller = LabelListController(model, view)

    controller.handle_remove_label("bad")
    assert "Remove 'bad' from list of labels" in model.received_signals
    assert "Remove 'bad' from list of labels" in view.received_signals


def test_handle_chain_of_operations() -> None:
    """add two labels, remove the second, then replace it with a third label"""
    view = MockView()
    model = MockModel()
    controller = LabelListController(model, view)

    controller.handle_add_label("1")
    controller.handle_add_label("2")
    controller.handle_remove_label("2")
    controller.handle_add_label("3")

    expected_commands = [
        "Add '1' to list of labels",
        "Add '2' to list of labels",
        "Remove '2' from list of labels",
        "Add '3' to list of labels",
    ]
    assert model.received_signals == expected_commands
    assert view.received_signals == expected_commands


def test_controller_sets_up_view_handlers():
    """Misha: To be honest, the AI suggested to add this unit test. If you ask me, if you pass the previous, you know the connections are established"""
    print(f"MockView connect_add_item: {MockView.connect_add_item}")
    view = MockView()
    print(f"view.connect_add_item: {view.connect_add_item}")
    model = MockModel()
    _ = LabelListController(model, view)

    expected_signals = [
        "Connect handle_add_label as 'add label' callback",
        "Connect handle_remove_label as 'remove label' callback",
    ]

    assert view.connections == expected_signals
