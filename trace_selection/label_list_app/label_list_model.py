"""
Model responsibility: Store/update the list of labels
"""

from dataclasses import dataclass, field


@dataclass
class LabelList:
    labels: list[str] = field(default_factory=list)

    def add_label(self, name) -> None:
        self.labels.append(name)

    def remove_label(self, name) -> None:
        self.labels.remove(name)

    def get_labels(self) -> list[str]:
        return self.labels
