"""
Model knows of data that must either be shared with other components or is directly the data saved to a file / send back to the user.

NOTE: To shorten the code in this file, I made it directly depend on the `MagneticTweezersTrace`  and `MagneticTweezersExperiment` classes
    from `time_trace_tools`.
    ? If you want to make this more general. Define Protocols for the Trace and Experiment that define the parts that define those attributes and methods
    ? accessed by the MainModel.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from time_trace_tools.data_io.labels import (
    read_json,
    write_experiment_labels,
    write_experiment_section_labels,
)
from time_trace_tools.data_io.raw_mt import read_mt_data
from time_trace_tools.data_types.magnetic_tweezers_experiment import (
    MagneticTweezersExperiment as Experiment,
)
from time_trace_tools.data_types.magnetic_tweezers_trace import (
    MagneticTweezersTrace as Trace,
)


class MissingExperimentError(Exception):
    """
    To indicate you cannot perform certain operations before having loaded the experiment
    ---
    !NOTE: this is actually a programming error. The assertions in the code below are there to:
    ! 1. make the type-checker happy
    ! 2. specify a contract to all developers: please make sure the MainController guards against calling this method when there is no data.
    """

    def __init__(self, function_name: str) -> None:
        super().__init__(
            f"Called '{function_name}' before loading any data.\nAdd a guard clause at appropriate point in code (typically in the MainController)"
        )


@dataclass
class MainModel:
    """
    Main Model handles application-wide variables/data not pertaining to a particular component/widget.
    Methods/properties defined serve as an API for the MainController, i.e. the MainController can call these methods to give instructions to the Model.
    ? Possibly make this more generic, so it could also work with other types of Experiments/TimeTraces ?
    """

    path_to_experiment_data: Path = Path("")
    path_to_labels: Path = Path("")
    path_to_section_labels: Path = Path("")
    _experiment: Optional[Experiment] = None
    _current_trace_index: int = 0

    @property
    def has_traces(self) -> bool:
        return bool(self._experiment) and bool(self._experiment.traces)

    @property
    def has_experiment(self) -> bool:
        return bool(self._experiment)

    @property
    def current_trace(self) -> Trace:
        if not self._experiment:
            raise MissingExperimentError("current_trace")
        return self._experiment.traces[self._current_trace_index]

    @property
    def current_trace_id(self) -> str:
        if not self._experiment:
            return ""
        return self.current_trace.ID

    @property
    def _number_of_traces(self) -> int:
        """
        Default to 0, such that things will also work before having loaded any data.
        """
        if not self._experiment:
            return 0
        return len(self._experiment)

    @property
    def progress_percentage(self) -> float:
        """
        Determine how far the current index is w.r.t the length to the data set.
        default to 0%, such that things will also work before having loaded any data.
        """
        if not self._experiment:
            return 0.0
        return self._current_trace_index / (self._number_of_traces - 1) * 100.0

    def move_to_next_trace(self) -> None:
        """Do nothing if you are pointing at the final trace"""
        if self._current_trace_index < (self._number_of_traces - 1):
            self._current_trace_index += 1

    def move_to_previous_trace(self) -> None:
        """Do nothing if you are pointing at the first trace"""
        if self._current_trace_index > 0:
            self._current_trace_index -= 1

    def jump_to_index(self, target: int) -> None:
        """
        Clip the result to be from [0, N), with N the number of traces.
        This is to prevent things from crashing too easily due to typos by the user in the UI
        """
        next_index = target
        if target < 0:
            next_index = 0
        elif target >= self._number_of_traces:
            next_index = self._number_of_traces - 1

        self._current_trace_index = next_index

    def find_index_from_id(self, trace_id: str) -> int:
        """determine the index you want to jump to"""
        if not self._experiment:
            raise MissingExperimentError("find_index_from_id")
        target_trace = self._experiment.fetch_trace(trace_id)
        return self._experiment.traces.index(target_trace)

    def set_file_path_to_experiment_data(self, path: Path | str) -> None:
        self.path_to_experiment_data = Path(path)

    def set_file_path_to_labels(self, path: Path | str) -> None:
        self.path_to_labels = Path(path)

    def set_file_path_to_section_labels(self, path: Path | str) -> None:
        self.path_to_section_labels = Path(path)

    def load_experiment_data(self) -> None:
        """
        Read the data from file. Wrapper around functionality from TimeTraceTools
        ? Possibly make this more generic, so it could also work with other types of Experiments/TimeTraces ?
        ? Unfortunately, we must use some kind of specific implementation at some point. Not sure if it can be deferred to later? Use some kind of BaseMainModel?
        ? Pro: possible generality. Con: Inheritance / coupling + a bit more complicated code for functionality not even sure will be used by the lab anyways. 99% of users are going to use it for magnetic tweezers data anyways.
        """
        # Instantiate your magnetic tweezers Experiment
        experiment = Experiment(ID="")
        experiment.load_raw_data(
            self.path_to_experiment_data, data_loader_fn=read_mt_data
        )
        experiment.create_traces_from_raw_data()
        self._set_experiment(experiment)

    def _set_experiment(self, experiment: Experiment) -> None:
        self._experiment = experiment

    def update_trace_labels(self, new_labels: list[str]) -> None:
        """
        Updates the data (on the current trace) when receiving the information from the `LabelPanelModel` (the controller).
        """
        return self.current_trace.add_labels(new_labels)

    def update_trace_section_labels(
        self, new_section_labels: dict[tuple[int, int], list[str]]
    ) -> None:
        """
        Updates the data (on the current trace) when receiving the information from the `LabelPanelModel` (the controller).
        """
        self.current_trace.add_labelled_sections_from_dictionary(new_section_labels)

    def load_labels(self) -> None:
        if not self._experiment:
            raise MissingExperimentError("load_labels")
        labels_from_file = read_json(self.path_to_labels)
        self._experiment.set_labels(labels_from_file)

    def load_section_labels(self) -> None:
        if not self._experiment:
            raise MissingExperimentError("load_section_labels")
        section_labels_from_file = read_json(self.path_to_section_labels)
        self._experiment.set_section_labels(section_labels_from_file)

    def write_labels(self) -> None:
        """Write the data to file. Wrapper around functionality from TimeTraceTools"""
        if not self._experiment:
            raise MissingExperimentError("write_labels")
        write_experiment_labels(self._experiment, self.path_to_labels)

    def write_section_labels(self) -> None:
        """Write the data to file. Wrapper around functionality from TimeTraceTools"""
        if not self._experiment:
            raise MissingExperimentError("write_section_labels")
        write_experiment_section_labels(self._experiment, self.path_to_labels)
