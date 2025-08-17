"""
View: User-facing part knows of a plot that can be clicked in and some adjustable values for the plot ranges
"""

from typing import Callable, Optional, Sequence, TypeAlias, Union

import matplotlib.pylab as plt
import numpy as np
from matplotlib.backend_bases import MouseButton, MouseEvent
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy.typing import NDArray
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

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
    left_mouse_button_signal = pyqtSignal(float, float)
    right_mouse_button_signal = pyqtSignal()
    adjusted_z_min_signal = pyqtSignal(float)
    adjusted_z_max_signal = pyqtSignal(float)
    adjusted_t_min_signal = pyqtSignal(float)
    adjusted_t_max_signal = pyqtSignal(float)

    def __init__(self) -> None:
        super().__init__()
        self.build_ui()

        # properly connect the Matplotlib Figure into the placeholder (QVBoxLayout)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

    def build_ui(self) -> None:
        """use the (compiled) UI file to build things, such that this code knows about the variable names in VSCode"""
        self.setupUi(self)

    # logic to change the view
    def update_t_vs_z_plot(
        self, t: NDArray[np.floating], z: NDArray[np.floating]
    ) -> None: ...

    def show_line_in_plot(
        self, time_point: float, color: Optional[Color] = None
    ) -> None: ...
    def clear_last_line_from_plot(self) -> None: ...
    def clear_all_lines_from_plot(self) -> None: ...
    def clear_figure(self) -> None: ...

    def update_z_range(self, min: float, max: float) -> None: ...
    def update_t_range(self, min: float, max: float) -> None: ...

    # connect methods on the Controller side to the pyqtSignals
    def connect_left_mouse_click(
        self, callback: Callable[[float, float], None]
    ) -> None: ...
    def connect_right_mouse_click(self, callback: Callable[[], None]) -> None: ...
    def connect_adjusted_z_min(self, callback: Callable[[float], None]) -> None: ...
    def connect_adjusted_z_max(self, callback: Callable[[float], None]) -> None: ...
    def connect_adjusted_t_min(self, callback: Callable[[float], None]) -> None: ...
    def connect_adjusted_t_max(self, callback: Callable[[float], None]) -> None: ...

    # emit pyqtSignals depending on user input
    def _send_mouse_click_signal(self, event: MouseEvent) -> None:
        """
        Matplotlib just knows any mouse button has been used. Here we emit the signal corresponding to the type of mouse click
        (Matplotlib stores the possible options in the MouseButton Enum)
        """

    def _send_z_min_adjusted_signal(self) -> None: ...
    def _send_z_max_adjusted_signal(self) -> None: ...
    def _send_t_min_adjusted_signal(self) -> None: ...
    def _send_t_max_adjusted_signal(self) -> None: ...
