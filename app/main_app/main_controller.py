"""
The MainController will be `the brains of the whole operation`
- handles direct communication with the MainModel and MainView (much like the individual component's controllers)
- handles communication between components (and components with the main app) via sending/receiving signals from the individual controllers.

Hence, the MainController knows of:
- the main app's Model and View
- the Controllers of the components.
"""

from enum import Enum, auto
from pathlib import Path
from typing import Callable, Concatenate, Protocol, TypedDict

from app.exceptions import with_error_handling
from app.main_app.component_controller_protocols import (
    InteractivePlotController,
    ItemListController,
    LabelPanelController,
    SectionsPanelController,
)
from app.main_app.main_model import Trace
from app.state_variables import EventSeverity, LightState


class ComponentControllers(TypedDict):
    """
    Register the new components over here

    ---
    NOTE: The types here refer to protocol types.

    ---
    NOTE II: The Item list is a popup window, so we pass the controller the controller factory (the callable that takes the list of items and returns the controller), not the controller itself.
    """

    item_list: Callable[Concatenate[list[str], ...], ItemListController]
    interactive_plot: InteractivePlotController
    label_panel: LabelPanelController
    sections_panel: SectionsPanelController


class FileType(Enum):
    """
    The kinds of files to be opened/saved
    """

    RAW_DATA = auto()
    LABELS = auto()
    SECTION_LABELS = auto()


class FileAction(Enum):
    """The kinds of actions performed on a file"""

    OPEN = auto()
    SAVE = auto()


class Model(Protocol):
    """API for the MainModel"""

    path_to_experiment_data: Path = Path("")
    path_to_labels: Path = Path("")
    path_to_section_labels: Path = Path("")

    @property
    def current_trace(self) -> Trace: ...

    @property
    def current_trace_id(self) -> str: ...

    @property
    def progress_percentage(self) -> float: ...

    @property
    def has_traces(self) -> bool: ...

    def move_to_next_trace(self) -> None: ...
    def move_to_previous_trace(self) -> None: ...
    def jump_to_index(self, target: int) -> None: ...
    def set_file_path_to_experiment_data(self, path: Path | str) -> None: ...
    def set_file_path_to_labels(self, path: Path | str) -> None: ...
    def set_file_path_to_section_labels(self, path: Path | str) -> None: ...
    def load_experiment_data(self) -> None: ...
    def load_labels(self) -> None: ...
    def load_section_labels(self) -> None: ...
    def write_labels(self) -> None: ...
    def write_section_labels(self) -> None: ...
    def update_trace_labels(self, new_labels: list[str]) -> None: ...
    def update_trace_section_labels(
        self, new_section_labels: dict[tuple[int, int], list[str]]
    ) -> None: ...
    def find_index_from_id(self, trace_id: str) -> int: ...


class View(Protocol):
    """API for the MainView"""

    def display_trace_id(self, name: str) -> None: ...
    def update_progressbar(self, value: float) -> None: ...
    def toggle_indicator_saved_changes(self, state: LightState) -> None: ...
    def display_ref_beads_ids(self, names: list[str]) -> None: ...
    def ask_open_file(self, window_title: str) -> None: ...
    def ask_save_file(self, window_title: str) -> None: ...
    def open_message_box(self, msg_type: EventSeverity, message: str) -> None: ...

    def connect_next_trace(self, callback: Callable[[], None]) -> None: ...
    def connect_prev_trace(self, callback: Callable[[], None]) -> None: ...
    def connect_jump_to_trace(self, callback: Callable[[str], None]) -> None: ...
    def connect_menu_file_open(self, callback: Callable[[], None]) -> None: ...
    def connect_menu_file_save(self, callback: Callable[[], None]) -> None: ...
    def connect_menu_file_save_as(self, callback: Callable[[], None]) -> None: ...
    def connect_menu_file_import_labels(self, callback: Callable[[], None]) -> None: ...
    def connect_menu_file_import_sections(
        self, callback: Callable[[], None]
    ) -> None: ...
    def connect_file_name_selected(self, callback: Callable[[Path], None]) -> None: ...
    def connect_go_to_help_docs(self, callback: Callable[[], None]) -> None: ...


class MainController:
    """
    The MainController will be 'the brains of the whole operation'
    ---
    - handles direct communication with the MainModel and MainView (much like the individual component's controllers)
    - handles communication between components (and components with the main app) via sending/receiving signals from the individual controllers.

    Hence, the MainController knows of:
    - the main app's Model and View
    - the API's / protocols of the component Controllers.
    """

    def __init__(
        self,
        model: Model,
        view: View,
        components: ComponentControllers,
    ) -> None:
        self.model = model
        self.view = view
        # a dictionary mapping the name of the available component (see Enum above) to the corresponding controller
        self.components = components

        # Keep track of a first-in-first-out (FIFO) queue of opening/saving actions to be performed
        self._pending_file_dialog_requests: list[tuple[FileType, FileAction]] = []

        # Connect (listen) to incoming signals from the MainView:
        self.view.connect_next_trace(self.handle_move_to_next_trace)
        self.view.connect_prev_trace(self.handle_move_to_prev_trace)
        self.view.connect_jump_to_trace(self.handle_jump_to_trace)
        self.view.connect_menu_file_open(self.handle_menu_file_open)
        self.view.connect_menu_file_save(self.handle_menu_file_save)
        self.view.connect_menu_file_save_as(self.handle_menu_file_save_as)
        self.view.connect_menu_file_import_labels(self.handle_menu_load_labels)
        self.view.connect_menu_file_import_sections(self.handle_menu_load_sections)
        self.view.connect_file_name_selected(self.handle_file_name_selected)
        self.view.connect_go_to_help_docs(self.handle_go_to_help_docs)

        # Connect (listen) to signals from the components
        self.connect_components()

    def connect_components(self) -> None:
        """
        Establish connections to the signals emitted by components.
        """
        self.components["label_panel"].connect_open_item_list(
            self.handle_open_item_list_from_label_panel
        )
        self.components["sections_panel"].connect_open_item_list(
            self.handle_open_item_list_from_sections_panel
        )

    # main app logic
    def close_app(self) -> None:
        """Checks for untracked changes"""

    def handle_error(self, severity: EventSeverity, message: str) -> None:
        """When a method fails expectedly: do not crash the code, but show a message box"""
        self.view.open_message_box(severity, message)

    def handle_move_to_next_trace(self) -> None:
        """
        Updates the data of the current trace before moving to the next.
        NOTE: This means the data also gets updated if you are already at the final one.
        TODO: set untracked changes
        ? Implement a way of checking if you actually changed something / have untracked changes?
        """
        # If the user clicks before any data is loaded, simply ignore the action
        if not self._data_is_loaded:
            return

        # update the current trace's data before changing focus
        self._update_current_trace()

        # Change focus to the new trace
        self.model.move_to_next_trace()
        self.view.display_trace_id(self.model.current_trace_id)

        # reset the components that work with one trace at the time
        self._reset_components()

        # update the progress bar
        self.view.update_progressbar(self.model.progress_percentage)

    def handle_move_to_prev_trace(self) -> None:
        """
        Updates the data of the current trace before moving to the previous.
        NOTE: This means the data also gets updated if you are already at the first one.
        TODO: set untracked changes
        ? Implement a way of checking if you actually changed something / have untracked changes?
        """

        # If the user clicks before any data is loaded, simply ignore the action
        if not self._data_is_loaded:
            return
        # update the current trace's data before changing focus
        self._update_current_trace()

        # Change focus to the new trace
        self.model.move_to_previous_trace()
        self.view.display_trace_id(self.model.current_trace_id)

        # reset the components that work with one trace at the time
        self._reset_components()

        # update the progress bar
        self.view.update_progressbar(self.model.progress_percentage)

    @with_error_handling(severity=EventSeverity.INFO)
    def handle_jump_to_trace(self, trace_id: str) -> None:
        """
        Updates the data of the current trace before changing focus
        NOTE: This means the data also gets updated if you are already at the final one.
        TODO: set untracked changes
        ? Implement a way of checking if you actually changed something / have untracked changes?
        """
        # If the user enters a number before any data is loaded, simply ignore the action
        if not self._data_is_loaded:
            return

        # update the current trace's data before changing focus
        self._update_current_trace()

        # Change focus to the new trace
        target_index = self.model.find_index_from_id(trace_id)
        self.model.jump_to_index(target_index)
        self.view.display_trace_id(self.model.current_trace_id)

        # reset the components that work with one trace at the time
        self._reset_components()

        # update the progress bar
        self.view.update_progressbar(self.model.progress_percentage)

    @with_error_handling(severity=EventSeverity.ERROR)
    def handle_file_name_selected(self, file_name: Path):
        """
        Triggered when a file path is selected in the file dialog.
        ---
        The View tells the Controller: "here is the selected file path"

        ---
        Origin:
        - View signal: file_name_selected

        Handler responsibility:
        - Dequeue the corresponding file request (FIFO).
        - Update the model with the selected file path.
        - triggers the actions on the model side to do the actual opening/closing of the data + logic on the view side to reflect updates
        - On successful loading of the data: Tells the components to update their model/view to reflect the updated state of the main model.
        - moves on to the next request (the _process_next_request() will automatically break out of this pattern when there are no more requests pending)

        ---
        Notes:
        - If the user cancels the dialog, this signal will not fire (no-op).
        - This method completes the file-open or file-save operation
          that was initiated in `handle_menu_file_open` or `handle_menu_file_save`.
        """

        # current request is done: FIFO, so remove the top request
        file_type, file_action = self._pending_file_dialog_requests.pop(0)

        # update the model's file paths
        if file_type == FileType.RAW_DATA:
            self.model.set_file_path_to_experiment_data(file_name)
        elif file_type == FileType.LABELS:
            self.model.set_file_path_to_labels(file_name)
        elif file_type == FileType.SECTION_LABELS:
            self.model.set_file_path_to_section_labels(file_name)

        # process the selected file
        if file_action == FileAction.OPEN:
            self._open_file(file_type)
            self._reset_components()
            success_message = f"\N{CHECK MARK} Successfully loaded {file_type.name.lower()} from: {file_name}"
            self.view.open_message_box(EventSeverity.INFO, success_message)

        elif file_action == FileAction.SAVE:
            self._save_file(file_type)
            success_message = f"\N{CHECK MARK} Successfully saved {file_type.name.lower()} into: {file_name}"
            self.view.open_message_box(EventSeverity.INFO, success_message)

        # move on to the next file dialog that must be opened
        self._process_next_request()

    def handle_menu_file_open(self) -> None:
        """
        Triggered when you activate the "Open..." action from the menu bar.
        ----

        Origin:
        - View signal: menu_file_open

        Handler responsibility:
        - Post a request to open the file dialog for raw data.
        - Trigger processing of the next pending request (opens the dialog).

        ---
        Notes:
        - This method only initiates the open action.
        - The controller awaits the *file selected* signal from the view.
        - Further processing is handled in `handle_file_name_selected_from_dialogue`.
        """
        # the Open... action implies loading the raw experiment data
        self._post_open_request(FileType.RAW_DATA)
        self._process_next_request()

    def handle_menu_file_save(self) -> None:
        """
        Triggered when you activate the "Save..." action from the menu bar.
        ----
        Origin:
        - View signal: menu_file_save_as

        ---
        If you previously set the output file paths (for instance, by doing 'Save as...' previously),
        it is assumed the user wants to write into the same set of files.

        ---
        If any of the file paths are (yet) unknown (for instance, you do 'Save...' without having done 'Save as...')
        default to performing the logic of the 'Save as...' action
        """
        if self._out_file_paths_are_set():
            # First update the data to take the latest changes into account
            self._update_current_trace()
            self._save_file(FileType.LABELS)
            self._save_file(FileType.SECTION_LABELS)
        else:
            self.handle_menu_file_save_as()

    def handle_menu_file_save_as(self) -> None:
        """
        Triggered when you activate the "Save as..." action from the menu bar
        ---
        It is assumed you want to manually select the output file paths

        ---
        Origin:
        - View signal: menu_file_save_as

        ---
        Handler responsibility:
        - Post requests to open the file dialog for selecting the destinations for both the labels and section labels.
        - Trigger processing of the next pending request (opens the first dialog).

        ---
        Notes:
        - This method only initiates the save as action.
        - The controller awaits the *file selected* signal from the view.
        - Further processing is handled in `handle_file_name_selected_from_dialogue`.
        """
        # First update the data to take the latest changes into account
        self._update_current_trace()

        self._post_save_request(FileType.LABELS)
        self._post_save_request(FileType.SECTION_LABELS)
        self._process_next_request()

    def handle_menu_load_labels(self) -> None:
        """
        Controller does similar to "Open...", but now for the file containing the labels
        """
        self._post_open_request(FileType.LABELS)
        self._process_next_request()

    def handle_menu_load_sections(self) -> None:
        """
        Controller does similar to "Open...", but now for the file containing the section labels
        """
        self._post_open_request(FileType.SECTION_LABELS)
        self._process_next_request()

    def handle_changed_ref_bead(self) -> None:
        # TODO: Implement this later
        self.view.open_message_box(EventSeverity.INFO, "Not implemented yet.")

    def handle_toggle_subtract_ref_bead(self) -> None:
        # TODO: Implement this later
        self.view.open_message_box(EventSeverity.INFO, "Not implemented yet.")

    def handle_open_item_list_from_label_panel(self) -> None:
        """Button clicked in the `LabelsPanel` : instantiate `ItemList` with appropriate list of available labels"""

        # ensure to only open one copy of the window at the time to avoid confusion(even if you press the button multiple times)
        if getattr(self, "popup_window_from_labels", None):
            return

        available_labels = self.components["label_panel"].get_available_labels()
        # create an instance variable, to have the window actually persist after you exit this function.
        self.popup_window_from_labels = self.components["item_list"](available_labels)
        self.popup_window_from_labels.connect_window_closed_signal(
            self.handle_close_item_list_from_label_panel
        )
        self.popup_window_from_labels.show()

    def handle_close_item_list_from_label_panel(self, items: list[str]) -> None:
        """Update the list of available labels"""
        self.components["label_panel"].update_available_labels(items)
        self.popup_window_from_labels = None

    def handle_open_item_list_from_sections_panel(self) -> None:
        """Button clicked in the `SectionsPanel` : instantiate `ItemList` with appropriate list of available labels"""
        # ensure to only open one copy of the window at the time to avoid confusion(even if you press the button multiple times)
        if getattr(self, "popup_window_from_sections", None):
            return
        available_labels = self.components["sections_panel"].get_available_labels()
        # create an instance variable, to have the window actually persist after you exit this function.
        self.popup_window_from_sections = self.components["item_list"](available_labels)
        self.popup_window_from_sections.connect_window_closed_signal(
            self.handle_close_item_list_from_sections_panel
        )
        self.popup_window_from_sections.show()

    def handle_close_item_list_from_sections_panel(self, items: list[str]) -> None:
        """Update the list of available section labels"""
        self.components["sections_panel"].update_available_labels(items)
        self.popup_window_from_sections = None

    def handle_line_added_in_plot(self, location: float) -> None:
        """Makes the InterActivePlot affect the SectionsPanel"""

    def handle_removed_line_from_plot(self) -> None:
        """Makes the InterActivePlot affect the SectionsPanel"""

    def handle_go_to_help_docs(self) -> None:
        # TODO: Implement this later when MkDocs website is running
        self.view.open_message_box(
            EventSeverity.INFO, "Coming soon... (not implemented yet)"
        )

    # file-handling logic
    def _process_next_request(self) -> None:
        """Checks the next job in the queue and triggers the View to open the corresponding FileDialog"""

        # if there are no more requests, you are done
        if not self._pending_file_dialog_requests:
            return

        # Otherwise, process the next in line. FIFO: So check for the earliest posted job
        file_type, file_action = self._pending_file_dialog_requests[0]
        if file_action == FileAction.OPEN:
            self.view.ask_open_file(
                window_title=f"File to read {file_type.name.lower().replace('_', ' ')} from"
            )
        elif file_action == FileAction.SAVE:
            self.view.ask_save_file(
                window_title=f"File to save {file_type.name.lower().replace('_', ' ')} into"
            )

    def _post_open_request(self, file_type: FileType) -> None:
        """Adds a job to open a file to the FIFO queue"""
        self._pending_file_dialog_requests.append((file_type, FileAction.OPEN))

    def _post_save_request(self, file_type: FileType) -> None:
        """Adds a job to save a file to the FIFO queue"""
        self._pending_file_dialog_requests.append((file_type, FileAction.SAVE))

    def _open_file(self, file_type: FileType) -> None:
        """Trigger the correct actions on the Model-side depending on the type of data we are trying to open"""

        if file_type == FileType.RAW_DATA:
            self.model.load_experiment_data()
        elif file_type == FileType.LABELS:
            self.model.load_labels()
        elif file_type == FileType.SECTION_LABELS:
            self.model.load_section_labels()

    def _save_file(self, file_type: FileType) -> None:
        """Trigger the correct actions on the Model-side depending on the type of data we are trying to save"""
        if file_type == FileType.LABELS:
            self.model.write_labels()
        elif file_type == FileType.SECTION_LABELS:
            self.model.write_section_labels()

    def _out_file_paths_are_set(self) -> bool:
        """
        Checks that all file paths are already set for saving. If so, no need to re-open file-dialog when 'Save...' (not 'Save as...')

        ---
        NOTE: Only checks for the files you are going to be saving.
        """
        if self.model.path_to_labels == Path(""):
            return False
        if self.model.path_to_section_labels == Path(""):
            return False
        return True

    # Logic that requires accessing the component controllers
    def _update_current_trace(self) -> None:
        """
        Update the data of the MainModel to reflect the latests set of sections/labels chosen.
        ---
        Will be triggered whenever the app changes focus to a new trace

        ---
        NOTE: By construction, you will always have updated any other trace
        """
        # Update the current trace's labels (from the LabelPanel)
        new_labels = self.components["label_panel"].get_assigned_labels()
        self.model.update_trace_labels(new_labels)

        # update the current trace's section labels (from the SectionsPanel)
        new_section_labels = self.components["sections_panel"].get_section_labels()
        self.model.update_trace_section_labels(new_section_labels)

    def _reset_components(self) -> None:
        """
        Resets the components by passing them the (relevant part) of the current trace's data
        ---
        Will be triggered whenever the app changes focus to a new trace.

        ----
        NOTE: The list of available labels is assumed to be shared amongst traces (for you entire experiment).Therefore, it does not have to get updated here.
        """
        # plot the new trace
        horizontal_line_time_points = [
            self.model.current_trace.t[frame]
            for frame in self.components["sections_panel"].get_section_boundaries()
        ]
        self.components["interactive_plot"].reset_for_new_trace(
            self.model.current_trace, horizontal_line_time_points
        )
        # reset the assigned labels
        self.components["label_panel"].reset_for_new_trace(
            self.model.current_trace.labels
        )
        # reset the assigned section labels
        self.components["sections_panel"].reset_for_new_trace(
            self.model.current_trace.section_labels
        )

    @property
    def _data_is_loaded(self) -> bool:
        return (
            self.model.has_traces
            and self.components["interactive_plot"].data_is_loaded()
        )
