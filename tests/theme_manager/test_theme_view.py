"""
Test listening to input and emitting signals accordingly.
(use the `qapp` fixture automatically provided by pytestqt (no import needed))
"""

from PyQt6.QtWidgets import QApplication

from app.theme_manager.theme_view import ThemeView


def test_toggle(qapp: QApplication) -> None:
    """Switch between dark and light modes"""
    received_signals = []

    def mock_toggle_handler(state: bool) -> None:
        if state:
            mode = "dark"
        else:
            mode = "light"
        received_signals.append(mode)

    view = ThemeView()
    view.connect_dark_mode(mock_toggle_handler)

    # turn on dark mode
    view.themeToggle.toggle()
    assert received_signals == ["dark"]

    # turn on light mode (turn off dark mode)
    view.themeToggle.toggle()
    assert received_signals == ["dark", "light"]

    # for good measure, turn on dark mode once more
    view.themeToggle.toggle()
    assert received_signals == ["dark", "light", "dark"]
