"""
Application-wide information:
    - index of the current trace displayed
    - progress
    - files to read from / save into etc...
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Protocol

import numpy as np
from numpy.typing import NDArray


class HasArray(Protocol):
    """
    The actual data container can be anything with at least one numpy-array as its attributes.
    Since MainModel() does not explicitly call this anywhere, this is purely meant as a type hint for development
    """

    values: NDArray[np.floating]


ArrayOrHasArray = NDArray[np.floating] | HasArray


@dataclass
class Experiment(Protocol):
    """Just the part that is important here. Yes, we will use time_trace_tools, but this protocol specifies what the model strictly needs."""

    traces: Iterable[ArrayOrHasArray] = field(default_factory=list)

    def get_labels(self) -> None: ...
    def get_section_labels(self) -> None: ...
    def fetch_trace(self, id: str) -> ArrayOrHasArray: ...
    def __len__(self) -> int: ...


@dataclass
class MainModel:
    """
    # todo: POPULATE THIS AFTER THE TESTS ARE DONE
    """

    current_index: int = 0
    path_in: Path = Path("")
    path_out: Path = Path("")

    def move_to_next(self) -> None: ...
    def move_to_previous(self) -> None: ...
    def jump_to_index(self, target: int) -> None: ...

    @property
    def progress_percentage(self) -> float:
        """Determine how far the current index is w.r.t the length to the data set"""
        if hasattr(self, "experiment"):
            return self.current_index / (len(self.experiment) - 1) * 100.0
        return 0.0

    def set_file_path_in(self, path: Path | str) -> None:
        self.path_in = Path(path)

    def set_file_path_out(self, path: Path | str) -> None:
        self.path_out = Path(path)

    def load_data() -> None:
        """Read the data from file. Wrapper around functionality from TimeTraceTools"""

    def _set_experiment(self, experiment: Experiment) -> None:
        self.experiment = experiment

    def write_data() -> None:
        """Write the data to file. Wrapper around functionality from TimeTraceTools"""

    def get_current_trace() -> ArrayOrHasArray:
        """
        # todo: Import TimeTraceTools
        #! Did not yet import TimeTraceTools
        """
        ...
