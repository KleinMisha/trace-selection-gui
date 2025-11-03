"""
No need to test basic setting/getting (that is built-in Python stuff). Just testing the functions we wrote work as expected
"""

import numpy as np
import pytest
from time_trace_tools.data_types.magnetic_tweezers_trace import MagneticTweezersTrace

from app.core.exceptions import MissingExperimentError
from app.interactive_plot.plot_model import InteractivePlotModel


@pytest.fixture
def trace() -> MagneticTweezersTrace:
    x = np.array([float(n) for n in range(100)])
    y = np.array([float(n) for n in range(100)])
    z = np.array([float(n) for n in range(100)])
    t = np.array([float(n) for n in range(100)])
    return MagneticTweezersTrace(ID="mock", t=t, x=x, y=y, z=z)


@pytest.mark.parametrize(
    "x_coordinate, expected_x, expected_y",
    (
        [(float(n) + 0.2, float(n), float(n)) for n in range(10)]
        + [(float(n) + 0.8, float(n + 1), float(n + 1)) for n in range(10)]
    ),
)
def test_find_nearest_data_point(
    trace: MagneticTweezersTrace,
    x_coordinate: float,
    expected_x: float,
    expected_y: float,
) -> None:
    model = InteractivePlotModel(
        trace_data=trace, t_min=0.0, t_max=0.0, z_min=0.0, z_max=0.0
    )

    x_nearest, y_nearest = model.find_nearest_data_point(x_coordinate)
    assert x_nearest == expected_x
    assert y_nearest == expected_y


def test_method_calls_before_setting_data() -> None:
    """Make sure you raise a MissingExperimentError when attempting to call this method without there being any data"""
    model = InteractivePlotModel(
        trace_data=None, t_min=0.0, t_max=0.0, z_min=0.0, z_max=0.0
    )
    with pytest.raises(MissingExperimentError):
        model.find_nearest_data_point(x_coordinate=42.0)

    with pytest.raises(MissingExperimentError):
        model.get_time_point_by_index(index=0)


def test_get_time_point_by_frame_number(trace: MagneticTweezersTrace) -> None:
    model = InteractivePlotModel(
        trace_data=trace, t_min=0.0, t_max=0.0, z_min=0.0, z_max=0.0
    )
    for index in [0, 20, 40, 60, 80, 99]:
        assert model.get_time_point_by_index(index) == trace.t[index]
