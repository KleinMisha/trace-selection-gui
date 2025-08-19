"""
Model: Knows of the set of available labels, a index pointing to the currently selected label, labels that are assigned
"""

from dataclasses import dataclass, field


@dataclass
class LabelPanelModel:
    available_labels: list[str] = field(default_factory=list)
    assigned_labels: list[str] = field(default_factory=list)
    current_idx: int = 0

    @property
    def current_label(self) -> str:
        return self.available_labels[self.current_idx]

    @property
    def current_is_assigned(self) -> bool:
        return self.current_label in self.assigned_labels

    def assign_current_label(self) -> None:
        """Avoid duplicates: only assign when not already done before"""
        if not self.current_is_assigned:
            self.assigned_labels.append(self.current_label)

    def unassign_current_label(self) -> None:
        """Avoid attempting to remove something that is not there (smooth operation when eventually clicking twice)"""
        if self.current_is_assigned:
            self.assigned_labels.remove(self.current_label)

    def move_to_next(self) -> None:
        """Avoid moving past the final available label (smooth operation when eventually clicking multiple times)"""
        if self.current_idx < len(self.available_labels) - 1:
            self.current_idx += 1

    def move_to_previous(self) -> None:
        """Avoid moving into negative indices. Stop when you are already at the first label"""
        if self.current_idx > 0:
            self.current_idx -= 1

    def reset_assigned_labels(self, labels_new_trace: list[str]) -> None:
        """Will be called by MainController when moving to the next trace"""
        self.assigned_labels = labels_new_trace

    def update_available_labels(self, updated_list: list[str]) -> None:
        """Will be called by the MainController when done editing the ItemList"""
        original_list = self.available_labels.copy()
        # make sure to keep pointing at the same label when you shrink the label list
        if len(updated_list) < len(original_list) and self.current_idx > 0:
            self.current_idx -= 1

        self.available_labels = updated_list
