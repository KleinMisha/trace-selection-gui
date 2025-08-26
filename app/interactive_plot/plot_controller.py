"""
Controller: handle user interaction events (signals received from the View) and pass the View the appropriate data from the Model to then be shown in the View
"""

from typing import Callable, Optional, Protocol, Sequence, TypeAlias, Union

import numpy as np
from numpy.typing import NDArray
from PyQt6.QtCore import QObject, pyqtSignal

from app.interactive_plot.plot_model import TraceData

# TODO: Move the following stuff into some configuration file
DEFAULT_Z_MIN = -1.0
DEFAULT_Z_MAX = 1.0
DEFAULT_T_MIN = 0.0
DEFAULT_T_MIN = 3600.0


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

    @t_min.setter
    def t_min(self, value: float) -> None: ...

    @property
    def t_max(self) -> float: ...

    @t_max.setter
    def t_max(self, value: float) -> None: ...

    @property
    def z_min(self) -> float: ...

    @z_min.setter
    def z_min(self, value: float) -> None: ...

    @property
    def z_max(self) -> float: ...

    @z_max.setter
    def z_max(self, value: float) -> None: ...

    @property
    def trace_data(self) -> TraceData | None: ...

    @trace_data.setter
    def trace_data(self, value: float) -> None: ...

    def find_nearest_data_point(self, x_coordinate: float) -> tuple[float, float]: ...


class View(Protocol):
    """Protocol for the InteractivePlot View"""

    # logic to change the view
    def update_figure(self, title: Optional[str] = None) -> None: ...
    def adjust_t_range(self, min_value: float, max_value: float): ...
    def adjust_z_range(self, min_value: float, max_value: float): ...
    def show_t_vs_z_plot(
        self, t: NDArray[np.floating], z: NDArray[np.floating]
    ) -> None: ...
    def show_line_in_plot(
        self, time_point: float, color: Optional[Color] = None
    ) -> None: ...
    def clear_last_line_from_plot(self) -> None: ...
    def clear_all_lines_from_plot(self) -> None: ...
    def clear_figure(self) -> None: ...

    # connect methods on the Controller side to the pyqtSignals
    def connect_left_mouse_click(
        self, callback: Callable[[float, float], None]
    ) -> None: ...
    def connect_right_mouse_click(self, callback: Callable[[], None]) -> None: ...
    def connect_adjusted_z_min(self, callback: Callable[[str], None]) -> None: ...
    def connect_adjusted_z_max(self, callback: Callable[[str], None]) -> None: ...
    def connect_adjusted_t_min(self, callback: Callable[[str], None]) -> None: ...
    def connect_adjusted_t_max(self, callback: Callable[[str], None]) -> None: ...


class InteractivePlotController(QObject):
    # signals send back upwards to the main controller
    _line_added_to_plot_signal = pyqtSignal(float)
    _line_removed_from_plot_signal = pyqtSignal()

    def __init__(self, model: Model, view: View) -> None:
        super().__init__()
        self.model = model
        self.view = view

        # connect callbacks :: Listening to the View's signals
        self.view.connect_left_mouse_click(self.handle_left_mouse_click)
        self.view.connect_right_mouse_click(self.handle_right_mouse_click)
        self.view.connect_adjusted_z_min(self.handle_adjusted_z_min)
        self.view.connect_adjusted_z_max(self.handle_adjusted_z_max)
        self.view.connect_adjusted_t_min(self.handle_adjusted_t_min)
        self.view.connect_adjusted_t_max(self.handle_adjusted_t_max)

    # Callbacks for signals emitted by the View
    def handle_left_mouse_click(self, x_click: float, _: float) -> None:
        """
        triggers when user clicks in the plot (left mouse button)
        NOTE: The signal emitted by the View has the x and y coordinates of where the user clicked.
        However, we technically do not need both for now. Hence, the "_" as an argument.
        ? Should this be removed?
        """
        t_data_point, _ = self.model.find_nearest_data_point(x_click)
        print("Hello")

        # TODO: use the main controller to pass the appropriate color
        self.view.show_line_in_plot(t_data_point)
        self.view.update_figure()

        # inform the main Controller
        self._send_line_added_to_plot_signal(t_data_point)

    def handle_right_mouse_click(self) -> None:
        """
        triggers when the user clicks in the plot (right mouse button)
        """
        self.view.clear_last_line_from_plot()
        self.view.update_figure()

        # inform the main Controller
        self._send_line_removed_from_plot_signal()

    def handle_adjusted_z_min(self, entry: str) -> None:
        """triggers when done adjusting. For a smooth working UI, do nothing unless the entered value is valid"""

        if self._is_valid_number(entry):
            self.model.z_min = float(entry)
            z_min = self.model.z_min
            z_max = self.model.z_max
            self.view.adjust_z_range(min_value=z_min, max_value=z_max)
            self.view.update_figure()

    def handle_adjusted_z_max(self, entry: str) -> None:
        """triggers when done adjusting. For a smooth working UI, do nothing unless the entered value is valid"""

        if self._is_valid_number(entry):
            self.model.z_max = float(entry)
            z_min = self.model.z_min
            z_max = self.model.z_max
            self.view.adjust_z_range(min_value=z_min, max_value=z_max)
            self.view.update_figure()

    def handle_adjusted_t_min(self, entry: str) -> None:
        """triggers when done adjusting. For a smooth working UI, do nothing unless the entered value is valid"""

        if self._is_valid_number(entry):
            self.model.t_min = float(entry)
            t_min = self.model.t_min
            t_max = self.model.t_max
            self.view.adjust_t_range(min_value=t_min, max_value=t_max)
            self.view.update_figure()

    def handle_adjusted_t_max(self, entry: str) -> None:
        """triggers when done adjusting. For a smooth working UI, do nothing unless the entered value is valid"""

        if self._is_valid_number(entry):
            self.model.t_max = float(entry)
            t_min = self.model.t_min
            t_max = self.model.t_max
            self.view.adjust_t_range(min_value=t_min, max_value=t_max)
            self.view.update_figure()

    # Actions that should effect cross-components. Send a signal to allow the main controller to handle things.
    # NOTE: Strictly not needed to have these methods explicitly, but makes for better readability in my opinion.
    def _send_line_added_to_plot_signal(self, location: float) -> None:
        self._line_added_to_plot_signal.emit(location)

    def _send_line_removed_from_plot_signal(self) -> None:
        self._line_removed_from_plot_signal.emit()

    def connect_line_added_to_plot(self, callback: Callable[[float], None]) -> None:
        self._line_added_to_plot_signal.connect(callback)

    def connect_line_removed_from_plot(self, callback: Callable[[], None]) -> None:
        self._line_removed_from_plot_signal.connect(callback)

    @staticmethod
    def _is_valid_number(entry: str) -> bool:
        has_at_most_one_decimal_point = entry.count(".") <= 1
        is_positive_number = entry.count("-") == 0
        is_negative_number = entry.count("-") == 1 and entry[0] == "-"
        what_remains_are_digits = (
            entry.replace(".", "", 1).replace("-", "", 1).isdigit()
        )
        return (
            has_at_most_one_decimal_point
            and (is_positive_number or is_negative_number)
            and what_remains_are_digits
        )
