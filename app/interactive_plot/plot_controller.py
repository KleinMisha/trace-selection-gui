"""
Controller: handle user interaction events (signals received from the View) and pass the View the appropriate data from the Model to then be shown in the View
"""

from typing import Callable, Protocol, Sequence, TypeAlias, Union

import numpy as np
from numpy.typing import NDArray

from app.interactive_plot.plot_model import TraceData

# Type hint for anything that is a proper color input.
Color: TypeAlias = Union[
    str,  # "red", "#FF00FF", "0.5", "C0"
    tuple[float, float, float],  # RGB
    tuple[float, float, float, float],  # RGBA
    Sequence[float],  # list/array of floats
    np.ndarray,  # numpy array
]


class Model(Protocol):
    """Protocol for the InteractivePlot Model"""

    @property
    def t_min(self) -> float: ...

    @property
    def t_max(self) -> float: ...

    @property
    def z_min(self) -> float: ...

    @property
    def z_max(self) -> float: ...

    @property
    def trace_data(self) -> TraceData: ...


class View(Protocol):
    """Protocol for the InteractivePlot View"""

    # logic to change the view
    def update_t_vs_z_plot(
        self, t: NDArray[np.floating], z: NDArray[np.floating]
    ) -> None: ...

    def show_line_in_plot(self, time_point: float, color: Color) -> None: ...
    def clear_lines_from_plot(self) -> None: ...
    def clear_figure(self) -> None: ...

    def update_z_range(self, min: float, max: float) -> None: ...
    def update_t_range(self, min: float, max: float) -> None: ...

    # connect methods on the Controller side to the pyqtSignals
    def connect_left_mouse_click(
        self, callback: Callable[[float, float], None]
    ) -> None: ...
    def connect_right_mouse_click(
        self, callback: Callable[[float, float], None]
    ) -> None: ...
    def connect_adjusted_z_min(self, callback: Callable[[float], None]) -> None: ...
    def connect_adjusted_z_max(self, callback: Callable[[float], None]) -> None: ...
    def connect_adjusted_t_min(self, callback: Callable[[float], None]) -> None: ...
    def connect_adjusted_t_max(self, callback: Callable[[float], None]) -> None: ...


class InteractivePlotController:
    def __init__(self, model: Model, view: View) -> None:
        pass

    def handle_left_mouse_click(self, x_loc: float, y_loc: float) -> None: ...
    def handle_right_mouse_click(self, x_loc: float, y_loc: float) -> None: ...
    def handle_adjusted_z_min(self, value: float) -> None: ...
    def handle_adjusted_z_max(self, value: float) -> None: ...
    def handle_adjusted_t_min(self, value: float) -> None: ...
    def handle_adjusted_t_max(self, value: float) -> None: ...

    def update_view(self) -> None:
        """wrapper function to update all the stuff in the plot. Might be good to have"""
