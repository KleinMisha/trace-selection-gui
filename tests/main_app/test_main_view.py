"""
Test
- listening to user input --> emit signal accordingly
- correct display update logic
NOTE: Simulates user clicks with pyQt specific functionalities. So that part is not framework agnostic.

NOTE: Because of the code encapsulating different responsibilities, there are actually not that many test of the main View needed.
"""

import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from app.main_app.main_view import (
    COLOR_OFF,
    COLOR_ON,
    KEYBOARD_SHORTCUTS,
    LightState,
    MainView,
    MessageBox,
)
from app.main_app.main_view import QFileDialog as ViewFileDialog
from app.main_app.main_view import QMessageBox as ViewMessageBox


def test_trigger_file_open_signal(qtbot: QtBot) -> None:
    """Simple check to ensure the View emits a signal when you trigger a menu bar item"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("Open...")

    # Ensure a QApplication exists
    _ = QApplication.instance() or QApplication([])

    # Create and register the view
    view = MainView()
    qtbot.addWidget(view)
    with qtbot.wait_exposed(view):
        view.show()

    view.connect_menu_file_open(mock_handler)
    view.actionOpen.trigger()
    assert received_signals == ["Open..."]


def test_trigger_file_save_signal(qtbot: QtBot) -> None:
    """Simple check to ensure the View emits a signal when you trigger a menu bar item"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("Save...")

    # Ensure a QApplication exists
    _ = QApplication.instance() or QApplication([])

    # Create and register the view
    view = MainView()
    qtbot.addWidget(view)
    with qtbot.wait_exposed(view):
        view.show()

    view.connect_menu_file_save(mock_handler)
    view.actionSave.trigger()
    assert received_signals == ["Save..."]


def test_trigger_file_save_as_signal(qtbot: QtBot) -> None:
    """Simple check to ensure the View emits a signal when you trigger a menu bar item"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("Save as...")

    # Ensure a QApplication exists
    _ = QApplication.instance() or QApplication([])

    # Create and register the view
    view = MainView()
    qtbot.addWidget(view)
    with qtbot.wait_exposed(view):
        view.show()
    view.connect_menu_file_save_as(mock_handler)
    view.actionSaveAs.trigger()
    assert received_signals == ["Save as..."]


def test_trigger_file_import_labels_signal(qtbot: QtBot) -> None:
    """Simple check to ensure the View emits a signal when you trigger a menu bar item"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("Import labels...")

    # Ensure a QApplication exists
    _ = QApplication.instance() or QApplication([])

    # Create and register the view
    view = MainView()
    qtbot.addWidget(view)
    with qtbot.wait_exposed(view):
        view.show()
    view.connect_menu_file_import_labels(mock_handler)
    view.actionImportLabels.trigger()
    assert received_signals == ["Import labels..."]


def test_trigger_file_import_sections_signal(qtbot: QtBot) -> None:
    """Simple check to ensure the View emits a signal when you trigger a menu bar item"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("Import sections...")

    # Ensure a QApplication exists
    _ = QApplication.instance() or QApplication([])

    # Create and register the view
    view = MainView()
    qtbot.addWidget(view)
    with qtbot.wait_exposed(view):
        view.show()
    view.connect_menu_file_import_sections(mock_handler)
    view.actionImportSectionLabels.trigger()
    assert received_signals == ["Import sections..."]


def test_keyboard_shortcuts(qtbot: QtBot) -> None:
    """Simulate using keyboard shortcuts"""
    # Ensure a QApplication exists
    _ = QApplication.instance() or QApplication([])

    view = MainView()
    qtbot.addWidget(view)
    with qtbot.wait_exposed(view):
        view.show()

    for action_name, (action_in_words, expected_shortcut) in KEYBOARD_SHORTCUTS.items():
        # get the correct QAction
        action: QAction = getattr(view, action_name)

        # Simple tests: Check that the display text and shortcuts are assigned as intended
        key_sequence = QKeySequence(expected_shortcut)
        key_icons = key_sequence.toString(QKeySequence.SequenceFormat.NativeText)
        expected_display_text = f"{action_in_words}\t{key_icons}"
        assert action.shortcut().toString() == expected_shortcut
        assert action.text() == expected_display_text

        # Now connect a mock signal handler to the action and simulate sending the shortcut user input
        primary_key = key_sequence[0].key()
        mod_keys = key_sequence[0].keyboardModifiers()
        mock_handler = Mock()
        action.triggered.connect(mock_handler)
        qtbot.keyClick(view.window(), primary_key, modifier=mod_keys)
        mock_handler.assert_called_once()


def test_next_trace_button(qtbot: QtBot) -> None:
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("next trace")

    view = MainView()
    view.connect_next_trace(mock_handler)
    qtbot.add_widget(view)
    qtbot.mouseClick(view.NextTraceButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["next trace"]


def test_prev_trace_button(qtbot: QtBot) -> None:
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("previous trace")

    view = MainView()
    view.connect_prev_trace(mock_handler)
    qtbot.mouseClick(view.previousTraceButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["previous trace"]


def test_indicator_untracked_changes_on() -> None:
    """check the output stylesheet's content"""
    view = MainView()
    view.toggle_indicator_saved_changes(LightState.ON)
    new_styling = view.UnsavedChangesIndicator.styleSheet()

    # TODO: use the configuration file ?
    # ? Check what is best-practice when doing this, as we actually do not care about the precise color, just that it sets it accordingly
    pattern_to_find = rf"background-color\s*: ({COLOR_ON}|{COLOR_OFF});"
    match = re.search(pattern_to_find, new_styling)
    assert match is not None
    assert match.group(1) == COLOR_ON


def test_indicator_untracked_changes_off() -> None:
    """check the output stylesheet's content"""
    view = MainView()
    view.toggle_indicator_saved_changes(LightState.OFF)
    new_styling = view.UnsavedChangesIndicator.styleSheet()

    # TODO: use the configuration file ?
    # ? Check what is best-practice when doing this, as we actually do not care about the precise color, just that it sets it accordingly
    pattern_to_find = rf"background-color\s*: ({COLOR_ON}|{COLOR_OFF});"
    match = re.search(pattern_to_find, new_styling)
    assert match is not None
    assert match.group(1) == COLOR_OFF


@pytest.mark.parametrize(
    "message_box, message, title, expected_method",
    [
        (MessageBox.INFO, "Info", "Note", "information"),
        (MessageBox.WARNING, "Warning", "Warning", "warning"),
        (MessageBox.ERROR, "Error", "Error", "critical"),
    ],
)
def test_opening_the_correct_message_box(
    message_box: MessageBox, message: str, title: str, expected_method: str
) -> None:
    """Use unittest.mock.patch to mock the correct method depending on the input"""
    view = MainView()
    with patch.object(target=ViewMessageBox, attribute=expected_method) as mock_msg_box:
        view.open_message_box(message_box, message)
        mock_msg_box.assert_called_once_with(view, title=title, text=message)


def test_opening_the_correct_file() -> None:
    view = MainView()
    with (
        patch.object(
            target=ViewFileDialog,
            attribute="getOpenFileName",
            return_value=("/mock/mocker/mockeronyNcheese/most_mockest.txt", ""),
        ),
        patch.object(
            target=view, attribute="_send_file_path_selected_signal"
        ) as mock_signal_caller,
    ):
        view.ask_open_file("")
        mock_signal_caller.assert_called_once_with(
            Path("/mock/mocker/mockeronyNcheese/most_mockest.txt")
        )


def test_saving_to_the_correct_file() -> None:
    view = MainView()
    with (
        patch.object(
            target=ViewFileDialog,
            attribute="getSaveFileName",
            return_value=("/mock/mocker/mockeronyNcheese/most_mockest.txt", ""),
        ),
        patch.object(
            target=view, attribute="_send_file_path_selected_signal"
        ) as mock_signal_caller,
    ):
        view.ask_save_file("")
        mock_signal_caller.assert_called_once_with(
            Path("/mock/mocker/mockeronyNcheese/most_mockest.txt")
        )
