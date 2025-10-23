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
from PyQt6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from app.main_app.main_view import EventSeverity, LightState, MainView
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

    color_on = view._unsaved_changes_on_color
    color_off = view._unsaved_changes_off_color
    pattern_to_find = rf"background-color\s*: ({color_on}|{color_off});"
    match = re.search(pattern_to_find, new_styling)
    assert match is not None
    assert match.group(1) == color_on


def test_indicator_untracked_changes_off() -> None:
    """check the output stylesheet's content"""
    view = MainView()

    view.toggle_indicator_saved_changes(LightState.OFF)
    new_styling = view.UnsavedChangesIndicator.styleSheet()

    color_on = view._unsaved_changes_on_color
    color_off = view._unsaved_changes_off_color
    pattern_to_find = rf"background-color\s*: ({color_on}|{color_off});"
    match = re.search(pattern_to_find, new_styling)
    assert match is not None
    assert match.group(1) == color_off


@pytest.mark.parametrize(
    "message_box, message, title, expected_method",
    [
        (EventSeverity.INFO, "Info", "Note", "information"),
        (EventSeverity.WARNING, "Warning", "Warning", "warning"),
        (EventSeverity.ERROR, "Error", "Error", "critical"),
    ],
)
def test_opening_the_correct_message_box(
    message_box: EventSeverity,
    message: str,
    title: str,
    expected_method: str,
) -> None:
    """Use unittest.mock.patch to mock the correct method depending on the input"""
    view = MainView()

    with patch.object(target=ViewMessageBox, attribute=expected_method) as mock_msg_box:
        view.open_message_box(message_box, message)
        mock_msg_box.assert_called_once_with(view, title, message)


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


def test_display_trace_id_call_does_not_emit_a_signal() -> None:
    """
    Ensure that programmatically updating the trace ID in the view
    does not emit the 'jump_to_trace' signal.

    This prevents the controller from treating programmatic updates
    as user-initiated actions and avoids unintended updates on the new trace.
    """
    mock_handler = Mock()
    view = MainView()
    view.connect_jump_to_trace(mock_handler)
    view.display_trace_id("mock")
    mock_handler.assert_not_called()
