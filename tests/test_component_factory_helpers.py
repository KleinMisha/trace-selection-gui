"""
unit tests for the component_factory_helpers.py

most are very basic. Still serve as a little guard clause against unintended malfunction if the code gets refactored.
"""

import sys
from typing import cast

import pytest
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication, QLayoutItem, QVBoxLayout, QWidget

from app.component_factory_helpers import (
    _force_component_layout,
    fill_component_to_placeholder,
)


@pytest.fixture(scope="session", autouse=True)
def mock_application():
    """Ensure a QApplication exists for all Qt widget tests. Circumvents the 'fatal error' you otherwise get."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.mark.parametrize("force", [True, False])
def test_component_is_placed_within_placeholder(force: bool) -> None:
    """Check that the placeholder contains the component"""

    # mock the component and placeholders
    component = QWidget()
    placeholder = QWidget()

    fill_component_to_placeholder(component, placeholder, force_layout=force)
    assert component in placeholder.children()


@pytest.mark.parametrize("force", [True, False])
def test_component_fills_placeholder(force: bool) -> None:
    """Check the component now has the size of the placeholder"""
    component = QWidget()
    placeholder = QWidget()
    fill_component_to_placeholder(component, placeholder, force_layout=force)
    assert component.size() == placeholder.size()


def test_placeholder_styling_is_removed() -> None:
    """Any background/styling added to placeholders where there just for visual que, these should be gone after placing the actual component in it"""
    component = QWidget()
    placeholder = QWidget()
    fill_component_to_placeholder(component, placeholder)
    assert placeholder.styleSheet() == ""


def test_forced_layout() -> None:
    """Checks this does not remove any children widgets / and actually adds a top level layout to the component"""
    component = QWidget()
    child_widget_1 = QWidget(parent=component)
    child_widget_2 = QWidget(parent=component)
    # A non-widget child (anything that is a QObject, the superclass is a valid child of component)
    non_widget_child = QObject(parent=component)
    _force_component_layout(component)
    assert all(
        [
            child in component.children()
            for child in [child_widget_1, child_widget_2, non_widget_child]
        ]
    )

    assert isinstance(component.layout(), QVBoxLayout)
    layout = cast(QVBoxLayout, component.layout())
    available_widgets = [
        cast(QLayoutItem, layout.itemAt(idx)).widget() for idx in range(layout.count())
    ]
    assert [child in available_widgets for child in [child_widget_1, child_widget_2]]
