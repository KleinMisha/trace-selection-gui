"""
tests for the core keyboard_shortcuts module
"""

import sys
from unittest.mock import Mock

import pytest
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QApplication, QMenu, QMenuBar, QPushButton, QWidget
from pytestqt.qtbot import QtBot

from app.keyboard_shortcuts import assign_shortcut, clean_shortcut, is_valid


@pytest.fixture(scope="session", autouse=True)
def mock_application():
    """Ensure a QApplication exists for all Qt widget tests. Circumvents the 'fatal error' you otherwise get."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.mark.parametrize(
    "shortcut",
    [
        "Ctrl+S",  # common modifier + letter
        "Ctrl+Shift+Z",  # multiple modifiers
        "Alt+F4",  # modifier + function key
        "Ctrl++",  # special symbol key
        "Ctrl+Right",  # arrow key
        "Shift+1",  # modifier + number
        "Command+Q",  # Mac variant
        "Option+Cmd+C",  # combo with mac variant of the option key
    ],
)
def test_valid_shortcuts(shortcut: str) -> None:
    assert is_valid(shortcut)


@pytest.mark.parametrize(
    "shortcut",
    [
        "Ctrl+",  # trailing '+'
        "+S",  # leading '+'
        "Ctrl+Shift+",  # unfinished combo
        "",  # empty string
        "Banana+O",  # nonsense key
        "Cmd + Ctrl + C",  # duplicate keys (user thinks the Ctrl is not the same as the Cmd key on their Mac)
        "Ctrl+&",  # Explicitly entering the '&', which should be 'Shift + 7'
        "12",  # A number that requires multiple keys to press (valid version is '1+2')
        "Shift + X+Y",  # Multiple 'regular keys'. Only multiple modifiers are allowed, and one single regular key.
    ],
)
def test_invalid_shortcut(shortcut: str) -> None:
    """invalid entries"""
    assert not is_valid(shortcut)


@pytest.mark.parametrize(
    "shortcut, expected_key_combo",
    [
        ("Ctrl + S", "Ctrl+S"),  # remove spaces
        ("Control + Alt + 3", "Ctrl+Alt+3"),  # spelling it out
        ("Cmd+Shift+S", "Ctrl+Shift+S"),  # MacOS naming for the 'control key'
        ("Opt + Cmd + 3", "Alt+Ctrl+3"),  # MacOS naming for the 'alt key'
        ("Option+V", "Alt+V"),  # spelling it out
    ],
)
def test_cleaning_shortcut_strings(shortcut: str, expected_key_combo: str) -> None:
    """check this work independent of OS-specific naming of certain keys. uses some synonyms"""
    assert clean_shortcut(shortcut) == expected_key_combo


def test_assign_shortcut_to_button(qtbot: QtBot) -> None:
    """A button should have the shortcut assigned + have it's tooltip text adjusted"""

    window = QWidget()
    mock_button = QPushButton(window)
    mock_handler = Mock()
    mock_button.clicked.connect(mock_handler)
    shortcut = "Ctrl+D"
    desc = "mock"
    assign_shortcut(mock_button, shortcut=shortcut, description_prefix=desc)

    # use bot to send key combination signal
    qtbot.addWidget(window)
    with qtbot.wait_exposed(window):
        window.show()

    key_combo = QKeySequence(shortcut)
    primary_key = key_combo[0].key()
    mod_keys = key_combo[0].keyboardModifiers()
    qtbot.keyClick(window, primary_key, modifier=mod_keys)
    qtbot.wait(100)
    mock_handler.assert_called_once()
    # check tooltip text has been set
    assert mock_button.toolTip() != ""


def test_assign_shortcut_to_menu_action(qtbot: QtBot) -> None:
    """Menu items have enough space to display description in menu directly"""
    window = QWidget()
    menu_bar = QMenuBar(window)
    file_menu = QMenu("File", menu_bar)
    menu_bar.addMenu(file_menu)

    mock_action = QAction("Mock", window)
    file_menu.addAction(mock_action)

    qtbot.addWidget(window)
    with qtbot.wait_exposed(window):
        window.show()

    shortcut = "Ctrl+D"
    desc = "mock"
    assign_shortcut(mock_action, shortcut=shortcut, description_prefix=desc)

    mock_handler = Mock()
    mock_action.triggered.connect(mock_handler)

    # Simulate key press on the window
    key_combo = QKeySequence(shortcut)
    primary_key = key_combo[0].key()
    mod_keys = key_combo[0].keyboardModifiers()
    qtbot.keyClick(window, primary_key, modifier=mod_keys)

    mock_handler.assert_called_once()
