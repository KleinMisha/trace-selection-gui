"""
Test listening to input and emitting signals accordingly.
NOTE: Simulates user clicks with pyQt specific functionalities. So that part is not framework agnostic.
"""

import numpy as np
import pytest
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from app.interactive_plot.plot_view import InterActivePlotView


# Test sending the correct signals:
@pytest.mark.parametrize(
    "fraction",
    ([n * 0.1 for n in range(1, 10)]),
)
def test_left_mouse_click_in_plot(qtbot: QtBot, fraction: float) -> None:
    """
    mimic clicking at a specified location within the figure and check that the View sends the signal that a left mouse click button is pressed at the specified location
    """
    received_signals = []

    def mock_click_handler(num_1: float, num_2: float) -> None:
        """For the click events, the signal emitted will be a pair of floating point numbers representing the location of the click"""
        received_signals.append(num_1)
        received_signals.append(num_2)

    view = InterActivePlotView()
    view.connect_left_mouse_click(mock_click_handler)
    view.show()
    qtbot.waitExposed(view)

    # click location: convert the desired click coordinates into the pixel coordinates that the qt_bot understands

    # coordinates according to Matplotlib:
    x_pixel, y_pixel = view.ax.transData.transform((fraction, fraction))

    # Qt and Matplotlib use different origins (bottom left corner vs top left corner)
    _, canvas_height = view.canvas.get_width_height()
    qt_pixel = QPoint(int(x_pixel), int(canvas_height - y_pixel))

    qtbot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=qt_pixel)

    # Assert that the signal emitted is the expected location
    expected_x, expected_y = view.ax.transData.inverted().transform([x_pixel, y_pixel])
    assert isinstance(received_signals[0], float)
    assert isinstance(received_signals[1], float)
    assert expected_x == pytest.approx(received_signals[0], abs=1e-2)
    assert expected_y == pytest.approx(received_signals[1], abs=1e-2)


def test_right_mouse_click_in_plot(qtbot: QtBot) -> None:
    """
    A right-mouse click will be used for undoing an action. Hence, it's location does not actually matter
    """
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("right click")

    view = InterActivePlotView()
    view.connect_right_mouse_click(mock_handler)
    view.show()
    qtbot.waitExposed(view)

    canvas_width, canvas_height = view.canvas.get_width_height()
    center_of_canvas = QPoint(canvas_width // 2, canvas_height // 2)
    qtbot.mouseClick(view.canvas, Qt.MouseButton.RightButton, pos=center_of_canvas)

    assert received_signals[0] == "right click"


def test_left_click_outside_of_the_plot(qtbot: QtBot) -> None:
    """Make sure no signal gets emitted when the user clicks anywhere outside of the figure itself"""
    received_signals = []

    def mock_click_handler(signal_1: float, signal_2: float) -> None:
        received_signals.append(signal_1)
        received_signals.append(signal_2)

    view = InterActivePlotView()
    view.connect_left_mouse_click(mock_click_handler)
    view.show()
    qtbot.waitExposed(view)

    canvas_width, canvas_height = view.canvas.get_width_height()

    # click somewhere beyond the width/height of the canvas
    outside_canvas_1 = QPoint(
        canvas_width - 10,
        canvas_height - 10,
    )
    # click somewhere beyond the width/height of the canvas
    outside_canvas_2 = QPoint(
        canvas_width + 10,
        canvas_height + 10,
    )

    qtbot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=outside_canvas_1)
    qtbot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=outside_canvas_2)
    assert len(received_signals) == 0


def test_right_click_outside_of_the_plot(qtbot: QtBot) -> None:
    """Make sure no signal gets emitted when the user clicks anywhere outside of the figure itself"""
    received_signals = []

    def mock_handler() -> None:
        received_signals.append("right click")

    view = InterActivePlotView()
    view.connect_right_mouse_click(mock_handler)
    view.show()
    qtbot.waitExposed(view)

    canvas_width, canvas_height = view.canvas.get_width_height()

    # click somewhere beyond the width/height of the canvas
    outside_canvas_1 = QPoint(
        canvas_width - 10,
        canvas_height - 10,
    )
    # click somewhere beyond the width/height of the canvas
    outside_canvas_2 = QPoint(
        canvas_width + 10,
        canvas_height + 10,
    )

    qtbot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=outside_canvas_1)
    qtbot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=outside_canvas_2)
    assert len(received_signals) == 0


def test_mouse_clicks_do_not_mix(qtbot: QtBot) -> None:
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
    view.show()
    qtbot.waitExposed(view)
    canvas_width, canvas_height = view.canvas.get_width_height()
    center_of_canvas = QPoint(canvas_width // 2, canvas_height // 2)

    qtbot.mouseClick(view.canvas, Qt.MouseButton.LeftButton, pos=center_of_canvas)
    expected_x, expected_y = view.ax.transData.inverted().transform(
        [canvas_width // 2, canvas_height // 2]
    )

    assert len(received_signals) == 2
    assert pytest.approx(received_signals[0], rel=1e-2) == expected_x
    assert pytest.approx(received_signals[1], rel=1e-2) == expected_y

    qtbot.mouseClick(view.canvas, Qt.MouseButton.RightButton, pos=center_of_canvas)
    assert len(received_signals) == 3
    assert received_signals[-1] == "right click"


@pytest.mark.parametrize(
    "entered_value", [n for n in range(10)] + [float(n) for n in range(10)]
)
def test_adjust_z_min(qtbot: QtBot, entered_value: int | float) -> None:
    """
    test entering a valid number.
    Adjust the text directly.
    Use the bot to hit the ENTER button, such that the editingFinished signal should get triggered.
    """
    received_signals = []

    def mock_handler(value: str) -> None:
        received_signals.append(float(value))

    view = InterActivePlotView()
    view.connect_adjusted_z_min(mock_handler)
    view.zPosMinEdit.setText(str(entered_value))
    qtbot.keyClick(view.zPosMinEdit, Qt.Key.Key_Return)

    assert isinstance(received_signals[0], float)
    assert received_signals[0] == entered_value


@pytest.mark.parametrize(
    "entered_value", [n for n in range(10)] + [float(n) for n in range(10)]
)
def test_adjust_z_max(qtbot: QtBot, entered_value: int | float) -> None:
    """test entering a valid number"""
    received_signals = []

    def mock_handler(value: str) -> None:
        received_signals.append(float(value))

    view = InterActivePlotView()
    view.connect_adjusted_z_max(mock_handler)
    view.zPosMaxEdit.setText(str(entered_value))
    qtbot.keyClick(view.zPosMaxEdit, Qt.Key.Key_Return)

    assert isinstance(received_signals[0], float)
    assert received_signals[0] == entered_value


@pytest.mark.parametrize(
    "entered_value", [n for n in range(10)] + [float(n) for n in range(10)]
)
def test_adjust_t_min(qtbot: QtBot, entered_value: int | float) -> None:
    """test entering a valid number"""
    received_signals = []

    def mock_handler(value: str) -> None:
        received_signals.append(float(value))

    view = InterActivePlotView()
    view.connect_adjusted_t_min(mock_handler)
    view.timeMinEdit.setText(str(entered_value))
    qtbot.keyClick(view.timeMinEdit, Qt.Key.Key_Return)

    assert isinstance(received_signals[0], float)
    assert received_signals[0] == entered_value


@pytest.mark.parametrize(
    "entered_value", [n for n in range(10)] + [float(n) for n in range(10)]
)
def test_adjust_t_max(qtbot: QtBot, entered_value: int | float) -> None:
    """test entering a valid number"""
    received_signals = []

    def mock_handler(value: str) -> None:
        received_signals.append(float(value))

    view = InterActivePlotView()
    view.connect_adjusted_t_max(mock_handler)
    view.timeMaxEdit.setText(str(entered_value))
    qtbot.keyClick(view.timeMaxEdit, Qt.Key.Key_Return)

    assert isinstance(received_signals[0], float)
    assert received_signals[0] == entered_value


# Test receiving the correct signals:
def test_update_t_vs_z_plot(qapp: QApplication) -> None:
    """Confirm the matplotlib figure gets updated as expected. Trivial, but an additional safety net when refactoring code"""
    view = InterActivePlotView()
    view.show_t_vs_z_plot(np.array([1.0]), np.array([1.0]), color="black")
    view.update_figure()

    assert len(view._all_lines) == 1
    assert len(view._vertical_lines) == 0
    curve = view._all_lines[0]
    assert curve.get_xdata() == np.array([1.0])
    assert curve.get_ydata() == np.array([1.0])


@pytest.mark.parametrize("location", [23, 45, 8, 24, 6])
def test_adding_line_to_plot(qapp: QApplication, location: float) -> None:
    """Confirm the matplotlib figure gets updated as expected. Trivial, but an additional safety net when refactoring code"""
    view = InterActivePlotView()
    view.show_line_in_plot(time_point=location, color="black")
    view.update_figure()

    assert len(view._all_lines) == 1
    assert len(view._vertical_lines) == 1
    vertical_line = view._vertical_lines[0]
    line_x = np.array(vertical_line.get_xdata())
    assert all(x == location for x in line_x)


def test_removing_last_added_line_from_plot(qapp: QApplication) -> None:
    """First add, then remove. If the previous test passes, this is correctly checking the removing operation"""
    view = InterActivePlotView()
    view.show_line_in_plot(time_point=1.0, color="black")
    view.show_line_in_plot(time_point=2.0, color="black")
    view.update_figure()

    assert len(view._all_lines) == 2
    assert len(view._vertical_lines) == 2
    view.clear_last_line_from_plot()
    view.update_figure()
    assert len(view._all_lines) == 1
    assert len(view._vertical_lines) == 1
    vertical_line = view._vertical_lines[0]
    line_x = np.array(vertical_line.get_xdata())
    assert np.all(line_x == 1.0)


def test_removing_all_lines_from_plot(qapp: QApplication) -> None:
    view = InterActivePlotView()
    view.show_t_vs_z_plot(np.array([1.0]), np.array([1.0]), color="black")
    view.show_line_in_plot(1.0, color="black")
    view.show_line_in_plot(2.0, color="black")
    view.update_figure()

    assert len(view._all_lines) == 3
    assert len(view._vertical_lines) == 2
    view.clear_all_lines_from_plot()
    view.update_figure()

    assert len(view._all_lines) == 1
    assert len(view._vertical_lines) == 0


def test_clear_plot(qapp: QApplication) -> None:
    """should completely clear everything from the figure"""
    view = InterActivePlotView()
    view.show_t_vs_z_plot(np.array([23.0]), np.array([45.0]), color="black")
    view.show_line_in_plot(23.0, color="black")
    view.show_line_in_plot(45.0, color="black")
    view.show_line_in_plot(8.0, color="black")
    view.show_line_in_plot(24.0, color="black")
    view.show_line_in_plot(6.0, color="black")
    view.show_line_in_plot(3.0, color="black")
    view.update_figure()

    assert len(view._all_lines) == 7
    assert len(view._vertical_lines) == 6
    view.clear_figure()
    view.update_figure()
    assert len(view._all_lines) == 0


def test_do_not_remove_if_no_vertical_line(qapp: QApplication) -> None:
    """
    Make sure the plotted curve remains, regardless of the number of calls to the remove last line.
    This will later be connected to left-mouse button. Hence, this basically checks that the user cannot do weird stuff by "right-clicking once too often"

    The plotted time trace should remain no matter.
    """
    view = InterActivePlotView()
    view.show_t_vs_z_plot(np.array([23.0]), np.array([45.0]), color="black")
    view.show_line_in_plot(8.0, color="black")
    view.show_line_in_plot(24.0, color="black")
    view.update_figure()
    assert len(view._vertical_lines) == 2
    assert len(view._all_lines) == 3

    # regular: remove all the added lines, one by one
    view.clear_last_line_from_plot()
    view.clear_all_lines_from_plot()
    assert len(view._vertical_lines) == 0
    assert len(view._all_lines) == 1

    # the actual test: try to remove once more, even though there is nothing to be removed
    view.clear_last_line_from_plot()
    assert len(view._vertical_lines) == 0
    assert len(view._all_lines) == 1


def test_toggle_click_lock() -> None:
    """Simple check if signals are connected properly"""
    received_signals = []

    def mock_toggle_handler(state: bool) -> None:
        received_signals.append(state)

    view = InterActivePlotView()
    view.connect_lock_clicks_toggled_signal(mock_toggle_handler)

    # turn lock on
    view.lockToggle.toggle()
    assert received_signals == [True]

    # turn lock off
    view.lockToggle.toggle()
    assert received_signals == [True, False]

    # turn back on for good measures
    view.lockToggle.toggle()
    assert received_signals == [True, False, True]


def test_toggle_is_turned_off_initially() -> None:
    """Simple contract: Ensure the toggle is turned off at startup. The logic of the Controller depends on this test passing."""
    view = InterActivePlotView()
    assert not view.lockToggle.isChecked()
