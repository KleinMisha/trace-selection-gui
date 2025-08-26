"""
Model: The Interactive plot must know of the data to be plotted + some axis ranges, etc.
"""

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from numpy.typing import NDArray


class TraceData(Protocol):
    """Represents the simplified version of the data container strictly needed for this part of the application"""

    @property
    def t(self) -> NDArray[np.floating]: ...

    @property
    def z(self) -> NDArray[np.floating]: ...


@dataclass
class InteractivePlotModel:
    t_min: float
    t_max: float
    z_min: float
    z_max: float
    trace_data: TraceData | None = None

    def find_nearest_data_point(self, x_coordinate: float) -> tuple[float, float]:
        """
        Find the data point closest to where the user clicked (i.e. the values used as input to this method)
        NOTE: the value leads (not the time point), because the user will like to click close to a particular feature observed.
        """

        # ? this can be made adjustable if also plots for x and y data are included.
        # ? to achieve a general version, this function must get the axis / keys you want to axis from the data as input
        if self.trace_data is None:
            raise AttributeError(
                "Cannot determine nearest-point before setting the trace data"
            )
        x_data = self.trace_data.t
        y_data = self.trace_data.z
        idx_nearest = np.argmin(abs(x_data - x_coordinate))
        return x_data[idx_nearest], y_data[idx_nearest]
