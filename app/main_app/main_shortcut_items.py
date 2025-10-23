""" """

from enum import Enum, auto


class MainShortcutID(Enum):
    """
    Defines logical identifiers for elements in the MainApp component that (can) get a shortcut assigned to them

    These enum values serve as the shared contract between:
      - `MainConfig.get_shortcuts()`, which provides the actual key sequences,
      - `MainView.get_shortcut_targets()`, which exposes the corresponding UI targets,
      - and `MainController.apply_config()`, which ties both together.

    By using Enum members instead of plain strings, we ensure:
      * auto-completion and refactor-safety
      * compile-time checking in IDEs / linters
      * an easy way to validate that every config key matches a defined shortcut
    """

    MENU_FILE_OPEN = auto()
    MENU_FILE_SAVE = auto()
    MENU_FILE_SAVE_AS = auto()
    NEXT_TRACE = auto()
    PREVIOUS_TRACE = auto()
