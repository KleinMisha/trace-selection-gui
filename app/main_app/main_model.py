"""
Application-wide information:
    - index of the current trace displayed
    - progress
    - files to read from / save into etc...
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Generic, Iterable, Protocol, TypeVar

T = TypeVar("T")


@dataclass
class Experiment(Protocol, Generic[T]):
    """Just the part that is important here. Yes, we will use time_trace_tools, but this protocol specifies what the model strictly needs."""

    traces: list[T] = field(default_factory=list)

    def get_labels(self) -> None: ...
    def get_section_labels(self) -> None: ...
    def fetch_trace(self, id: str) -> T: ...


@dataclass
class MainModel:
    """
    # todo: POPULATE THIS AFTER THE TESTS ARE DONE
    """

    # todo: instantiate without actual data, only needed once you explicitly call the `open()` from the menu
    experiment: Experiment | None = None
    current_index: int = 0
    path_in: Path = Path("")
    path_out: Path = Path("")

    def move_to_next(self) -> None: ...
    def move_to_previous(self) -> None: ...
    def jump_to_index(self, target: int) -> None: ...

    @property
    def progress_percentage(self) -> float:
        """Determine how far the current index is w.r.t the length to the data set"""

    def set_file_path_in(self, path: Path | str) -> None:
        self.path_in = Path(path)

    def set_file_path_out(self, path: Path | str) -> None:
        self.path_out = Path(path)

    def load_data() -> None:
        """Read the data from file. Wrapper around functionality from TimeTraceTools"""

    def _set_experiment(self, experiment: MagneticTweezersExperiment) -> None:
        self.experiment = experiment

    def write_data() -> None:
        """Write the data to file. Wrapper around functionality from TimeTraceTools"""

    def get_current_trace() -> TimeTrace:
        """
        # todo: Import TimeTraceTools
        #! Did not yet import TimeTraceTools
        """
        ...
