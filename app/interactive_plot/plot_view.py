"""
View: User-facing part knows of a plot that can be clicked in and some adjustable values for the plot ranges
"""

from typing import Callable, Optional, Sequence, TypeAlias, Union, cast

import matplotlib.pylab as plt
import numpy as np
from matplotlib.backend_bases import Event, MouseButton, MouseEvent
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

DEFAULT_COLOR = "skyblue"


class InterActivePlotView(QWidget, Ui_InteractivePlot):
    left_mouse_button_signal = pyqtSignal(float, float)
    right_mouse_button_signal = pyqtSignal()
    adjusted_z_min_signal = pyqtSignal(str)
    adjusted_z_max_signal = pyqtSignal(str)
    adjusted_t_min_signal = pyqtSignal(str)
    adjusted_t_max_signal = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.build_ui()

        # connect emitting signals
        self.zPosMinEdit.editingFinished.connect(self._send_z_min_adjusted_signal)
        self.zPosMaxEdit.editingFinished.connect(self._send_z_max_adjusted_signal)
        self.timeMinEdit.editingFinished.connect(self._send_t_min_adjusted_signal)
        self.timeMaxEdit.editingFinished.connect(self._send_t_max_adjusted_signal)

        self.canvas.mpl_connect("button_press_event", self._send_mouse_click_signal)

    def build_ui(self) -> None:
        """use the (compiled) UI file to build things, such that this code knows about the variable names in VSCode"""
        self.setupUi(self)
        # properly connect the Matplotlib Figure into the placeholder (QVBoxLayout)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        plot_layout = self.plotContainer.layout()
        if plot_layout is None:
            plot_layout = QVBoxLayout()
            self.plotContainer.setLayout(plot_layout)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(self.canvas)

    # logic to change the view
    def update_figure(self, title: Optional[str] = None) -> None:
        """(re)-draw
        #todo: make font sizes adjustable and have it inside a configuration file?
        """
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Bead height (µm)")
        if title is not None:
            self.ax.set_title(title)

        plt.show()

    def adjust_t_range(self, min_value: float, max_value: float):
        self.ax.set_xlim((min_value, max_value))

    def adjust_z_range(self, min_value: float, max_value: float):
        self.ax.set_ylim((min_value, max_value))

    def show_t_vs_z_plot(
        self, t: NDArray[np.floating], z: NDArray[np.floating]
    ) -> None:
        self.ax.plot(t, z)

    def show_line_in_plot(
        self, time_point: float, color: Optional[Color] = None
    ) -> None:
        if color is None:
            color = DEFAULT_COLOR
        self.ax.axvline(time_point, linestyle="dashed", color=color)

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
        self.left_mouse_button_signal.connect(callback)

    def connect_right_mouse_click(self, callback: Callable[[], None]) -> None:
        self.right_mouse_button_signal.connect(callback)

    def connect_adjusted_z_min(self, callback: Callable[[str], None]) -> None:
        self.adjusted_z_min_signal.connect(callback)

    def connect_adjusted_z_max(self, callback: Callable[[str], None]) -> None:
        self.adjusted_z_max_signal.connect(callback)

    def connect_adjusted_t_min(self, callback: Callable[[str], None]) -> None:
        self.adjusted_t_min_signal.connect(callback)

    def connect_adjusted_t_max(self, callback: Callable[[str], None]) -> None:
        self.adjusted_t_max_signal.connect(callback)

    # emit pyqtSignals depending on user input
    def _send_mouse_click_signal(self, event: Event) -> None:
        """
        Matplotlib just knows any mouse button has been used. Here we emit the signal corresponding to the type of mouse click
        (Matplotlib stores the possible options in the MouseButton Enum)
        """
        event = cast(MouseEvent, event)
        if event.button == MouseButton.LEFT:
            self.left_mouse_button_signal.emit(event.xdata, event.ydata)

        if event.button == MouseButton.RIGHT:
            self.right_mouse_button_signal.emit()

    def _send_z_min_adjusted_signal(self) -> None:
        self.adjusted_z_min_signal.emit(self.zPosMinEdit.text())

    def _send_z_max_adjusted_signal(self) -> None:
        self.adjusted_z_max_signal.emit(self.zPosMaxEdit.text())

    def _send_t_min_adjusted_signal(self) -> None:
        self.adjusted_t_min_signal.emit(self.timeMinEdit.text())

    def _send_t_max_adjusted_signal(self) -> None:
        self.adjusted_t_max_signal.emit(self.timeMaxEdit.text())
