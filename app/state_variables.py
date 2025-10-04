"""
Enumerated constants used in / imported by several files in the application.
"""

from enum import Enum, auto


class LightState(Enum):
    """state to toggle the indicator 'light'"""

    ON = auto()
    OFF = auto()


class EventSeverity(Enum):
    """The kinds of feedback you'd want to give to the user, depends on the severity of the event"""

    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class Theme(Enum):
    """Appearance of the app"""

    LIGHT = "light"
    DARK = "dark"
