"""
Test that the controller correctly handles incoming signals from a mock View, updates a mock Model accordingly, and optionally emits the correct signals (will be send to the main controller later).



! Using the unittest.mock.Mock to essentially create models and views adhering to their protocols without caring about actual implementation.
! This requires a bit of "a dance of types" as the type hints within the unittest library itself are not correct. Hence,
! PyLance will never be able to understand your mock has the methods of the protocol as well as those of a Mock.
! Hence the moving back-and-forth with casting things.
? Is there a way to do this simpler? Technically, I could skip this, but then autocompletion is not available (because PyLance does not understand what instance methods it should have)
"""

from typing import Any, cast
from unittest.mock import Mock, PropertyMock, create_autospec

import pytest

from app.label_assignment.label_panel_controller import (
    LabelPanelConfig,
    LabelPanelController,
    LightState,
)
from app.label_assignment.label_panel_model import LabelPanelModel as Model
from app.label_assignment.label_panel_view import LabelPanelView as View


@pytest.fixture
def model() -> Model:
    """Mock the Model: type-hinting it here as Model, so that PyLance understands it has all the attributes and methods a View should have"""
    return create_autospec(Model, instance=True)


@pytest.fixture
def view() -> View:
    """Mock the View: type-hinting it here as View, so that PyLance understands it has all the attributes and methods a View should have"""
    return create_autospec(View, instance=True)


@pytest.fixture
def controller(model: Model, view: View) -> LabelPanelController:
    """Moved the creation of the controller into this fixture to avoid passing an entire grocery list of arguments into all the test functions"""
    return LabelPanelController(model, view, config=LabelPanelConfig())


def test_assign_label(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """adding a label"""

    cast(Any, type(model)).current_label = PropertyMock(return_value="mock")
    cast(Any, type(model)).has_labels = PropertyMock(return_value=True)
    controller.handle_assign_label()
    cast(Mock, model.assign_current_label).assert_called_once()
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_assign_non_existing_label(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """Calling the add label before there is any label available"""

    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)
    controller.handle_assign_label()
    cast(Mock, model.assign_current_label).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_unassign_label(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """removing a label. NOTE: Model and View already tested, so no need to worry about first assigning a label then removing it. Model already handles this case correctly"""

    cast(Any, type(model)).current_label = PropertyMock(return_value="mock")
    cast(Any, type(model)).has_labels = PropertyMock(return_value=True)
    controller.handle_unassign_label()
    cast(Mock, model.unassign_current_label).assert_called_once()
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.OFF)


def test_unassign_non_existing_label(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """Calling the remove label before there is any label available"""

    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)
    controller.handle_unassign_label()
    cast(Mock, model.unassign_current_label).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_move_to_next(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """
    test moving to next label
    NOTE: Because we are using a Mock of the Model. Unittest will by default evaluate "if model.current_is_assigned" to TRUE
    NOTE: Hence, the light will be toggled on.
    """

    cast(Any, type(model)).has_labels = PropertyMock(return_value=True)
    cast(Any, type(model)).current_label = PropertyMock(return_value="mock")
    controller.handle_move_to_next()
    cast(Mock, model.move_to_next).assert_called_once()
    cast(Mock, view.display_label).assert_called_once_with("mock")
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_move_to_next_no_available_labels(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """test moving before there is a label available"""

    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)
    controller.handle_move_to_next()
    cast(Mock, model.move_to_next).assert_not_called()
    cast(Mock, view.display_label).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_move_to_previous(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """
    test moving to previous label
    NOTE: Because we are using a Mock of the Model. Unittest will by default evaluate "if model.current_is_assigned" to TRUE
    NOTE: Hence, the light will be toggled on.
    """

    cast(Any, type(model)).current_label = PropertyMock(return_value="mock")
    controller.handle_move_to_previous()
    cast(Mock, model.move_to_previous).assert_called_once()
    cast(Mock, view.display_label).assert_called_once_with("mock")
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_move_to_previous_no_available_labels(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """test moving before there is a label available"""

    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)
    controller.handle_move_to_previous()
    cast(Mock, model.move_to_previous).assert_not_called()
    cast(Mock, view.display_label).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_change_assigned_labels(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """
    Mimic changing to a new trace that has a different set of labels assigned to it
    NOTE: As we are setting the assigned labels by hand, the light should be toggled on.
    """

    controller.reset_for_new_trace(labels_new_trace=["mock", "mocker", "most mockest"])
    cast(Mock, model.reset_assigned_labels).assert_called_once_with(
        ["mock", "mocker", "most mockest"]
    )
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_change_available_labels(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """
    Mimic having adjusted the set of available labels. Will actually be done via the ItemList window and input value will be passed from MainController
    NOTE: Because we are using a Mock of the Model. Unittest will by default evaluate "if model.current_is_assigned" to TRUE
    NOTE: Hence, the light will be toggled on.
    """

    cast(Any, type(model)).has_labels = PropertyMock(return_value=True)
    controller.update_available_labels(updated_list=["mock", "mocker", "most mockest"])
    cast(Mock, model.update_available_labels).assert_called_once_with(
        ["mock", "mocker", "most mockest"]
    )
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_change_without_available_labels(
    controller: LabelPanelController, model: Model, view: View
) -> None:
    """Mimic calling the update when there are no available labels"""

    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)
    controller.update_available_labels(updated_list=["mock", "mocker", "most mockest"])
    cast(Mock, model.update_available_labels).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


@pytest.mark.parametrize("is_assigned", [True, False])
def test_correct_light_state(
    controller: LabelPanelController, model: Model, view: View, is_assigned: bool
) -> None:
    """ "
    Simple check that the indicator behaves as expected. As for the above, the default behavior of unit test mocks are to
    evaluate to TRUE.

    mixing this with the above (by manually setting the state to OFF) felt unhandy as that would be mixing two different kinds of tests.
    """

    expected_state = LightState.ON
    if not is_assigned:
        expected_state = LightState.OFF

    cast(Any, type(model)).current_is_assigned = PropertyMock(return_value=is_assigned)
    assert controller._determine_light_state() == expected_state
