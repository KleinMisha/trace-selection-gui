"""
View: User-facing part knows of a plot that can be clicked in and some adjustable values for the plot ranges
"""

from typing import Callable, Optional, Sequence, TypeAlias, Union, cast

import matplotlib.pylab as plt
import numpy as np
from matplotlib.backend_bases import Event, MouseButton, MouseEvent
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy.typing import NDArray
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from app.interactive_plot.plot_view_ui import Ui_InteractivePlot

# Type hint for anything that is a proper color input.
Color: TypeAlias = Union[
    str,  # "red", "#FF00FF", "0.5", "C0"
    tuple[float, float, float],  # RGB
    tuple[float, float, float, float],  # RGBA
    Sequence[float],  # list/array of floats
    np.ndarray,  # numpy array
]


class InterActivePlotView(QWidget, Ui_InteractivePlot):
    _left_mouse_button_signal = pyqtSignal(float, float)
    _right_mouse_button_signal = pyqtSignal()
    _adjusted_z_min_signal = pyqtSignal(str)
    _adjusted_z_max_signal = pyqtSignal(str)
    _adjusted_t_min_signal = pyqtSignal(str)
    _adjusted_t_max_signal = pyqtSignal(str)
    _lock_clicks_toggled_signal = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.build_ui()

        # connect emitting signals
        self.zPosMinEdit.editingFinished.connect(self._send_z_min_adjusted_signal)
        self.zPosMaxEdit.editingFinished.connect(self._send_z_max_adjusted_signal)
        self.timeMinEdit.editingFinished.connect(self._send_t_min_adjusted_signal)
        self.timeMaxEdit.editingFinished.connect(self._send_t_max_adjusted_signal)
        self.lockToggle.toggled.connect(self._send_lock_clicks_toggled_signal)
        self.canvas.mpl_connect("button_press_event", self._send_mouse_click_signal)

        # store configurable colors internally, to make this View independent of the configuration existing and working.
        # NOTE: These defaults are purely here for testing the View by itself (now does not require a config to work)
        self._data_line_color: Color = "black"
        self._vertical_line_color: Color = "coral"

    def build_ui(self) -> None:
        """use the (compiled) UI file to build things, such that this code knows about the variable names in VSCode"""
        self.setupUi(self)
        # properly connect the Matplotlib Figure into the placeholder (QVBoxLayout)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.fig.add_subplot(111)

        plot_layout = self.plotContainer.layout()
        if plot_layout is None:
            plot_layout = QVBoxLayout()
            self.plotContainer.setLayout(plot_layout)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(self.canvas)
        plot_layout.addWidget(self.toolbar)

    # logic to change the view
    def set_plot_colors(self, color_data: Color, color_vert_line: Color) -> None:
        """set the colors for the indicator when the light is turned on/off. Will be eventually called upon theme changes"""
        self._data_line_color = color_data
        self._vertical_line_color = color_vert_line

    def update_figure(self, title: Optional[str] = None) -> None:
        """(re)-draw
        #todo: make font sizes adjustable and have it inside a configuration file?
        """
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Bead height (µm)")
        if title is not None:
            self.ax.set_title(title)

        self.canvas.draw()

    def adjust_t_range(self, min_value: float | None, max_value: float | None):
        self.ax.set_xlim(min_value, max_value)

    def adjust_z_range(self, min_value: float | None, max_value: float | None):
        self.ax.set_ylim(min_value, max_value)

    def display_t_min(self, value: float | None) -> None:
        """To allow the controller to set things at startup. needed to properly listen to configuration file"""
        if value is not None:
            self.timeMinEdit.setText(str(value))

    def display_t_max(self, value: float | None) -> None:
        """To allow the controller to set things at startup. needed to properly listen to configuration file"""
        if value is not None:
            self.timeMaxEdit.setText(str(value))

    def display_z_min(self, value: float | None) -> None:
        """To allow the controller to set things at startup. needed to properly listen to configuration file"""
        if value is not None:
            self.zPosMinEdit.setText(str(value))

    def display_z_max(self, value: float | None) -> None:
        """To allow the controller to set things at startup. needed to properly listen to configuration file"""
        if value is not None:
            self.zPosMaxEdit.setText(str(value))

    def show_t_vs_z_plot(
        self, t: NDArray[np.floating], z: NDArray[np.floating]
    ) -> None:
        self.ax.plot(t, z, color=self._data_line_color)

    def show_line_in_plot(self, time_point: float) -> None:
        self.ax.axvline(time_point, linestyle="dashed", color=self._vertical_line_color)

    def clear_last_line_from_plot(self) -> None:
        """use the _axesvline property in matplotlib to tell if the added line is a plt.axvline() vs the regular plt.plot() call"""
        if len(self._vertical_lines) > 0:
            last_line = self._vertical_lines[-1]
            last_line.remove()

    def clear_all_lines_from_plot(self) -> None:
        """
        Remove only the vertical lines from the figure
        #todo: make sure this is connected to a button that removes all selections?
        #todo: otherwise remove this if it remains unused.
        """
        for line in self._vertical_lines:
            line.remove()

    def clear_figure(self) -> None:
        """
        Remove everything that is plotted from the figure
        """
        for line in self._all_lines:
            line.remove()

    @property
    def _vertical_lines(self) -> list[plt.Line2D]:
        """A vertical line has multiple points and all are at the same horizontal position"""
        return [
            child
            for child in self.ax.get_children()
            if isinstance(child, plt.Line2D)
            and np.all(child.get_xdata() == np.asarray(child.get_xdata())[0])
            and len(np.asarray(child.get_ydata())) > 1
        ]

    @property
    def _all_lines(self) -> list[plt.Line2D]:
        return [
            child for child in self.ax.get_children() if isinstance(child, plt.Line2D)
        ]

    # connect methods on the Controller side to the pyqtSignals
    def connect_left_mouse_click(
        self, callback: Callable[[float, float], None]
    ) -> None:
        self._left_mouse_button_signal.connect(callback)

    def connect_right_mouse_click(self, callback: Callable[[], None]) -> None:
        self._right_mouse_button_signal.connect(callback)

    def connect_adjusted_z_min(self, callback: Callable[[str], None]) -> None:
        self._adjusted_z_min_signal.connect(callback)

    def connect_adjusted_z_max(self, callback: Callable[[str], None]) -> None:
        self._adjusted_z_max_signal.connect(callback)

    def connect_adjusted_t_min(self, callback: Callable[[str], None]) -> None:
        self._adjusted_t_min_signal.connect(callback)

    def connect_adjusted_t_max(self, callback: Callable[[str], None]) -> None:
        self._adjusted_t_max_signal.connect(callback)

    def connect_lock_clicks_toggled_signal(
        self, callback: Callable[[bool], None]
    ) -> None:
        self._lock_clicks_toggled_signal.connect(callback)

    # emit pyqtSignals depending on user input
    def _send_mouse_click_signal(self, event: Event) -> None:
        """
        Matplotlib just knows any mouse button has been used. Here we emit the signal corresponding to the type of mouse click
        (Matplotlib stores the possible options in the MouseButton Enum)
        """
        event = cast(MouseEvent, event)
        if event.button == MouseButton.LEFT:
            self._left_mouse_button_signal.emit(event.xdata, event.ydata)

        if event.button == MouseButton.RIGHT:
            self._right_mouse_button_signal.emit()

    def _send_z_min_adjusted_signal(self) -> None:
        self._adjusted_z_min_signal.emit(self.zPosMinEdit.text())

    def _send_z_max_adjusted_signal(self) -> None:
        self._adjusted_z_max_signal.emit(self.zPosMaxEdit.text())

    def _send_t_min_adjusted_signal(self) -> None:
        self._adjusted_t_min_signal.emit(self.timeMinEdit.text())

    def _send_t_max_adjusted_signal(self) -> None:
        self._adjusted_t_max_signal.emit(self.timeMaxEdit.text())

    def _send_lock_clicks_toggled_signal(self, is_locked: bool) -> None:
        """Re-emit builtin signal to the controller"""
        self._lock_clicks_toggled_signal.emit(is_locked)
