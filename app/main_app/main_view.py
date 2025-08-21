import re
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from app.main_app.main_view_ui import Ui_MainWindow

# TODO: Move this into a configuration file
KEYBOARD_SHORTCUTS = {
    "file_open": ("Open...", "Ctrl + O"),
    "file_save": ("Save...", "Ctrl + S"),
    "file_save_as": ("Save as...", "Ctrl + Shift + S"),
}
COLOR_ON = "coral"
COLOR_OFF = "white"


class LightState(Enum):
    ON = auto()
    OFF = auto()


class MessageBox(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class MainView(QMainWindow, Ui_MainWindow):
    _next_trace_signal = pyqtSignal()
    _prev_trace_signal = pyqtSignal()
    _jump_to_trace_signal = pyqtSignal(str)
    _menu_file_open_signal = pyqtSignal()
    _menu_file_save_signal = pyqtSignal()
    _menu_file_save_as_signal = pyqtSignal()
    _go_to_help_docs_signal = pyqtSignal()  # TODO: Implemented later in Controller
    _ref_bead_adjusted_signal = pyqtSignal(str)  # TODO: Implement later
    _toggle_subtract_ref_bead_signal = pyqtSignal(bool)  # TODO: Implement later

    # Emitted only after the Controller calls the View to display a QFileDialog:
    _file_path_selected_signal = pyqtSignal(Path)

    def __init__(self) -> None:
        super().__init__()
        self.build_ui()

        # connect listening to user input:
        self.NextTraceButton.clicked.connect(self._send_next_trace_signal)
        self.previousTraceButton.clicked.connect(self._send_prev_trace_signal)
        self.TraceIDEntry.textChanged.connect(self._send_jump_to_trace_signal)
        self.actionOpen.triggered.connect(self._send_menu_file_open_signal)
        self.actionSave.triggered.connect(self._send_menu_file_save_signal)
        self.actionSaveAs.triggered.connect(self._send_menu_file_save_as_signal)
        self.REFBeadIDsEntry.textChanged.connect(self._send_ref_bead_adjusted_signal)
        self.refBeadRadioButton.toggled.connect(
            self._send_toggle_subtract_ref_bead_signal
        )
        self.helpDocsButton.clicked.connect(self._send_go_to_help_docs)

    def build_ui(self) -> None:
        """Only build the parts specific to the mainView. Placing the components will be done in the mainController"""
        self.setupUi(self)

        # setting operating-system agnostic keyboard shortcuts / appropriate label in the MenuBar
        self._assign_keyboard_shortcut(
            self.actionOpen,
            action_in_words=KEYBOARD_SHORTCUTS["file_open"][0],
            shortcut=KEYBOARD_SHORTCUTS["file_open"][0],
        )
        self._assign_keyboard_shortcut(
            self.actionSave,
            action_in_words=KEYBOARD_SHORTCUTS["file_save"][0],
            shortcut=KEYBOARD_SHORTCUTS["file_save"][1],
        )
        self._assign_keyboard_shortcut(
            self.actionSaveAs,
            action_in_words=KEYBOARD_SHORTCUTS["file_save_as"][0],
            shortcut=KEYBOARD_SHORTCUTS["file_save_as"][1],
        )

        # global title of the window
        self.setWindowTitle("Trace Selection")

    @staticmethod
    def _assign_keyboard_shortcut(action: QAction, shortcut: str, action_in_words: str):
        """
        Convert the keyboard shortcut into a OS-agnostic version using builtin Qt methods
        ?Define this as a regular function at the top of this file? I thought this is still best as it will never be called outside this class anyways
        """
        key_sequence = QKeySequence(shortcut)
        action.setShortcut(key_sequence)
        key_icons = key_sequence.toString(QKeySequence.SequenceFormat.NativeText)
        display_text = f"{action_in_words}\t{key_icons}"
        action.setText(display_text)

    # UI-logic
    def display_trace_id(self, name: str) -> None:
        self.TraceIDEntry.setText(name)

    def update_progressbar(self, value: float) -> None:
        """the Qt progressbar expects integer values. Round the input percentage."""
        self.progressBar.setValue(round(value))

    def toggle_indicator_saved_changes(self, state: LightState) -> None:
        """
        Adjust the part in the stylesheet that determines the background color of the label.
        NOTE: This 'light' is simply 'a text label without any text displayed'
        """
        if state == LightState.ON:
            color = COLOR_ON
        elif state == LightState.OFF:
            color = COLOR_OFF

        # find the background-color option in the string and replace it with desired color
        current_styling = self.UnsavedChangesIndicator.styleSheet()
        background_color = "background-color\s*:\s*[^;]+;"
        new_styling = re.sub(
            pattern=background_color,
            repl=f"background-color: {color};",
            string=current_styling,
        )
        self.UnsavedChangesIndicator.setStyleSheet(new_styling)

    def display_ref_beads_ids(self, names: list[str]) -> None:
        # TODO: Implement later
        raise NotImplementedError

    def ask_open_file(self, window_title: str) -> None:
        """
        Ask the user to select a file to open
        ---
        This dialog only allows for selecting an existing file (which is what you want when opening a file)

        ---
        NOTE: The MainController will deal with routing this single file selection into those of the raw data, labels file, etc.
        """
        selected_file_path, _ = QFileDialog.getOpenFileName(self, caption=window_title)
        if selected_file_path:
            self._send_file_path_selected(Path(selected_file_path))

    def ask_save_file(self, window_title: str) -> None:
        """
        Ask the user to select a file to save into
        ----
        This dialog allows the user to enter a new file name
        """
        selected_file_path, _ = QFileDialog.getSaveFileName(self, caption=window_title)
        if selected_file_path:
            self._send_file_path_selected(Path(selected_file_path))

    def open_message_box(self, msg_type: MessageBox, message: str) -> None:
        """
        Display a message box to the user
        ----
        Open the correct Qt-widget depending on the state of the Enum passed as it's argument (i.e. INFO vs WARNING vs ERROR)

        ---
        NOTE: I know this is handled using if/else, but it seems to be a save assumption that this will never grow with many more options anyways.
        """
        if msg_type == MessageBox.INFO:
            QMessageBox.information(self, title="Note", text=message)
        elif msg_type == MessageBox.WARNING:
            QMessageBox.warning(self, title="Warning", text=message)
        elif msg_type == MessageBox.ERROR:
            QMessageBox.critical(self, title="Error", text=message)

    # Connect callbacks of controller to emitted signals
    def connect_next_trace(self, callback: Callable[[], None]) -> None:
        self._next_trace_signal.connect(callback)

    def connect_prev_trace(self, callback: Callable[[], None]) -> None:
        self._prev_trace_signal.connect(callback)

    def connect_jump_to_trace(self, callback: Callable[[str], None]) -> None:
        self._jump_to_trace_signal.connect(callback)

    def connect_menu_file_open(self, callback: Callable[[], None]) -> None:
        self._menu_file_open_signal.connect(callback)

    def connect_menu_file_save(self, callback: Callable[[], None]) -> None:
        self._menu_file_save_signal.connect(callback)

    def connect_menu_file_save_as(self, callback: Callable[[], None]) -> None:
        self._menu_file_save_as_signal.connect(callback)

    def connect_file_name_selected(self, callback: Callable[[Path], None]) -> None:
        self._file_path_selected_signal.connect(callback)

    def connect_go_to_help_docs(self, callback: Callable[[], None]) -> None:
        self._go_to_help_docs_signal.connect(callback)

    # emit signals when triggered by user's input
    def _send_next_trace_signal(self) -> None:
        """when the 'next trace' button is pressed"""
        self._next_trace_signal.emit()

    def _send_prev_trace_signal(self) -> None:
        """when the 'previous trace' button is pressed"""
        self._prev_trace_signal.emit()

    def _send_jump_to_trace_signal(self) -> None:
        """when the trace id is adjusted"""
        user_entry = self.TraceIDEntry.text()
        self._jump_to_trace_signal.emit(user_entry)

    def _send_menu_file_open_signal(self) -> None:
        """when you trigger File -> Open..."""
        self._menu_file_open_signal.emit()

    def _send_menu_file_save_signal(self) -> None:
        """when you trigger File -> Save..."""
        self._menu_file_save_signal.emit()

    def _send_menu_file_save_as_signal(self) -> None:
        """when you trigger File -> Save as..."""
        self._menu_file_save_as_signal.emit()

    def _send_file_path_selected(self, selected_path: Path) -> None:
        """
        When you selected a file from the FileDialog.
        ? Move this into the `ask_open_file` and `ask_save_file` methods? Just one line of code, but I felt this was more consistent with how the other code reads
        """
        self._file_path_selected_signal.emit(selected_path)

    def _send_go_to_help_docs(self) -> None:
        """when the `help` button is pressed"""
        self._go_to_help_docs_signal.emit()

    def _send_ref_bead_adjusted_signal(self) -> None:
        """when you adjust the reference bead ID(s)"""
        user_entry = self.REFBeadIDsEntry.text()
        self._ref_bead_adjusted_signal.emit(user_entry)

    def _send_toggle_subtract_ref_bead_signal(self) -> None:
        """when you toggle the radiobutton to subtract the reference bead from all traces"""
        state = self.refBeadRadioButton.isChecked()
        self._toggle_subtract_ref_bead_signal.emit(state)
