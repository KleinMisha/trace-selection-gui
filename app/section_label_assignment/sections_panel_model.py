"""
Model: Knows of the set of available labels, the current section and the current label you are considering to add/remove from it
"""

from dataclasses import dataclass, field


@dataclass
class Section:
    """Simple representation of data with labels assigned to a particular time-range"""

    start_frame: int
    end_frame: int
    assigned_labels: list[str] = field(default_factory=list)

    # expose some methods to make the syntax slightly more readable below (not strictly needed, could assign directly)
    def set_start_frame(self, value: int) -> None:
        self.start_frame = value

    def set_end_frame(self, value: int) -> None:
        self.end_frame = value

    def assign_label(self, label: str) -> None:
        self.assigned_labels.append(label)

    def unassign_label(self, label: str) -> None:
        self.assigned_labels.remove(label)


@dataclass
class SectionsPanelModel:
    available_labels: list[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    current_label_index: int = 0
    current_section_index: int = 0

    @property
    def current_label(self) -> str:
        return self.available_labels[self.current_label_index]

    @property
    def current_section(self) -> Section:
        return self.sections[self.current_section_index]

    @property
    def current_is_assigned(self) -> bool:
        return self.current_label in self.current_section.assigned_labels

    def create_new_section(self) -> None:
        """make a new section available for values to be set"""

    def remove_last_section(self) -> None: ...
    def set_start_section(self, value: int) -> None:
        """sets the starting frame for the current section"""

    def set_end_section(self, value: int) -> None:
        """sets the final frame for the current section"""

    def reset_sections(self, section_labels: dict[tuple[int, int], list[str]]) -> None:
        """
        Will be called by MainController when moving to the next trace.
        Parse a dictionary that maps (start_frame, end_frame) -> ["labels"] into Section objects (see definition above)
        """

    def assign_current_label(self) -> None:
        """
        Assign the current label to the current section.
        Avoid duplicates: only assign when not already done before
        """
        if not self.current_is_assigned:
            self.current_section.assign_label(self.current_label)

    def unassign_current_label(self) -> None:
        """
        Undo assignment of the current label to the current section
        Avoid attempting to remove something that is not there (smooth operation when eventually clicking twice)
        """
        if self.current_is_assigned:
            self.current_section.unassign_label(self.current_label)

    def move_to_next_label(self) -> None:
        """Avoid moving past the final available label (smooth operation when eventually clicking multiple times)"""
        if self.current_label_index < len(self.available_labels) - 1:
            self.current_label_index += 1

    def move_to_previous_label(self) -> None:
        """Avoid moving into negative indices. Stop when you are already at the first label"""
        if self.current_label_index > 0:
            self.current_label_index -= 1

    def move_to_next_section(self) -> None:
        """Avoid moving past the final available section (smooth operation when eventually clicking multiple times)"""
        if self.current_section_index < len(self.sections) - 1:
            self.current_section_index += 1

    def move_to_previous_section(self) -> None:
        """Avoid moving into negative indices. Stop when you are already at the first section"""
        if self.current_section_index > 0:
            self.current_section_index -= 1

    def update_available_labels(self, updated_list: list[str]) -> None:
        """Will be called by the MainController when done editing the ItemList"""
        original_list = self.available_labels.copy()
        # make sure to keep pointing at the same label when you shrink the label list
        if len(updated_list) < len(original_list) and self.current_label_index > 0:
            self.current_label_index -= 1

        self.available_labels = updated_list
