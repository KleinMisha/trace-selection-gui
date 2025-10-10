"""
Test of the controller factory.
NOTE: Tests are simple, but there as a safety valve when refactoring the code
"""

from typing import cast

from PyQt6.QtWidgets import QApplication, QWidget

from app.label_assignment.label_panel_factory import create_label_panel
from app.main_app.component_controller_protocols import LabelPanelController


def test_resulting_controller_satisfies_protocol(qapp: QApplication) -> None:
    """
    Checks that the controller returned by the factory indeed
    satisfies the requirements for it to function in the MainController
    """
    controller = create_label_panel(None)
    assert isinstance(controller, LabelPanelController)


def test_resulting_controller_has_model_and_view_attrs(qapp: QApplication) -> None:
    """Checks the controller indeed has a Model and a View"""
    controller = create_label_panel(None)
    assert hasattr(controller, "model")
    assert hasattr(controller, "view")


def test_view_is_placed_in_desired_placeholder(qapp: QApplication) -> None:
    """simply check that the component's view has it's parent set correctly"""
    mock_placeholder = QWidget()
    controller = create_label_panel(mock_placeholder)
    assert cast(QWidget, controller.view).parent() == mock_placeholder
