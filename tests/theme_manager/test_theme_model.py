"""
Test that the Model correctly implements styling logic
"""

import tempfile
from pathlib import Path
from typing import cast
from unittest.mock import Mock, mock_open, patch

import pytest

from app.theme_manager.theme_model import Theme, ThemeModel


@pytest.fixture
def stylesheet() -> str:
    """A mock QSS file with the placeholders using the '$<KEY>' syntax"""
    return "QWidget {color: $primary, background: $secondary}"


@pytest.mark.parametrize("theme", [theme for theme in Theme])
def test_loading_palette(theme: Theme, stylesheet: str) -> None:
    """Check that the path used to load the palette contains the chosen theme"""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".qss") as temp_qss:
        temp_qss.write(stylesheet)
        temp_qss.flush()

        mock_file_opener = mock_open(read_data=stylesheet)
        with (
            patch("builtins.open", new=mock_file_opener),
            patch("json.load", return_value="{background: mock}"),
        ):
            model = ThemeModel(
                current_theme=theme, stylesheet_template=Path(temp_qss.name)
            )
            model.load_palette()

            file_path_opened = cast(Path, cast(Mock, mock_file_opener).call_args[0][0])
            assert f"{theme.value}" in file_path_opened.name
            assert file_path_opened.suffix == ".json"

            # check the palette is loaded correctly
            assert model.color_palette == "{background: mock}"


def test_constructing_stylesheet(stylesheet: str) -> None:
    """Check the template is correctly replaced by the actual values"""

    mock_palette = {"primary": "#FFFFFF", "secondary": "#000000"}
    expected_stylesheet = "QWidget {color: #FFFFFF, background: #000000}"
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".qss") as temp_qss:
        temp_qss.write(stylesheet)
        temp_qss.flush()
        model = ThemeModel(
            current_theme=Theme.LIGHT,
            stylesheet_template=Path(temp_qss.name),
            color_palette=mock_palette,
        )
        stylesheet = model.construct_stylesheet()
        assert stylesheet == expected_stylesheet
