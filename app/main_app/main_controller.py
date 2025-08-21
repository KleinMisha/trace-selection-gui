"""
The MainController will be `the brains of the whole operation`
- handles direct communication with the MainModel and MainView (much like the individual component's controllers)
- handles communication between components (and components with the main app) via sending/receiving signals from the individual controllers.

Hence, the MainController knows of:
- the main app's Model and View
- the Controllers of the components.
"""

from enum import Enum, auto
from typing import Generic, Mapping, Protocol, TypeVar


class Component(Enum):
    """
    Register the name of the new component here.

    TODO: Move this into the `main.py` (the entry-point) as that is the only part of the code that must actually know of the different options
    TODO: In this code, it is enough for the Controller to understand `Component` as a type hint.
    """

    ITEM_LIST = auto()
    INTERACTIVE_PLOT = auto()
    LABEL_PANEL = auto()
    SECTIONS_PANEL = auto()


class File(Enum):
    """
    The kinds of files to be opened/saved
    """

    RAW_DATA = auto()
    LABELS = auto()
    SECTION_LABELS = auto()


M = TypeVar("M", bound=object)
V = TypeVar("V", bound=object)


class ComponentController(Generic[M, V], Protocol):
    """
    Just to indicate that the components registered at the mainController are their controllers.
    Only truly important part that defines the type of a Controller object : It holds a model and view object.
    """

    model: M
    view: V


class Model(Protocol):
    pass


class View(Protocol):
    pass


class MainController:
    """
    todo: populate specifics after having written the tests
    """

    def __init__(
        self,
        model: Model,
        view: View,
        components: Mapping[Component, ComponentController],
    ) -> None:
        self.main_model = model
        self.main_view = view
        # a dictionary mapping the name of the available component (see Enum above) to the corresponding controller
        self.components = components

        # Connect (listen) to incoming signals:

    def build_composite_ui(self) -> None:
        """
        Place Components into their placeholders in the MainView
        ----
        The MainView has a set of empty QWidgets with the same name as the component View we intend to use to populate it
        """

    # main app logic
    def close_app(self) -> None:
        """Checks for untracked changes"""

    def handle_move_to_next_trace(self) -> None: ...
    def handle_move_to_prev_trace(self) -> None: ...
    def handle_jump_to_trace(self) -> None: ...
    def handle_menu_file_open(self) -> None: ...
    def handle_menu_file_save(self) -> None: ...
    def handle_menu_file_save_as(self) -> None: ...
    def handle_menu_load_labels(
        self,
    ) -> None: ...  # TODO: Implement this into the menuBar + define the signal to be send by the MainView
    def handle_menu_load_sections(
        self,
    ) -> None: ...  # TODO: Implement this into the menuBar + define the signal to be send by the MainView
    def handle_changed_ref_bead(self) -> None:
        # TODO: Implement this later
        raise NotImplementedError

    def handle_toggle_subtract_ref_bead(self) -> None:
        # TODO: Implement this later
        raise NotImplementedError

    def handle_open_item_list_from_label_panel(self) -> None: ...
    def handle_open_item_list_from_sections_panel(self) -> None: ...

    def handle_line_added_in_plot(self, location: float) -> None:
        """Makes the InterActivePlot affect the SectionsPanel"""

    def handle_removed_line_from_plot(self) -> None:
        """Makes the InterActivePlot affect the SectionsPanel"""

    def handle_go_to_help_docs(self) -> None:
        # TODO: Implement this later when MkDocs website is running
        raise NotImplementedError

    def _open_file_route(self, file_type: File) -> None:
        """route to the correct function depending on the kind of file that you opened"""

    def _save_file_route(self, file_type: File) -> None:
        """route to the correct function depending on the kind of file that is being saved"""
