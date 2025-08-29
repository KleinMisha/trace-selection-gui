"""
Model: Knows of the set of available labels, the current section and the current label you are considering to add/remove from it
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Section:
    """Simple representation of data with labels assigned to a particular time-range"""

    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
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
        self.sections.append(Section())

    def remove_last_section(self) -> None:
        """Remove section if possible. Avoid index error by doing nothing when no more section is available"""
        if len(self.sections) > 0:
            self.sections.pop()

    def set_start_section(self, value: int) -> None:
        """sets the starting frame for the current section"""
        self.current_section.set_start_frame(value)

    def set_end_section(self, value: int) -> None:
        """sets the final frame for the current section"""
        self.current_section.set_end_frame(value)

    def reset_sections(self, section_labels: dict[tuple[int, int], list[str]]) -> None:
        """
        Will be called by MainController when moving to the next trace.
        Parse a dictionary that maps (start_frame, end_frame) -> ["labels"] into Section objects (see definition above)
        """
        # remove all the current sections
        number_original_sections = len(self.sections)
        for _ in range(number_original_sections):
            self.remove_last_section()

        # create the new sections
        for idx, ((start_frame, end_frame), labels) in enumerate(
            section_labels.items()
        ):
            self.create_new_section()
            self.sections[idx].set_start_frame(start_frame)
            self.sections[idx].set_end_frame(end_frame)
            for label in labels:
                self.sections[idx].assign_label(label)

            # NOTE: To ensure that you will point to an index that is available --> move back to the first
            self.current_section_index = 0

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

    def sections_to_dictionary(self) -> dict[tuple[int, int], list[str]]:
        """Parse the Sections into the format the TimeTraceTools accepts / known by the Controller"""
        section_labels = {}
        for section in self.sections:
            start = section.start_frame
            end = section.end_frame
            labels = section.assigned_labels
            section_labels[(start, end)] = labels
        return section_labels

    def determine_section_boundaries(self) -> list[int]:
        """
        Parse the Sections into the set of frames where vertical lines should be shown in the plot.
        ---

        Needed to be accessed by the MainController
        """
        boundary_frames: list[int] = []
        for section in self.sections:
            if section.start_frame is not None:
                boundary_frames.append(section.start_frame)
            if section.end_frame is not None:
                boundary_frames.append(section.end_frame)
        return boundary_frames
