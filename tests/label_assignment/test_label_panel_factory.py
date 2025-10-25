"""
Test of the controller factory.
NOTE: Tests are simple, but there as a safety valve when refactoring the code
"""

from typing import cast
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication, QWidget

from app.label_assignment.label_panel_factory import (
    LabelPanelConfig,
    create_label_panel,
)
from app.main_app.component_controller_protocols import LabelPanelController


def test_resulting_controller_satisfies_protocol(qapp: QApplication) -> None:
    """
    Checks that the controller returned by the factory indeed
    satisfies the requirements for it to function in the MainController
    """
    controller = create_label_panel(None, LabelPanelConfig())
    assert isinstance(controller, LabelPanelController)


def test_resulting_controller_has_model_and_view_attrs(qapp: QApplication) -> None:
    """Checks the controller indeed has a Model and a View"""
    controller = create_label_panel(None, LabelPanelConfig())
    assert hasattr(controller, "model")
    assert hasattr(controller, "view")


def test_view_is_placed_in_desired_placeholder(qapp: QApplication) -> None:
    """simply check that the component's view has it's parent set correctly"""
    mock_placeholder = QWidget()
    controller = create_label_panel(mock_placeholder, LabelPanelConfig())
    assert cast(QWidget, controller.view).parent() == mock_placeholder


def test_initialization_logic(qapp: QApplication) -> None:
    """test the theme is applied when first building the app (in main.py, via the factory)"""
    with patch.object(
        "app.theme_manager.theme_controller.ThemeController", attribute="apply_theme"
    ) as mock_apply_theme:
        _ = create_label_panel(None)
        mock_apply_theme.assert_called_once()
