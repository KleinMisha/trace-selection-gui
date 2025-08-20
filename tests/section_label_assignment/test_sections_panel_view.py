"""
Test
- listening to user input --> emit signal accordingly
- correct display update logic
NOTE: Simulates user clicks with pyQt specific functionalities. So that part is not framework agnostic.
"""

import re

from PyQt6.QtCore import Qt
from pytestqt.qtbot import QtBot

from app.section_label_assignment.sections_panel_view import (
    COLOR_OFF,
    COLOR_ON,
    LightState,
    SectionsPanelView,
)


def test_assign_label_button(qtbot: QtBot) -> None:
    """press / click the button and check signal is emitted."""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("add this label")

    view = SectionsPanelView()
    view.connect_assign_label(mock_handler)
    qtbot.add_widget(view)
    qtbot.mouseClick(view.assignButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["add this label"]


def test_unassign_label_button(qtbot: QtBot) -> None:
    """press / click the button and check signal is emitted."""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("remove this label")

    view = SectionsPanelView()
    view.connect_unassign_label(mock_handler)
    qtbot.add_widget(view)
    qtbot.mouseClick(view.unassignButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["remove this label"]


def test_next_label_button(qtbot: QtBot) -> None:
    """press / click the button and check signal is emitted."""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("move to next")

    view = SectionsPanelView()
    view.connect_next_label(mock_handler)
    qtbot.add_widget(view)
    qtbot.mouseClick(view.NextLabelButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["move to next"]


def test_prev_label_button(qtbot: QtBot) -> None:
    """press / click the button and check signal is emitted."""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("move to previous")

    view = SectionsPanelView()
    view.connect_prev_label(mock_handler)
    qtbot.add_widget(view)
    qtbot.mouseClick(view.previousLabelButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["move to previous"]


def test_click_open_item_list_button(qtbot: QtBot) -> None:
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("open item list window")

    view = SectionsPanelView()
    view.connect_open_item_list(mock_handler)
    qtbot.add_widget(view)
    qtbot.mouseClick(view.itemlistButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["open item list window"]


def test_switching_indicator_on() -> None:
    """check the output stylesheet's content"""
    view = SectionsPanelView()
    view.toggle_indicator(LightState.ON)
    new_styling = view.IndicatorAdded.styleSheet()

    # TODO: use the configuration file ?
    # ? Check what is best-practice when doing this, as we actually do not care about the precise color, just that it sets it accordingly
    pattern_to_find = rf"background-color\s*: ({COLOR_ON}|{COLOR_OFF});"
    match = re.search(pattern_to_find, new_styling)
    assert match is not None
    assert match.group(1) == COLOR_ON


def test_switching_indicator_off() -> None:
    """check the output stylesheet's content"""
    view = SectionsPanelView()
    view.toggle_indicator(LightState.OFF)
    new_styling = view.IndicatorAdded.styleSheet()

    # TODO: use the configuration file ?
    # ? Check what is best-practice when doing this, as we actually do not care about the precise color, just that it sets it accordingly
    pattern_to_find = rf"background-color\s*: ({COLOR_ON}|{COLOR_OFF});"
    match = re.search(pattern_to_find, new_styling)
    assert match is not None
    assert match.group(1) == COLOR_OFF


def test_next_section_button(qtbot: QtBot) -> None:
    """press / click the button and check signal is emitted."""

    received_signals = []

    def mock_handler() -> None:
        received_signals.append("next section")

    view = SectionsPanelView()
    view.connect_next_section(mock_handler)
    qtbot.add_widget(view)
    qtbot.mouseClick(view.NextSectionButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["next section"]


def test_prev_section_button(qtbot: QtBot) -> None:
    """press / click the button and check signal is emitted."""

    received_signals = []

    def mock_handler() -> None:
        received_signals.append("previous section")

    view = SectionsPanelView()
    view.connect_prev_section(mock_handler)
    qtbot.add_widget(view)
    qtbot.mouseClick(view.previousSectionButton, Qt.MouseButton.LeftButton)
    assert received_signals == ["previous section"]


def test_clicking_a_series_of_buttons(qtbot: QtBot) -> None:
    """double-check signal do not mix when pressing different buttons in the UI"""
    received_signals = []

    def mock_add_handler() -> None:
        received_signals.append("add label")

    def mock_remove_handler() -> None:
        received_signals.append("remove label")

    def mock_next_label_handler() -> None:
        received_signals.append("move to next label")

    def mock_previous_label_handler() -> None:
        received_signals.append("move to previous label")

    def mock_next_section_handler() -> None:
        received_signals.append("move to next section")

    def mock_previous_section_handler() -> None:
        received_signals.append("move to previous section")

    view = SectionsPanelView()
    view.connect_assign_label(mock_add_handler)
    view.connect_unassign_label(mock_remove_handler)
    view.connect_next_label(mock_next_label_handler)
    view.connect_prev_label(mock_previous_label_handler)
    view.connect_next_section(mock_next_section_handler)
    view.connect_prev_section(mock_previous_section_handler)

    # Add --> next label--> next label--> add --> prev label--> remove --> next section --> next label --> add --> previous section --> remove
    qtbot.add_widget(view)
    qtbot.mouseClick(view.assignButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.NextLabelButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.NextLabelButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.assignButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.previousLabelButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.unassignButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.NextSectionButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.NextLabelButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.assignButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.previousSectionButton, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(view.unassignButton, Qt.MouseButton.LeftButton)

    assert received_signals == [
        "add label",
        "move to next label",
        "move to next label",
        "add label",
        "move to previous label",
        "remove label",
        "move to next section",
        "move to next label",
        "add label",
        "move to previous section",
        "remove label",
    ]
