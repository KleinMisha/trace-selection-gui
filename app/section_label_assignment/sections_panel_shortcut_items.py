from enum import Enum, auto


class SectionsPanelShortcutID(Enum):
    """
    Defines logical identifiers for elements in the SectionsPanel component that (can) get a shortcut assigned to them

    These enum values serve as the shared contract between:
      - `SectionsPanelConfig.get_shortcuts()`, which provides the actual key sequences,
      - `SectionsPanelView.get_shortcut_targets()`, which exposes the corresponding UI targets,
      - and `SectionsPanelController.apply_config()`, which ties both together.

    By using Enum members instead of plain strings, we ensure:
      * auto-completion and refactor-safety
      * compile-time checking in IDEs / linters
      * an easy way to validate that every config key matches a defined shortcut
    """

    ASSIGN = auto()
    UNASSIGN = auto()
    NEXT_LABEL = auto()
    PREVIOUS_LABEL = auto()
    NEXT_SECTION = auto()
    PREVIOUS_SECTION = auto()
