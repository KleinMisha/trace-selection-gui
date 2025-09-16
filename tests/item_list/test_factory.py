"""
Test of the controller factory.
NOTE: Tests are simple, but there as a safety valve when refactoring the code
"""

from PyQt6.QtWidgets import QApplication

from app.item_list.item_list_factory import create_item_list
from app.main_app.component_controller_protocols import ItemListController


def test_resulting_controller_satisfies_protocol(qapp: QApplication) -> None:
    """
    Checks that the controller returned by the factory indeed
    satisfies the requirements for it to function in the MainController
    """

    controller = create_item_list([])
    assert isinstance(controller, ItemListController)


def test_resulting_controller_has_model_and_view_attrs(qapp: QApplication) -> None:
    """Checks the controller indeed has a Model and a View"""
    controller = create_item_list([])
    assert hasattr(controller, "model")
    assert hasattr(controller, "view")


def test_model_has_the_desired_items(qapp: QApplication) -> None:
    """Checks that the model created is indeed as intended. Should be trivial"""
    mock_items = ["mock", "mocker", "most mockest"]
    controller = create_item_list(mock_items)
    assert controller.model.get_items() == mock_items
