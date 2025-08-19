"""
Test that the controller correctly handles incoming signals from a mock View, updates a mock Model accordingly, and optionally emits the correct signals (will be send to the main controller later).



! Using the unittest.mock.Mock to essentially create models and views adhering to their protocols without caring about actual implementation.
! This requires a bit of "a dance of types" as the type hints within the unittest library itself are not correct. Hence,
! PyLance will never be able to understand your mock has the methods of the protocol as well as those of a Mock.
! Hence the moving back-and-forth with casting things.
? Is there a way to do this simpler? Technically, I could skip this, but then autocompletion is not available (because PyLance does not understand what instance methods it should have)
"""

from typing import cast
from unittest.mock import Mock

import pytest

from app.interactive_plot.plot_controller import InteractivePlotController, Model, View


@pytest.mark.parametrize("location", [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0])
def test_handle_left_mouse_click(location: float) -> None:
    """
    Trigger handler at Controller: Are signals received by Model and View ?
    """
    received_signals = []

    def mock_handler(value: float) -> None:
        received_signals.append(value)

    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    controller = InteractivePlotController(model, view)

    cast(Mock, model.find_nearest_data_point).return_value = (location, 23.0)
    controller.connect_line_added_to_plot(mock_handler)
    controller.handle_left_mouse_click(location, 42.0)

    cast(Mock, view.show_line_in_plot).assert_called_once_with(location)
    cast(Mock, view.update_figure).assert_called_once()

    assert received_signals[0] == location


def test_handle_right_mouse_click() -> None:
    """
    Trigger handler at Controller: Are signals received by Model and View ?
    """
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("right click")

    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    controller = InteractivePlotController(model, view)
    controller.connect_line_removed_from_plot(mock_handler)
    controller.handle_right_mouse_click()
    cast(Mock, view.clear_last_line_from_plot).assert_called_once()
    cast(Mock, view.update_figure).assert_called_once()
    assert received_signals == ["right click"]


@pytest.mark.parametrize(
    "entry", [str(value) for value in [8.0, 24.0, 23.0, 45.0, 23.6]]
)
def test_adjusting_zmin_valid_entry(entry: str) -> None:
    """Entering valid numbers"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.z_max = 23.0
    controller = InteractivePlotController(model, view)
    controller.handle_adjusted_z_min(entry)
    cast(Mock, view.adjust_z_range).assert_called_once_with(
        min_value=float(entry), max_value=23.0
    )
    cast(Mock, view.update_figure).assert_called_once()


@pytest.mark.parametrize(
    "entry", ["", " ", "1,2", "1.3,4", "1-2", "bla", "2.8.24", "__/ == !##$__"]
)
def test_adjusting_zmin_invalid_entry(entry: str) -> None:
    """Check that entering anything other than something that can be converted into a floating point number results in doing nothing"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.z_max = 23.0
    controller = InteractivePlotController(model, view)
    controller.handle_adjusted_z_min(entry)
    cast(Mock, view.adjust_z_range).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()


@pytest.mark.parametrize(
    "entry", [str(value) for value in [8.0, 24.0, 23.0, 45.0, 23.6]]
)
def test_adjusting_zmax_valid_entry(entry: str) -> None:
    """Entering valid numbers"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.z_min = 23.0
    controller = InteractivePlotController(model, view)
    controller.handle_adjusted_z_max(entry)
    cast(Mock, view.adjust_z_range).assert_called_once_with(
        min_value=23.0, max_value=float(entry)
    )
    cast(Mock, view.update_figure).assert_called_once()


@pytest.mark.parametrize(
    "entry", ["", " ", "1,2", "1.3,4", "1-2", "bla", "2.8.24", "__/ == !##$__"]
)
def test_adjusting_zmax_invalid_entry(entry: str) -> None:
    """Check that entering anything other than something that can be converted into a floating point number results in doing nothing"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.z_min = 23.0
    controller = InteractivePlotController(model, view)
    controller.handle_adjusted_z_max(entry)
    cast(Mock, view.adjust_z_range).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()


@pytest.mark.parametrize(
    "entry", [str(value) for value in [8.0, 24.0, 23.0, 45.0, 23.6]]
)
def test_adjusting_tmin_valid_entry(entry: str) -> None:
    """Entering valid numbers"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.t_max = 23.0
    controller = InteractivePlotController(model, view)
    controller.handle_adjusted_t_min(entry)
    cast(Mock, view.adjust_t_range).assert_called_once_with(
        min_value=float(entry), max_value=23.0
    )
    cast(Mock, view.update_figure).assert_called_once()


@pytest.mark.parametrize(
    "entry", ["", " ", "1,2", "1.3,4", "1-2", "bla", "2.8.24", "__/ == !##$__"]
)
def test_adjusting_tmin_invalid_entry(entry: str) -> None:
    """Check that entering anything other than something that can be converted into a floating point number results in doing nothing"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.z_max = 23.0
    controller = InteractivePlotController(model, view)
    controller.handle_adjusted_t_min(entry)
    cast(Mock, view.adjust_t_range).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()


@pytest.mark.parametrize(
    "entry", [str(value) for value in [8.0, 24.0, 23.0, 45.0, 23.6, 0.8, 0.24]]
)
def test_adjusting_tmax_valid_entry(entry: str) -> None:
    """Entering valid numbers"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.t_min = 23.0
    controller = InteractivePlotController(model, view)
    controller.handle_adjusted_t_max(entry)
    cast(Mock, view.adjust_t_range).assert_called_once_with(
        min_value=23.0, max_value=float(entry)
    )
    cast(Mock, view.update_figure).assert_called_once()


@pytest.mark.parametrize(
    "entry", ["", " ", "1,2", "1.3,4", "1-2", "bla", "2.8.24", "__/ == !##$__"]
)
def test_adjusting_tmax_invalid_entry(entry: str) -> None:
    """Check that entering anything other than something that can be converted into a floating point number results in doing nothing"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.z_max = 23.0
    controller = InteractivePlotController(model, view)
    controller.handle_adjusted_t_max(entry)
    cast(Mock, view.adjust_t_range).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()
