"""
Test that the controller correctly handles incoming signals from a mock View, and updates a mock Model accordingly.

NOTE: Currently, these tests are quite trivial for the simple widget. Doing this as a stepping stone for the full app / to learn how this would be done for more complex situations
"""

from typing import cast
from unittest.mock import Mock

from app.item_list.item_list_controller import ItemListController, Model, View


def test_handle_add_item() -> None:
    """The View detects the add button has been clicked! Does the controller correctly update the Model and the View?"""
    view = cast(View, Mock(spec=View))
    model = cast(Model, Mock(spec=Model))
    cast(Mock, model.get_items).return_value = ["good"]

    controller = ItemListController(model, view)

    controller.handle_add_label("good")
    cast(Mock, model.add_item).assert_called_once_with("good")
    cast(Mock, view.display_list).assert_called_with(["good"])


def test_handle_remove_item() -> None:
    """The View detects the remove button has been clicked! Does the controller correctly update the Model and the View?"""
    view = cast(View, Mock(spec=View))
    model = cast(Model, Mock(spec=Model))
    cast(Mock, model.get_items).return_value = []

    controller = ItemListController(model, view)

    controller.handle_remove_label("bad")
    cast(Mock, model.remove_item).assert_called_once_with("bad")
    cast(Mock, view.display_list).assert_called_with([])


def test_handle_chain_of_operations() -> None:
    """add two labels, remove the second, then replace it with a third label"""
    view = cast(View, Mock(spec=View))
    model = cast(Model, Mock(spec=Model))
    cast(Mock, model.get_items).return_value = ["1", "2", "3"]

    controller = ItemListController(model, view)

    controller.handle_add_label("1")
    controller.handle_add_label("2")
    controller.handle_remove_label("2")
    controller.handle_add_label("3")
    cast(Mock, view.display_list).assert_called_with(["1", "2", "3"])


def test_closing_window_event() -> None:
    """Test that the correct data gets emitted as a signal"""
    received_signals = []

    def mock_handler(items: list[str]):
        received_signals.append(items)

    view = cast(View, Mock(spec=View))
    model = cast(Model, Mock(spec=Model))
    cast(Mock, model.get_items).return_value = ["mock", "mocky", "mockerony-and-cheese"]

    controller = ItemListController(model, view)
    controller.connect_window_closed_signal(mock_handler)
    controller._send_window_closed_signal()
    assert received_signals[0] == ["mock", "mocky", "mockerony-and-cheese"]
