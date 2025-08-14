"""
Test for application-wide variables / data / states / etc. stored and/or modified by the mainModel
"""

from dataclasses import dataclass, field

import numpy as np
import pytest
from numpy.typing import NDArray

from app.main_app.main_model import MainModel

NUMBER_OF_TRACES: int = 100


@dataclass
class MockTrace:
    """Just the part that is strictly needed for MainModel to work. This type hint makes that things do not really have to change in case of data other than magnetic tweezers data"""

    t: NDArray[np.floating]
    labels: list[str] = field(default_factory=list)
    section_labels: dict[tuple[int, int], list[str]] = field(default_factory=dict)


@dataclass
class MockExperiment:
    """Just the part that is important here. Yes, we will use time_trace_tools, but this protocol specifies what the model strictly needs."""

    traces: list[MockTrace]

    def get_labels(self) -> dict[str, list[str]]: ...
    def set_labels(self, labels: dict[str, list[str]]) -> None: ...
    def get_section_labels(self) -> dict[str, dict[tuple[int, int], list[str]]]: ...
    def set_section_labels(
        self, section_labels: dict[str, dict[tuple[int, int], list[str]]]
    ) -> None: ...
    def __len__(self) -> int: ...


@pytest.fixture
def experiment() -> MockExperiment:
    mock_traces = [MockTrace(np.array([n] * 100)) for n in range(NUMBER_OF_TRACES)]
    return MockExperiment(mock_traces)


def test_move_to_next(experiment: MockExperiment) -> None:
    """easy case: navigate to the next trace"""

    model = MainModel(current_index=0)
    model._set_experiment(experiment)  # type: ignore
    model.move_to_next()
    assert model.current_index == 1


def test_move_to_next_start_from_last(experiment: MockExperiment) -> None:
    """the model should handle correctly to not attempt moving past the final index"""
    model = MainModel(current_index=NUMBER_OF_TRACES - 1)
    model._set_experiment(experiment)  # type: ignore
    model.move_to_next()
    assert model.current_index == NUMBER_OF_TRACES - 1


def test_move_to_previous(experiment: MockExperiment) -> None:
    """easy case: navigate to the previous trace"""
    model = MainModel(current_index=NUMBER_OF_TRACES - 1)
    model._set_experiment(experiment)  # type: ignore
    model.move_to_previous()
    assert model.current_index == NUMBER_OF_TRACES - 2


def test_move_to_previous_from_first(experiment: MockExperiment) -> None:
    """the model should handle correctly to not attempt moving past the first index"""
    model = MainModel(current_index=0)
    model._set_experiment(experiment)  # type: ignore
    model.move_to_previous()
    assert model.current_index == 0


@pytest.mark.parametrize(
    "index,expected_percentage",
    [(n, n / (NUMBER_OF_TRACES - 1) * 100.0) for n in range(NUMBER_OF_TRACES)],
)
def test_calculating_percentage_progressed(
    experiment: MockExperiment, index: int, expected_percentage: float
) -> None:
    """Even though this is a very simple calculation, writing this test ensures this will be implemented in the model"""
    model = MainModel(current_index=index)
    model._set_experiment(experiment)  # type: ignore
    assert model.progress_percentage == expected_percentage


@pytest.mark.parametrize(
    "target",
    [n for n in range(NUMBER_OF_TRACES)],
)
def test_jump_to_index(experiment: MockExperiment, target: int) -> None:
    """Manually jump to selected index"""
    model = MainModel()
    model._set_experiment(experiment)  # type: ignore
    model.jump_to_index(target)
    assert model.current_index == target


def test_jump_to_index_before_first(experiment: MockExperiment) -> None:
    """ensure the model handles this correctly"""
    model = MainModel()
    model._set_experiment(experiment)  # type: ignore
    model.jump_to_index(target=-1)
    assert model.current_index == 0


def test_jump_to_index_beyond_last(experiment: MockExperiment) -> None:
    """ensure the model handles this correctly"""
    model = MainModel()
    model._set_experiment(experiment)  # type: ignore
    model.jump_to_index(target=NUMBER_OF_TRACES)
    assert model.current_index == NUMBER_OF_TRACES - 1
