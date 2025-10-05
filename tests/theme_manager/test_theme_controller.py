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

    with patch.object(controller, attribute="_apply_theme") as mock_apply:
        controller.handle_dark_mode_toggle(use_dark_mode)
        expected_theme = Theme.DARK if use_dark_mode else Theme.LIGHT
        expected_filename = f"{expected_theme.value}.qss"
        assert controller.model.current_theme == expected_theme
        assert isinstance(controller.model.stylesheet_file, Path)
        assert controller.model.stylesheet_file.name == expected_filename
        mock_apply.assert_called_once()


def test_applying_qss_stylesheet() -> None:
    """Test that when an app is running, the style sheet is read from the qss file"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    controller = ThemeController(model, view)
    mock_app = cast(QApplication, Mock(spec=QApplication))

    expected_contents = "QWidget {background: green;}"
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".qss") as temp_qss:
        temp_qss.write(expected_contents)
        temp_qss.flush()
        model.stylesheet_file = Path(temp_qss.name)

        with patch("PyQt6.QtWidgets.QApplication.instance", return_value=mock_app):
            controller._apply_theme()
            cast(Mock, mock_app.setStyleSheet).assert_called_once_with(
                expected_contents
            )


def test_do_not_apply_theme_without_running_app() -> None:
    """Guard clause: do not apply a theme when there is no active QApplication"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    controller = ThemeController(model, view)
    mock_app = cast(QApplication, Mock())

    with patch("PyQt6.QtWidgets.QApplication.instance", return_value=mock_app):
        controller.model.stylesheet_file = Path("")
        controller._apply_theme()
        cast(Mock, mock_app.setStyleSheet).assert_not_called()
