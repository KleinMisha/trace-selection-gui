"""
Test that the controller correctly handles incoming signals from a mock View, updates a mock Model accordingly, and optionally emits the correct signals (will be send to the main controller later).



! Using the unittest.mock.Mock to essentially create models and views adhering to their protocols without caring about actual implementation.
! This requires a bit of "a dance of types" as the type hints within the unittest library itself are not correct. Hence,
! PyLance will never be able to understand your mock has the methods of the protocol as well as those of a Mock.
! Hence the moving back-and-forth with casting things.
? Is there a way to do this simpler? Technically, I could skip this, but then autocompletion is not available (because PyLance does not understand what instance methods it should have)
"""

from typing import cast
from unittest.mock import Mock, call, patch

import numpy as np
import pytest
from numpy.typing import NDArray

from app.interactive_plot.plot_controller import (
    InterActivePlotConfig,
    InteractivePlotController,
    Model,
    View,
)


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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
    cast(Mock, model.has_data).return_value = True
    cast(Mock, model.find_nearest_data_point).return_value = (location, 23.0)
    controller.connect_line_added_to_plot(mock_handler)
    controller.handle_left_mouse_click(location, 42.0)
    cast(Mock, view.show_line_in_plot).assert_called_once_with(
        location, config.vertical_line_color
    )
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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
    controller.connect_line_removed_from_plot(mock_handler)
    cast(Mock, model.has_data).return_value = True
    controller.handle_right_mouse_click()
    cast(Mock, view.clear_last_line_from_plot).assert_called_once()
    cast(Mock, view.update_figure).assert_called_once()
    assert received_signals == ["right click"]


@pytest.mark.parametrize("location", [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0])
def test_handle_left_mouse_click_without_data(location: float) -> None:
    """
    Trigger handler at Controller: Are signals received by Model and View ?
    """
    received_signals = []

    def mock_handler(value: float) -> None:
        received_signals.append(value)

    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
    cast(Mock, model.has_data).return_value = False
    cast(Mock, model.find_nearest_data_point).return_value = (location, 23.0)
    controller.connect_line_added_to_plot(mock_handler)
    controller.handle_left_mouse_click(location, 42.0)
    cast(Mock, view.show_line_in_plot).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()
    assert received_signals == []


def test_handle_right_mouse_click_without_data() -> None:
    """tests that controller simply breaks out of the handling function if you click before data is set"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("right click")

    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
    controller.connect_line_removed_from_plot(mock_handler)
    cast(Mock, model.has_data).return_value = False
    controller.handle_right_mouse_click()
    cast(Mock, view.clear_last_line_from_plot).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()
    assert received_signals == []


@pytest.mark.parametrize("location", [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0])
def test_handle_left_mouse_click_when_locked(location: float) -> None:
    """When the click actions are locked, ignore the click in the plot area"""
    received_signals = []

    def mock_handler(value: float) -> None:
        received_signals.append(value)

    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
    controller._lock_clicks = True

    cast(Mock, model.has_data).return_value = True
    cast(Mock, model.find_nearest_data_point).return_value = (location, 23.0)
    controller.connect_line_added_to_plot(mock_handler)
    controller.handle_left_mouse_click(location, 42.0)
    cast(Mock, view.show_line_in_plot).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()
    assert received_signals == []


def test_handle_right_mouse_click_when_locked() -> None:
    """When the click actions are locked, ignore the click in the plot area"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("right click")

    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
    controller._lock_clicks = True

    controller.connect_line_removed_from_plot(mock_handler)
    cast(Mock, model.has_data).return_value = True
    controller.handle_right_mouse_click()
    cast(Mock, view.clear_last_line_from_plot).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()
    assert received_signals == []


@pytest.mark.parametrize(
    "entry", [str(value) for value in [8.0, 24.0, 23.0, 45.0, 23.6]]
)
def test_adjusting_zmin_valid_entry(entry: str) -> None:
    """Entering valid numbers"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    model.z_max = 23.0
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
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
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)
    controller.handle_adjusted_t_max(entry)
    cast(Mock, view.adjust_t_range).assert_not_called()
    cast(Mock, view.update_figure).assert_not_called()


def test_reset_for_new_trace() -> None:
    """Test resetting the plot with a new dataset with potentially section labels assigned"""
    model: Model = cast(Model, Mock(spec=Model))
    view: View = cast(View, Mock(spec=View))
    config = InterActivePlotConfig()
    controller = InteractivePlotController(model, view, config)

    class MockTrace:
        def __init__(self, t: NDArray[np.floating], z: NDArray[np.floating]) -> None:
            self.t = t
            self.z = z

    mock_trace = MockTrace(
        t=np.array([float(n + 1) for n in range(50)]), z=np.array([1.0] * 100)
    )
    mock_clicked_locations = [8, 23, 24, 45]

    with patch.object(model, attribute="get_time_point_by_index", return_value=23):
        controller.reset_for_new_trace(mock_trace, mock_clicked_locations)
        assert model.trace_data == mock_trace
        cast(Mock, view.show_t_vs_z_plot).assert_called_once_with(
            mock_trace.t, mock_trace.z, config.data_line_color
        )

        cast(Mock, view.show_line_in_plot).assert_has_calls(
            [
                call(23, config.vertical_line_color)
                for _ in range(len(mock_clicked_locations))
            ]
        )
        cast(Mock, view.update_figure).assert_called_once()
