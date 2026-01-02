from enum import Enum, auto


class LabelPanelShortcutID(Enum):
    """
    Defines logical identifiers for elements in the LabelPanel component that (can) get a shortcut assigned to them

    These enum values serve as the shared contract between:
      - `LabelPanelConfig.get_shortcuts()`, which provides the actual key sequences,
      - `LabelPanelView.get_shortcut_targets()`, which exposes the corresponding UI targets,
      - and `LabelPanelController.apply_config()`, which ties both together.

    By using Enum members instead of plain strings, we ensure:
      * auto-completion and refactor-safety
      * compile-time checking in IDEs / linters
      * an easy way to validate that every config key matches a defined shortcut
    """

    ASSIGN = auto()
    UNASSIGN = auto()
    NEXT = auto()
    PREVIOUS = auto()
