"""
Application-wide information:
    - index of the current trace displayed
    - progress
    - files to read from / save into etc...
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol, Sequence

import numpy as np
from numpy.typing import NDArray
from time_trace_tools.data_io.labels import (
    read_json,
    write_experiment_labels,
    write_experiment_section_labels,
)
from time_trace_tools.data_io.raw_mt import read_mt_data
from time_trace_tools.data_types.magnetic_tweezers_experiment import (
    MagneticTweezersExperiment,
)


class Trace(Protocol):
    """Just the part that is strictly needed for MainModel to work. This type hint makes that things do not really have to change in case of data other than magnetic tweezers data"""

    @property
    def t(self) -> NDArray[np.floating]: ...
    @property
    def labels(self) -> list[str]: ...
    @property
    def section_labels(self) -> dict[tuple[int, int], list[str]]: ...


class Experiment(Protocol):
    """Just the part that is important here. Yes, we will use time_trace_tools, but this protocol specifies what the model strictly needs."""

    @property
    def traces(self) -> Sequence[Trace]: ...
    def get_labels(self) -> dict[str, list[str]]: ...
    def set_labels(self, labels: dict[str, list[str]]) -> None: ...
    def get_section_labels(self) -> dict[str, dict[tuple[int, int], list[str]]]: ...
    def set_section_labels(
        self, section_labels: dict[str, dict[tuple[int, int], list[str]]]
    ) -> None: ...
    def __len__(self) -> int: ...


@dataclass
class MainModel:
    """
    Main Model handles application-wide variables/data not pertaining to a particular component/widget.
    Methods/properties defined serve as an API for the MainController, i.e. the MainController can call these methods to give instructions to the Model.
    ? Possibly make this more generic, so it could also work with other types of Experiments/TimeTraces ?
    """

    current_index: int = 0
    path_to_experiment_data: Path = Path("")
    path_to_labels: Path = Path("")
    path_to_section_labels: Path = Path("")

    @property
    def _number_of_traces(self) -> int:
        return len(self._experiment) if self._experiment is not None else 0

    def move_to_next(self) -> None:
        if self.current_index < (self._number_of_traces - 1):
            self.current_index += 1

    def move_to_previous(self) -> None:
        if self.current_index > 0:
            self.current_index -= 1

    def jump_to_index(self, target: int) -> None:
        next_index = target
        if target < 0:
            next_index = 0
        elif target >= self._number_of_traces:
            next_index = self._number_of_traces - 1

        self.current_index = next_index

    @property
    def progress_percentage(self) -> float:
        """
        Determine how far the current index is w.r.t the length to the data set.
        default to 0%, such that things will also work before having loaded the data.
        """
        if hasattr(self, "experiment"):
            return self.current_index / (self._number_of_traces - 1) * 100.0
        return 0.0

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
        experiment = MagneticTweezersExperiment(ID="")
        experiment.load_raw_data(
            self.path_to_experiment_data, data_loader_fn=read_mt_data
        )
        experiment.create_traces_from_raw_data()
        self._set_experiment(experiment)

    def _set_experiment(self, experiment: Experiment) -> None:
        self._experiment = experiment

    def load_labels(self) -> None:
        labels_from_file = read_json(self.path_to_labels)
        self._experiment.set_labels(labels_from_file)

    def load_section_labels(self) -> None:
        section_labels_from_file = read_json(self.path_to_section_labels)
        self._experiment.set_section_labels(section_labels_from_file)

    def write_labels(self) -> None:
        """Write the data to file. Wrapper around functionality from TimeTraceTools"""
        write_experiment_labels(self._experiment, self.path_to_labels)  # type: ignore

    def write_section_labels(self) -> None:
        """Write the data to file. Wrapper around functionality from TimeTraceTools"""
        write_experiment_section_labels(self._experiment, self.path_to_labels)  # type: ignore

    def get_current_trace(self) -> Trace:
        """
        NOTE: In principle generic implementation, given the protocol
        ! Given the specific loader function --> you know the specific Experiment type used, and therefor also the specific Trace type used
        ? Adjust return type hint?
        """
        return self._experiment.traces[self.current_index]
