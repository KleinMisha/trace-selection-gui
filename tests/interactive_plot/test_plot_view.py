"""
Test listening to input and emitting signals accordingly.
NOTE: Simulates user clicks with pyQt specific functionalities. So that part is not framework agnostic.
"""

import numpy as np
import pytest
from PyQt6.QtCore import QPoint, Qt
from pytestqt.qtbot import QtBot

from app.interactive_plot.plot_view import InterActivePlotView


# Test sending the correct signals:
@pytest.mark.parametrize(
    "x_coordinate, y_coordinate",
    ([(n * 0.1, n * 0.1) for n in range(10)]),
)
def test_left_mouse_click_in_plot(
    x_coordinate: float, y_coordinate: float, qt_bot: QtBot
) -> None:
    """
    mimic clicking at a specified location within the figure and check that the View sends the signal that a left mouse click button is pressed at the specified location
    """
    received_signals = []

    def mock_click_handler(signal_1: float, signal_2: float) -> None:
        """For the click events, the signal emitted will be a pair of floating point numbers representing the location of the click"""
        received_signals.append((signal_1, signal_2))

    view = InterActivePlotView()
    view.connect_left_mouse_click(mock_click_handler)

    # click location: convert the desired click coordinates into the pixel coordinates that the qt_bot understands
    x_mpl, y_mpl = view.ax.transData.transform(
        (x_coordinate, y_coordinate)
    )  # coordinates according to Matplotlib

    # flip the y-location to adhere to the convention used by qt on where the origin is placed (top left corner vs bottom left corner)
    _, canvas_height = view.canvas.get_width_height()
    x_qt = int(x_mpl)
    y_qt = int(canvas_height - y_mpl)
    click_location = QPoint(x_qt, y_qt)

    # perform the click and check the correct signals have been emitted by the view
    qt_bot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=click_location)

    # Assert that the signal emitted is the expected location
    assert isinstance(received_signals[0], float)
    assert isinstance(received_signals[1], float)
    assert received_signals[0] == x_coordinate
    assert received_signals[1] == y_coordinate


def test_right_mouse_click_in_plot(qt_bot: QtBot) -> None:
    """
    A right-mouse click will be used for undoing an action. Hence, it's location does not actually matter
    """
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("right click")

    view = InterActivePlotView()
    view.connect_right_mouse_click(mock_handler)
    canvas_width, canvas_height = view.canvas.get_width_height()
    center_of_canvas = (canvas_width // 2, canvas_height // 2)

    qt_bot.mouseClick(view.canvas, Qt.MouseButton.RightButton, pos=center_of_canvas)
    assert received_signals[0] == "right click"


def test_left_click_outside_of_the_plot(qt_bot: QtBot) -> None:
    """Make sure no signal gets emitted when the user clicks anywhere outside of the figure itself"""
    received_signals = []

    def mock_click_handler(signal_1: float, signal_2: float) -> None:
        received_signals.append((signal_1, signal_2))

    view = InterActivePlotView()
    view.connect_left_mouse_click(mock_click_handler)
    canvas_width, canvas_height = view.canvas.get_width_height()
    outside_canvas_1 = (
        canvas_width - 10,
        canvas_height - 10,
    )  # click somewhere beyond the width/height of the canvas
    outside_canvas_2 = (
        canvas_width + 10,
        canvas_height + 10,
    )  # click somewhere beyond the width/height of the canvas
    qt_bot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=outside_canvas_1)
    qt_bot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=outside_canvas_2)
    assert len(received_signals) == 0


def test_right_click_outside_of_the_plot(qt_bot: QtBot) -> None:
    """Make sure no signal gets emitted when the user clicks anywhere outside of the figure itself"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("right click")

    view = InterActivePlotView()
    view.connect_right_mouse_click(mock_handler)
    canvas_width, canvas_height = view.canvas.get_width_height()
    outside_canvas_1 = (
        canvas_width - 10,
        canvas_height - 10,
    )  # click somewhere beyond the width/height of the canvas
    outside_canvas_2 = (
        canvas_width + 10,
        canvas_height + 10,
    )  # click somewhere beyond the width/height of the canvas
    qt_bot.mouseClick(view.canvas, Qt.MouseButton.RightButton, pos=outside_canvas_1)
    qt_bot.mouseClick(view.canvas, Qt.MouseButton.RightButton, pos=outside_canvas_2)
    assert len(received_signals) == 0


def test_mouse_clicks_do_not_mix(qt_bot: QtBot) -> None:
    """Make sure the handlers are not reversed somehow. Maybe trivial"""
    received_signals = []

    def mock_left_handler(num_1: float, num_2: float) -> None:
        received_signals.append(num_1)
        received_signals.append(num_2)

    def mock_right_handler() -> None:
        received_signals.append("right click")

    view = InterActivePlotView()
    view.connect_left_mouse_click(mock_left_handler)
    view.connect_right_mouse_click(mock_right_handler)
    canvas_width, canvas_height = view.canvas.get_width_height()
    center_of_canvas = (canvas_width // 2, canvas_height // 2)

    qt_bot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=center_of_canvas)
    assert len(received_signals) == 2
    assert received_signals[0] == center_of_canvas[0]
    assert received_signals[1] == center_of_canvas[1]

    qt_bot.mouseClick(view.canvas, Qt.MouseButton.RightButton, pos=center_of_canvas)
    assert len(received_signals) == 3
    assert received_signals[-1] == "right click"


@pytest.mark.parametrize(
    "entered_value", [n for n in range(10)] + [float(n) for n in range(10)]
)
def test_adjust_z_min(entered_value: int | float) -> None:
    """test entering a valid number"""
    received_signals = []

    def mock_handler(value: float) -> None:
        received_signals.append(value)

    view = InterActivePlotView()
    view.connect_adjusted_z_min(mock_handler)
    view.zPosMinEdit.setText(str(entered_value))
    assert isinstance(received_signals[0], float)
    assert received_signals[0] == entered_value


@pytest.mark.parametrize(
    "entered_value", [n for n in range(10)] + [float(n) for n in range(10)]
)
def test_adjust_z_max(entered_value: int | float) -> None:
    """test entering a valid number"""
    received_signals = []

    def mock_handler(value: float) -> None:
        received_signals.append(value)

    view = InterActivePlotView()
    view.connect_adjusted_z_max(mock_handler)
    view.zPosMinEdit.setText(str(entered_value))
    assert isinstance(received_signals[0], float)
    assert received_signals[0] == entered_value


@pytest.mark.parametrize(
    "entered_value", [n for n in range(10)] + [float(n) for n in range(10)]
)
def test_adjust_t_min(entered_value: int | float) -> None:
    """test entering a valid number"""
    received_signals = []

    def mock_handler(value: float) -> None:
        received_signals.append(value)

    view = InterActivePlotView()
    view.connect_adjusted_t_min(mock_handler)
    view.zPosMinEdit.setText(str(entered_value))
    assert isinstance(received_signals[0], float)
    assert received_signals[0] == entered_value


@pytest.mark.parametrize(
    "entered_value", [n for n in range(10)] + [float(n) for n in range(10)]
)
def test_adjust_t_max(entered_value: int | float) -> None:
    """test entering a valid number"""
    received_signals = []

    def mock_handler(value: float) -> None:
        received_signals.append(value)

    view = InterActivePlotView()
    view.connect_adjusted_t_max(mock_handler)
    view.zPosMinEdit.setText(str(entered_value))
    assert isinstance(received_signals[0], float)
    assert received_signals[0] == entered_value


# Test receiving the correct signals:
def test_update_t_vs_z_plot() -> None:
    """Confirm the matplotlib figure gets updated as expected. Trivial, but an additional safety net when refactoring code"""

    view = InterActivePlotView()
    view.update_t_vs_z_plot(np.array([1.0]), np.array([1.0]))

    assert len(view.ax.get_lines()) == 1
    curve = view.ax.get_lines()[0]
    assert curve.get_xdata() == np.array([1.0])
    assert curve.get_ydata() == np.array([1.0])


def test_adding_line_to_plot(location: float) -> None:
    """Confirm the matplotlib figure gets updated as expected. Trivial, but an additional safety net when refactoring code"""
    view = InterActivePlotView()
    view.show_line_in_plot(time_point=location)
    assert len(view.ax.get_lines()) == 1
    vertical_line = view.ax.get_lines()[0]
    line_x = np.array(vertical_line.get_xdata())
    assert all(x == location for x in line_x)


def test_removing_last_added_line_from_plot() -> None:
    """First add, then remove. If the previous test passes, this is correctly checking the removing operation"""
    view = InterActivePlotView()
    view.show_line_in_plot(time_point=1.0)
    view.show_line_in_plot(time_point=2.0)
    assert len(view.ax.get_lines()) == 2
    view.clear_last_line_from_plot()
    assert len(view.ax.get_lines()) == 1
    vertical_line = view.ax.get_lines()[0]
    line_x = np.array(vertical_line.get_xdata())
    assert all(x == 1.0 for x in line_x)


def test_removing_all_lines_from_plot() -> None:
    view = InterActivePlotView()
    view.show_line_in_plot(1.0)
    view.show_line_in_plot(2.0)
    assert len(view.ax.get_lines()) == 2
    view.clear_all_lines_from_plot()
    assert len(view.ax.get_lines()) == 0


def test_clear_plot() -> None:
    """should completely clear everything from the figure"""
    view = InterActivePlotView()
    view.update_t_vs_z_plot(np.array([23.0]), np.array([45.0]))
    view.show_line_in_plot(23.0)
    view.show_line_in_plot(45.0)
    view.show_line_in_plot(8.0)
    view.show_line_in_plot(24.0)
    view.show_line_in_plot(6.0)
    view.show_line_in_plot(3.0)
    assert len(view.ax.get_lines()) == 7
    view.clear_figure()
    assert len(view.ax.get_lines()) == 0
