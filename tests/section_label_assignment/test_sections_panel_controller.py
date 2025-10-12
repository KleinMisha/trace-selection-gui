"""
Test that the controller correctly handles incoming signals from a mock View, updates a mock Model accordingly, and optionally emits the correct signals (will be send to the main controller later).



! Using the unittest.mock.Mock to essentially create models and views adhering to their protocols without caring about actual implementation.
! This requires a bit of "a dance of types" as the type hints within the unittest library itself are not correct. Hence,
! PyLance will never be able to understand your mock has the methods of the protocol as well as those of a Mock.
! Hence the moving back-and-forth with casting things.
? Is there a way to do this simpler? Technically, I could skip this, but then autocompletion is not available (because PyLance does not understand what instance methods it should have)
"""

from typing import Any, cast
from unittest.mock import Mock, PropertyMock

import pytest

from app.section_label_assignment.sections_panel_controller import (
    LightState,
    Model,
    SectionsPanelConfig,
    SectionsPanelController,
    View,
)
from app.section_label_assignment.sections_panel_model import Section


def test_assign_label() -> None:
    """adding a label"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    cast(Any, type(model)).current_label = PropertyMock(return_value="mock")
    cast(Any, type(model)).has_labels = PropertyMock(return_value=True)
    controller.handle_assign_label()
    cast(Mock, model.assign_current_label).assert_called_once()
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_assign_non_existing_label() -> None:
    """Calling the add label before there is any label available"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)
    cast(Any, type(model)).has_sections = PropertyMock(return_value=True)
    controller.handle_assign_label()
    cast(Mock, model.assign_current_label).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_assign_label_no_existing_section() -> None:
    """Attempt calling before there is a section available"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_labels = PropertyMock(return_value=True)
    cast(Any, type(model)).has_sections = PropertyMock(return_value=False)
    controller.handle_assign_label()
    cast(Mock, model.assign_current_label).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_unassign_label() -> None:
    """removing a label. NOTE: Model and View already tested, so no need to worry about first assigning a label then removing it. Model already handles this case correctly"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    cast(Any, type(model)).current_label = PropertyMock(return_value="mock")
    controller.handle_unassign_label()
    cast(Mock, model.unassign_current_label).assert_called_once()
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.OFF)


def test_unassign_non_existing_label() -> None:
    """Calling the remove label before there is any label available"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)
    cast(Any, type(model)).has_sections = PropertyMock(return_value=True)
    controller.handle_unassign_label()
    cast(Mock, model.unassign_current_label).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_unassign_label_no_existing_section() -> None:
    """Attempt calling before there is a section available"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_labels = PropertyMock(return_value=True)
    cast(Any, type(model)).has_sections = PropertyMock(return_value=False)
    controller.handle_unassign_label()
    cast(Mock, model.unassign_current_label).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_move_to_next_label() -> None:
    """
    test moving to next label
    NOTE: Because we are using a Mock of the Model. Unittest will by default evaluate "if model.current_is_assigned" to TRUE
    NOTE: Hence, the light will be toggled on.
    """
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    cast(Any, type(model)).current_label = PropertyMock(return_value="mock")
    controller.handle_move_to_next_label()
    cast(Mock, model.move_to_next_label).assert_called_once()
    cast(Mock, view.display_label).assert_called_once_with("mock")
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_move_to_previous_label() -> None:
    """
    test moving to previous label
    NOTE: Because we are using a Mock of the Model. Unittest will by default evaluate "if model.current_is_assigned" to TRUE
    NOTE: Hence, the light will be toggled on.
    """

    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    cast(Any, type(model)).current_label = PropertyMock(return_value="mock")
    controller.handle_move_to_prev_label()
    cast(Mock, model.move_to_previous_label).assert_called_once()
    cast(Mock, view.display_label).assert_called_once_with("mock")
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_do_not_move_labels_before_data_available() -> None:
    """If the model has no available labels, make sure to break out of the controller's handler function"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    # a model without available labels:
    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)

    # assert you never move forwards:
    controller.handle_move_to_next_label()
    cast(Mock, model.move_to_next_label).assert_not_called()

    # assert you never more backwards:
    controller.handle_move_to_prev_label()
    cast(Mock, model.move_to_previous_label).assert_not_called()


def test_change_assigned_labels() -> None:
    """
    Mimic changing to a new trace that has a different set of labels assigned to it
    NOTE: As we are setting the assigned labels by hand, the light should be toggled on.
    """
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    expected_section_labels = {(23, 45): ["mock", "mocker", "most mockest"]}
    controller.reset_for_new_trace(sections_new_trace=expected_section_labels)
    cast(Mock, model.reset_sections).assert_called_once_with(expected_section_labels)
    cast(Mock, model.jump_to_section).assert_called_once_with(
        len(expected_section_labels.keys())
    )
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_change_available_labels() -> None:
    """
    Mimic having adjusted the set of available labels. Will actually be done via the ItemList window and input value will be passed from MainController
    NOTE: Because we are using a Mock of the Model. Unittest will by default evaluate "if model.current_is_assigned" to TRUE
    NOTE: Hence, the light will be toggled on.
    """
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    controller.update_available_labels(updated_list=["mock", "mocker", "most mockest"])
    cast(Mock, model.update_available_labels).assert_called_once_with(
        ["mock", "mocker", "most mockest"]
    )
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_change_without_available_labels() -> None:
    """Mimic calling the update when there are no available labels"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_labels = PropertyMock(return_value=False)
    controller.update_available_labels(updated_list=["mock", "mocker", "most mockest"])
    cast(Mock, model.update_available_labels).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


@pytest.mark.parametrize("is_assigned", [True, False])
def test_correct_light_state(is_assigned: bool) -> None:
    """ "
    Simple check that the indicator behaves as expected. As for the above, the default behavior of unit test mocks are to
    evaluate to TRUE.

    mixing this with the above (by manually setting the state to OFF) felt unhandy as that would be mixing two different kinds of tests.
    """
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    expected_state = LightState.ON
    if not is_assigned:
        expected_state = LightState.OFF

    cast(Any, type(model)).current_is_assigned = PropertyMock(return_value=is_assigned)
    assert controller._determine_light_state() == expected_state


def test_move_to_next_section() -> None:
    """
    test moving to next label
    NOTE: Because we are using a Mock of the Model. Unittest will by default evaluate "if model.current_is_assigned" to TRUE
    NOTE: Hence, the light will be toggled on.
    """
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_sections = PropertyMock(return_value=True)
    cast(Any, type(model)).current_section_start_frame = PropertyMock(return_value=8)
    cast(Any, type(model)).current_section_end_frame = PropertyMock(return_value=24)
    controller.handle_move_to_next_section()
    cast(Mock, model.move_to_next_section).assert_called_once()
    cast(Mock, view.display_section_start).assert_called_once_with(8)
    cast(Mock, view.display_section_end).assert_called_once_with(24)
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_move_to_previous_section() -> None:
    """
    test moving to next label
    NOTE: Because we are using a Mock of the Model. Unittest will by default evaluate "if model.current_is_assigned" to TRUE
    NOTE: Hence, the light will be toggled on.
    """
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_sections = PropertyMock(return_value=True)
    cast(Any, type(model)).current_section_start_frame = PropertyMock(return_value=8)
    cast(Any, type(model)).current_section_end_frame = PropertyMock(return_value=24)
    controller.handle_move_to_prev_section()
    cast(Mock, model.move_to_previous_section).assert_called_once()
    cast(Mock, view.display_section_start).assert_called_once_with(8)
    cast(Mock, view.display_section_end).assert_called_once_with(24)
    cast(Mock, view.toggle_indicator).assert_called_once_with(LightState.ON)


def test_move_to_next_without_a_section() -> None:
    """if you press the button to move to the next section, while there is no section for the current trace, nothing should happen"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_sections = PropertyMock(return_value=False)
    controller.handle_move_to_next_section()
    cast(Mock, model.move_to_previous_section).assert_not_called()
    cast(Mock, view.display_section_start).assert_not_called()
    cast(Mock, view.display_section_end).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_move_to_previous_without_a_section() -> None:
    """if you press the button to move to the next section, while there is no section for the current trace, nothing should happen"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)
    cast(Any, type(model)).has_sections = PropertyMock(return_value=False)
    controller.handle_move_to_prev_section()
    cast(Mock, model.move_to_previous_section).assert_not_called()
    cast(Mock, view.display_section_start).assert_not_called()
    cast(Mock, view.display_section_end).assert_not_called()
    cast(Mock, view.toggle_indicator).assert_not_called()


def test_do_not_move_sections_before_data_available() -> None:
    """If the model has no available sections, make sure to break out of the controller's handler function"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    # a model without available sections:
    cast(Any, type(model)).has_sections = PropertyMock(return_value=False)

    # assert you never move forwards:
    controller.handle_move_to_next_section()
    cast(Mock, model.move_to_next_section).assert_not_called()

    # assert you never more backwards:
    controller.handle_move_to_prev_section()
    cast(Mock, model.move_to_previous_section).assert_not_called()


@pytest.mark.parametrize("frame", [23, 45, 34, 30, 8, 24])
def test_setting_start_of_current_section(frame: int) -> None:
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    cast(Any, type(model)).sections = PropertyMock(return_value=Section())
    controller.set_start_section(frame)
    cast(Mock, model.set_start_section).assert_called_once_with(frame)
    cast(Mock, view.display_section_start).assert_called_once_with(frame)


@pytest.mark.parametrize("frame", [23, 45, 34, 30, 8, 24])
def test_setting_end_of_current_section(frame: int) -> None:
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    controller.set_end_section(frame)
    cast(Mock, model.set_end_section).assert_called_once_with(frame)
    cast(Mock, view.display_section_end).assert_called_once_with(frame)


def test_getting_section_labels() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    controller.get_section_labels()
    cast(Mock, model.sections_to_dictionary).assert_called_once()


def test_getting_available_labels() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    expected_labels = ["Lebron", "Steph", "KD", "Magic", "Shai", "Shaq", "Giannis"]
    cast(Any, type(model)).available_labels = PropertyMock(return_value=expected_labels)
    assert controller.get_available_labels() == expected_labels


def test_checking_start_of_current_section() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    cast(Any, type(model)).current_section_has_start = PropertyMock(return_value=True)
    assert controller.current_section_has_start_frame()

    cast(Any, type(model)).current_section_has_start = PropertyMock(return_value=False)
    assert not controller.current_section_has_start_frame()


def test_checking_end_of_current_section() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    cast(Any, type(model)).current_section_has_end = PropertyMock(return_value=True)
    assert controller.current_section_has_end_frame()

    cast(Any, type(model)).current_section_has_end = PropertyMock(return_value=False)
    assert not controller.current_section_has_end_frame()


def test_creating_a_new_section() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    controller.create_new_section_current_trace()
    cast(Mock, model.create_new_section).assert_called_once()


def test_removing_last_section() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    controller.remove_last_section_from_current_trace()
    cast(Mock, model.remove_last_section).assert_called_once()


def test_jumping_to_section() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    expected_target = 23
    controller.jump_to_section_by_index(expected_target)
    cast(Mock, model.jump_to_section).assert_called_once_with(expected_target)


def test_getting_number_of_sections_current_trace() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    expected_number = 45
    cast(Any, type(model)).sections = PropertyMock(
        return_value=[Section()] * expected_number
    )
    assert controller.get_number_of_sections_current_trace() == expected_number


def test_getting_current_section_index() -> None:
    """test API for MainController"""
    model = cast(Model, Mock(spec=Model))
    view = cast(View, Mock(spec=View))
    config = SectionsPanelConfig()
    controller = SectionsPanelController(model, view, config)

    expected_value = 23
    cast(Any, type(model)).current_section_index = PropertyMock(
        return_value=expected_value
    )
    assert controller.get_current_section_index() == expected_value
