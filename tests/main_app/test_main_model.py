"""
Test 'business logic'.
Test for application-wide variables / data / states / etc. stored and/or modified by the mainModel

NOTE: TimeTraceTools already tests that functions used from there work. hence, we are not going to test that loading an experiment from file / writing it to file works as desired.
NOTE: Hence, we just use unittest.mock.Mock to assert the correct functions are called. Their internal logic is already assured to be correct by the time_trace_tools library itself.
"""

from typing import Any, cast
from unittest.mock import Mock, PropertyMock

import numpy as np
import pytest
from time_trace_tools.data_types.magnetic_tweezers_experiment import (
    MagneticTweezersExperiment as Experiment,
)
from time_trace_tools.data_types.magnetic_tweezers_trace import (
    MagneticTweezersTrace as Trace,
)

from app.main_app.main_model import MainModel, MissingExperimentError

NUMBER_OF_TRACES = 100
NUMBER_OF_DATA_POINTS = 10


def mock_trace(name: str) -> Trace:
    """
    create a dummy (MagneticTweezers)Trace
    """
    t = np.array([n for n in range(NUMBER_OF_DATA_POINTS)])
    x = np.array([8.0] * len(t))
    y = np.array([24.0] * len(t))
    z = np.array([23.0] * len(t))
    return Trace(ID=name, t=t, x=x, y=y, z=z)


@pytest.fixture
def experiment() -> Experiment:
    """Mock the experiment data with dummy Trace data (see function above)"""
    traces = [mock_trace(name=f"trace_{n + 1}") for n in range(NUMBER_OF_TRACES)]
    return Experiment(ID="mock", traces=traces)


def test_move_to_next_trace(experiment: Experiment) -> None:
    """easy case: navigate to the next trace"""
    model = MainModel(_current_trace_index=0)
    model._set_experiment(experiment)
    for times_moved in range(1, NUMBER_OF_TRACES - 1):
        model.move_to_next_trace()
        assert model._current_trace_index == times_moved


def test_do_not_move_past_last_trace(experiment: Experiment) -> None:
    """make sure you just do not move past the final trace. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = MainModel(_current_trace_index=NUMBER_OF_TRACES - 1)
    model._set_experiment(experiment)
    model.move_to_next_trace()
    assert model._current_trace_index == NUMBER_OF_TRACES - 1


def test_move_to_previous_trace(experiment: Experiment) -> None:
    """easy case: navigate to the previous trace"""
    model = MainModel(_current_trace_index=NUMBER_OF_TRACES - 1)
    model._set_experiment(experiment)
    for times_moved in range(1, NUMBER_OF_TRACES):
        model.move_to_previous_trace()
        assert model._current_trace_index == (NUMBER_OF_TRACES - 1) - times_moved


def test_do_not_move_beyond_first_label(experiment: Experiment) -> None:
    """make sure you just do not move back when already at the first trace. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = MainModel(_current_trace_index=0)
    model._set_experiment(experiment)
    model.move_to_previous_trace()
    assert model._current_trace_index == 0


@pytest.mark.parametrize(
    "index,expected_percentage",
    [(n, n / (NUMBER_OF_TRACES - 1) * 100.0) for n in range(NUMBER_OF_TRACES)],
)
def test_calculating_percentage_progressed(
    experiment: Experiment, index: int, expected_percentage: float
) -> None:
    """Even though this is a very simple calculation, writing this test ensures this will not be somehow broken when refactoring code"""
    model = MainModel(_current_trace_index=index)
    model._set_experiment(experiment)
    assert model.progress_percentage == expected_percentage


@pytest.mark.parametrize(
    "target",
    [n for n in range(NUMBER_OF_TRACES)],
)
def test_jump_to_index(experiment: Experiment, target: int) -> None:
    """Manually jump to selected index"""
    model = MainModel()
    model._set_experiment(experiment)
    model.jump_to_index(target)
    assert model._current_trace_index == target


def test_jump_to_index_before_first(experiment: Experiment) -> None:
    """ensure the model handles this correctly"""
    model = MainModel()
    model._set_experiment(experiment)
    model.jump_to_index(target=-1)
    assert model._current_trace_index == 0


def test_jump_to_index_beyond_last(experiment: Experiment) -> None:
    """ensure the model handles this correctly"""
    model = MainModel()
    model._set_experiment(experiment)
    model.jump_to_index(target=NUMBER_OF_TRACES)
    assert model._current_trace_index == NUMBER_OF_TRACES - 1


def test_initial_values() -> None:
    """Check defaults for the percentage progressed, current trace index, etc. , i.e. before having loaded (raw) data"""
    model = MainModel()
    assert model.progress_percentage == 0.0
    assert model.current_trace_id == ""
    assert model._number_of_traces == 0
    assert not model.has_experiment
    assert not model.has_traces
    with pytest.raises(MissingExperimentError):
        model.current_trace
    with pytest.raises(MissingExperimentError):
        model.write_labels()
    with pytest.raises(MissingExperimentError):
        model.write_section_labels()
    with pytest.raises(MissingExperimentError):
        model.load_labels()
    with pytest.raises(MissingExperimentError):
        model.load_section_labels()
    with pytest.raises(MissingExperimentError):
        model.find_index_from_id("ANYTHING")


def test_number_of_traces_in_experiment(experiment: Experiment) -> None:
    """Check that if you did load an experiment, the number of traces are determined correctly"""
    model = MainModel()
    model._set_experiment(experiment)
    assert model._number_of_traces == NUMBER_OF_TRACES


@pytest.mark.parametrize(
    "index, expected_id",
    [(n, f"trace_{n + 1}") for n in range(NUMBER_OF_TRACES)],
)
def test_retrieving_trace_labels(
    experiment: Experiment, index: int, expected_id: str
) -> None:
    """Check that if you did load an experiment, the current trace ID is correctly interpreted"""
    model = MainModel(_current_trace_index=index)
    model._set_experiment(experiment)
    assert model.current_trace_id == expected_id


def test_calling_label_update() -> None:
    """Simple checks to see data gets updated properly (call to the correct method)"""
    model = MainModel()
    mock_experiment = cast(Experiment, Mock())
    cast(Any, type(model)).current_trace = PropertyMock(return_value=Mock())
    model._set_experiment(mock_experiment)
    new_labels = ["mock", "mock-a-dee", "mock-a-doo"]
    model.update_trace_labels(new_labels)
    cast(Mock, model.current_trace.add_labels).assert_called_once_with(new_labels)


def test_calling_section_labels_update() -> None:
    """Simple check to see that data gets updated properly (call to the correct method)"""
    model = MainModel()
    mock_experiment = cast(Experiment, Mock())
    cast(Any, type(model)).current_trace = PropertyMock(return_value=Mock())
    model._set_experiment(mock_experiment)

    nicknames = {
        (32, 34): ["Shaq", "Big Diesel", "Big Aristotle", "Superman", "Shaq-foo"],
        (34, None): ["Giannis", "Greek Freak", "The Alphabet"],
        (15, None): ["The Joker"],
        (None, 30): ["Baby-faced assassin", "Chef Curry", "Steph"],
    }
    model.update_trace_section_labels(nicknames)
    cast(
        Mock, model.current_trace.add_labelled_sections_from_dictionary
    ).assert_called_once_with(nicknames)


@pytest.mark.parametrize(
    "trace_id, expected_index", [(f"trace_{n + 1}", n) for n in range(NUMBER_OF_TRACES)]
)
def test_fetching_index_by_trace_id(
    experiment: Experiment, trace_id: str, expected_index: int
) -> None:
    """test method that serves as the bridge between the view, controller, and model"""
    model = MainModel()
    model._set_experiment(experiment)
    assert model.find_index_from_id(trace_id) == expected_index
