"""
Test that the controller correctly handles incoming signals from a mock View, updates a mock Model accordingly, and optionally emits the correct signals (will be send to the main controller later).
"""

import tempfile
from pathlib import Path
from typing import cast
from unittest.mock import Mock, patch

import pytest
from PyQt6.QtWidgets import QApplication

from app.theme_manager.theme_controller import Model, Theme, ThemeController, View


@pytest.mark.parametrize("use_dark_mode", [True, False])
def test_toggle_dark_mode(use_dark_mode: bool) -> None:
    """check logic after user changed to dark/light mode"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    controller = ThemeController(model, view)

    with patch.object(controller, attribute="apply_theme") as mock_apply:
        controller.handle_dark_mode_toggle(use_dark_mode)
        expected_theme = Theme.DARK if use_dark_mode else Theme.LIGHT
        assert controller.model.current_theme == expected_theme
        mock_apply.assert_called_once()


def test_applying_qss_stylesheet() -> None:
    """Test that when an app is running, the style sheet is read from the qss file"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    controller = ThemeController(model, view)
    mock_app = cast(QApplication, Mock(spec=QApplication))

    # a mock qss: contents is irrelevant.
    template = "QWidget {mock: mock;}"
    mock_stylesheet = "QWidget {mock: black;}"
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".qss") as temp_qss:
        temp_qss.write(template)
        temp_qss.flush()
        model.stylesheet_template = Path(temp_qss.name)

        with (
            patch("PyQt6.QtWidgets.QApplication.instance", return_value=mock_app),
            patch.object(
                controller.model,
                attribute="construct_stylesheet",
                return_value=mock_stylesheet,
            ) as mock_stylesheet_builder,
        ):
            controller.apply_theme()
            mock_stylesheet_builder.assert_called_once()
            cast(Mock, mock_app.setStyleSheet).assert_called_once_with(mock_stylesheet)


def test_do_not_apply_theme_without_running_app() -> None:
    """Guard clause: do not apply a theme when there is no active QApplication"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    controller = ThemeController(model, view)
    mock_app = cast(QApplication, Mock())

    with patch("PyQt6.QtWidgets.QApplication.instance", return_value=mock_app):
        controller.model.stylesheet_template = Path("")
        controller.apply_theme()
        cast(Mock, mock_app.setStyleSheet).assert_not_called()
