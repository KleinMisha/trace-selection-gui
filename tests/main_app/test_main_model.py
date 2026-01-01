"""
Test 'business logic'.
Test for application-wide variables / data / states / etc. stored and/or modified by the mainModel

NOTE: TimeTraceTools already tests that functions used from there work. hence, we are not going to test that loading an experiment from file / writing it to file works as desired.
NOTE: Hence, we just use unittest.mock.Mock to assert the correct functions are called. Their internal logic is already assured to be correct by the time_trace_tools library itself.
"""

from typing import cast
from unittest.mock import Mock, PropertyMock, patch

import numpy as np
import pytest
from time_trace_tools.data_types.magnetic_tweezers_experiment import (
    MagneticTweezersExperiment as Experiment,
)
from time_trace_tools.data_types.magnetic_tweezers_trace import (
    MagneticTweezersTrace as Trace,
)

from app.core.exceptions import UnsupportedFileTypeError
from app.core.file_types import FileAction, FileType
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
    model = MainModel(current_trace_index=0)
    model._set_experiment(experiment)
    for times_moved in range(1, NUMBER_OF_TRACES - 1):
        model.move_to_next_trace()
        assert model.current_trace_index == times_moved


def test_do_not_move_past_last_trace(experiment: Experiment) -> None:
    """make sure you just do not move past the final trace. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = MainModel(current_trace_index=NUMBER_OF_TRACES - 1)
    model._set_experiment(experiment)
    model.move_to_next_trace()
    assert model.current_trace_index == NUMBER_OF_TRACES - 1


def test_move_to_previous_trace(experiment: Experiment) -> None:
    """easy case: navigate to the previous trace"""
    model = MainModel(current_trace_index=NUMBER_OF_TRACES - 1)
    model._set_experiment(experiment)
    for times_moved in range(1, NUMBER_OF_TRACES):
        model.move_to_previous_trace()
        assert model.current_trace_index == (NUMBER_OF_TRACES - 1) - times_moved


def test_do_not_move_beyond_first_label(experiment: Experiment) -> None:
    """make sure you just do not move back when already at the first trace. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = MainModel(current_trace_index=0)
    model._set_experiment(experiment)
    model.move_to_previous_trace()
    assert model.current_trace_index == 0


@pytest.mark.parametrize(
    "target",
    [n for n in range(NUMBER_OF_TRACES)],
)
def test_jump_to_index(experiment: Experiment, target: int) -> None:
    """Manually jump to selected index"""
    model = MainModel()
    model._set_experiment(experiment)
    model.jump_to_index(target)
    assert model.current_trace_index == target


def test_jump_to_index_before_first(experiment: Experiment) -> None:
    """ensure the model handles this correctly"""
    model = MainModel()
    model._set_experiment(experiment)
    model.jump_to_index(target=-1)
    assert model.current_trace_index == 0


def test_jump_to_index_beyond_last(experiment: Experiment) -> None:
    """ensure the model handles this correctly"""
    model = MainModel()
    model._set_experiment(experiment)
    model.jump_to_index(target=NUMBER_OF_TRACES)
    assert model.current_trace_index == NUMBER_OF_TRACES - 1


def test_initial_values() -> None:
    """Check defaults for the current trace index, etc. , i.e. before having loaded (raw) data"""
    model = MainModel()
    assert model.current_trace_id == ""
    assert model.number_of_traces == 0
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
    assert model.number_of_traces == NUMBER_OF_TRACES


@pytest.mark.parametrize(
    "index, expected_id",
    [(n, f"trace_{n + 1}") for n in range(NUMBER_OF_TRACES)],
)
def test_retrieving_trace_labels(
    experiment: Experiment, index: int, expected_id: str
) -> None:
    """Check that if you did load an experiment, the current trace ID is correctly interpreted"""
    model = MainModel(current_trace_index=index)
    model._set_experiment(experiment)
    assert model.current_trace_id == expected_id


def test_calling_label_update() -> None:
    """Simple checks to see data gets updated properly (call to the correct method)"""
    model = MainModel()
    mock_experiment = cast(Experiment, Mock())
    with patch.object(
        MainModel,
        attribute="current_trace",
        new_callable=PropertyMock,
    ) as _:
        model._set_experiment(mock_experiment)
        new_labels = ["mock", "mock-a-dee", "mock-a-doo"]
        model.update_trace_labels(new_labels)
        assert set(model.current_trace.labels) == set(new_labels)


def test_calling_section_labels_update() -> None:
    """Simple check to see that data gets updated properly (call to the correct method)"""
    model = MainModel()
    mock_experiment = cast(Experiment, Mock())
    with patch.object(
        MainModel,
        attribute="current_trace",
        new_callable=PropertyMock,
    ) as _:
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


def test_only_updating_current_trace_sections(experiment: Experiment) -> None:
    """Check that when moving to a different trace, only the previous trace got the updated data"""
    model = MainModel()
    model._set_experiment(experiment)

    # update the current trace's labels
    nicknames = {
        (32, 34): ["Shaq", "Big Diesel", "Big Aristotle", "Superman", "Shaq-foo"],
        (34, None): ["Giannis", "Greek Freak", "The Alphabet"],
        (15, None): ["The Joker"],
        (None, 30): ["Baby-faced assassin", "Chef Curry", "Steph"],
    }
    model.update_trace_section_labels(nicknames)

    for key, labels in nicknames.items():
        assert set(model.current_trace.section_labels[key]) == set(labels)

    # change focus
    model.move_to_next_trace()

    # should not have anything assigned to this trace
    assert model.current_trace.section_labels == {}

    # move back and check updates are still applied
    model.move_to_previous_trace()
    for key, labels in nicknames.items():
        assert set(model.current_trace.section_labels[key]) == set(labels)


def test_only_updating_current_trace_labels(experiment: Experiment) -> None:
    """Check that when moving to a different trace, only the previous trace got the updated data"""
    model = MainModel()
    model._set_experiment(experiment)

    # update the current trace's labels
    nicknames = ["Shaq", "Big Diesel", "Big Aristotle", "Superman", "Shaq-foo"]

    model.update_trace_labels(nicknames)

    assert set(model.current_trace.labels) == set(nicknames)

    # change focus
    model.move_to_next_trace()

    # should not have anything assigned to this trace
    assert model.current_trace.labels == []

    # move back and check updates are still applied
    model.move_to_previous_trace()
    assert set(model.current_trace.labels) == set(nicknames)


def test_update_only_new_labels(
    experiment: Experiment,
) -> None:
    """
    The update should only take newly added labels into account, do not keep appending already added labels
    """
    model = MainModel()
    model._set_experiment(experiment)
    # add labels to the current trace:
    nicknames_1 = ["Shaq", "Big Diesel"]
    nicknames_2 = nicknames_1 + ["Big Aristotle", "Superman", "Shaq-foo"]
    model.update_trace_labels(nicknames_1)
    assert set(model.current_trace.labels) == set(nicknames_1)

    # calling the update a second time ("mimics a call from MainController to change focus to another trace, again with the first trace as the original focus")
    model.update_trace_labels(nicknames_1)
    assert set(model.current_trace.labels) == set(nicknames_1)

    # now add more labels, the labels should now include all labels
    model.update_trace_labels(nicknames_2)
    assert set(model.current_trace.labels) == set(nicknames_2)


def test_replacing_labels(experiment: Experiment) -> None:
    """update the labels, when completely removing the old ones / replacing by new ones"""
    model = MainModel()
    model._set_experiment(experiment)
    # add labels to the current trace:
    nicknames_1 = ["Shaq", "Big Diesel"]
    nicknames_2 = ["Big Aristotle", "Superman", "Shaq-foo"]
    model.update_trace_labels(nicknames_1)
    assert set(model.current_trace.labels) == set(nicknames_1)

    # replace the labels by a non-overlapping set
    model.update_trace_labels(nicknames_2)
    assert set(model.current_trace.labels) == set(nicknames_2)


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


def test_loading_invalid_file() -> None:
    """Make sure to raise an exception when user tries to open a file of the wrong type."""
    model = MainModel()
    with (
        patch.object(MainModel, attribute="_set_experiment") as mock_setter,
        patch.object(
            MainModel, "_validate_file_extension", side_effect=UnsupportedFileTypeError
        ),
    ):
        with pytest.raises(UnsupportedFileTypeError):
            model.load_experiment_data()

        mock_setter.assert_not_called()


def test_adding_default_extension_labels(experiment: Experiment) -> None:
    """Allow user to 'forget' to add a file extension when selecting the output path"""
    model = MainModel()
    model._set_experiment(experiment)
    model.set_file_path_to_labels("mock")

    expected_extension = FileType.LABELS.extensions_for(FileAction.SAVE)[0]
    assert str(model.path_to_labels) == f"mock{expected_extension}"


def test_adding_default_extension_sections(experiment: Experiment) -> None:
    """Allow user to 'forget' to add a file extension when selecting the output path"""
    model = MainModel()
    model._set_experiment(experiment)
    model.set_file_path_to_labels("mock")

    expected_extension = FileType.SECTION_LABELS.extensions_for(FileAction.SAVE)[0]
    assert str(model.path_to_labels) == f"mock{expected_extension}"


def test_write_valid_labels_file(experiment: Experiment) -> None:
    """Check that selecting a file without extension still safely makes it through the writing process (because of the above)"""
    model = MainModel()
    model._set_experiment(experiment)
    model.set_file_path_to_labels("mock")

    with (
        patch.object(
            MainModel, attribute="_validate_file_extension", return_value=True
        ),
        patch("app.main_app.main_model.write_experiment_labels") as mock_writer,
    ):
        model.write_labels()
        mock_writer.assert_called_once()


def test_write_valid_sections_file(experiment: Experiment) -> None:
    """Check that selecting a file without extension still safely makes it through the writing process (because of the above)"""
    model = MainModel()
    model._set_experiment(experiment)
    model.set_file_path_to_section_labels("mock")

    with (
        patch.object(
            MainModel, attribute="_validate_file_extension", return_value=True
        ),
        patch("app.main_app.main_model.write_experiment_section_labels") as mock_writer,
    ):
        model.write_section_labels()
        mock_writer.assert_called_once()
