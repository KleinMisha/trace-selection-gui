"""
Test listening to input and emitting signals accordingly.
NOTE: Simulates user clicks with pyQt specific functionalities. So that part is not framework agnostic.
"""

from PyQt6.QtCore import Qt
from pytestqt.qtbot import QtBot

from app.item_list.item_list_view import PyQtView


def test_callback_add_button_click(qtbot: QtBot) -> None:
    """Change the input field value, click the button, and check if the callback indeed gets the value of the input field (as the function inside the View tells it to)"""

    view = PyQtView()
    received_signal = []

    def mock_signal_handler(signal: str) -> None:
        """mimic the controller-side function that has to get the signal emitted by the view"""
        received_signal.append(signal)

    view.connect_add_item(mock_signal_handler)
    qtbot.addWidget(view)
    view.input_label.setText("entered text")
    view.add_button.click()
    assert received_signal[0] == "entered text"


def test_callback_remove_button_click(qtbot: QtBot) -> None:
    """Check that when you select the N-th item, this value would correctly be received at the controller side."""

    view = PyQtView()
    qtbot.addWidget(view)
    received_signal = []

    def mock_signal_handler(signal: str) -> None:
        """mimic the controller-side function that has to get the signal emitted by the view"""
        received_signal.append(f"Remove {signal}")

    view.connect_remove_item(mock_signal_handler)
    labels = ["first label", "second label", "third label"]
    view.list_box.addItems(labels)

    for index in range(len(labels)):
        view.list_box.setCurrentRow(index)
        view.remove_button.click()
        assert received_signal[index] == f"Remove {labels[index]}"


def test_closing_window() -> None:
    """Check you emit a signal when you close the window"""
    received_signals = []

    def mock_signal_handler() -> None:
        """mimic the controller-side function that has to get the signal emitted by the view"""
        received_signals.append("close")

    view = PyQtView()
    view.connect_close_window(mock_signal_handler)
    view.close()
    assert received_signals == ["close"]


def test_add_label_using_enter_key(qtbot: QtBot) -> None:
    """test that adding a new label after pressing the return key does the same as clicking the add button"""
    view = PyQtView()
    received_signal = []

    def mock_signal_handler(signal: str) -> None:
        """mimic the controller-side function that has to get the signal emitted by the view"""
        received_signal.append(signal)

    view.connect_add_item(mock_signal_handler)
    qtbot.addWidget(view)
    view.input_label.setText("entered text")
    qtbot.keyPress(view.input_label, Qt.Key.Key_Return)
    assert received_signal[0] == "entered text"
