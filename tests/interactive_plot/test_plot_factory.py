"""
Test of the controller factory.
NOTE: Tests are simple, but there as a safety valve when refactoring the code
"""

from typing import cast

from PyQt6.QtWidgets import QApplication, QWidget

from app.interactive_plot.plot_factory import create_plot_controller
from app.main_app.component_controller_protocols import InteractivePlotController


def test_resulting_controller_satisfies_protocol(qapp: QApplication) -> None:
    """
    Checks that the controller returned by the factory indeed
    satisfies the requirements for it to function in the MainController
    """
    controller = create_plot_controller(None)
    assert isinstance(controller, InteractivePlotController)


def test_resulting_controller_has_model_and_view_attrs(qapp: QApplication) -> None:
    """Checks the controller indeed has a Model and a View"""
    controller = create_plot_controller(None)
    assert hasattr(controller, "model")
    assert hasattr(controller, "view")


def test_view_is_placed_in_desired_placeholder(qapp: QApplication) -> None:
    """simply check that the component's view has it's parent set correctly"""
    mock_placeholder = QWidget()
    controller = create_plot_controller(mock_placeholder)
    assert cast(QWidget, controller.view).parent() == mock_placeholder
