"""
Model responsibility: Store/update the list of labels
"""

from dataclasses import dataclass, field


@dataclass
class ItemList:
    labels: list[str] = field(default_factory=list)

    def add_item(self, name) -> None:
        self.labels.append(name)

    def remove_item(self, name) -> None:
        self.labels.remove(name)

    def get_items(self) -> list[str]:
        return self.labels
