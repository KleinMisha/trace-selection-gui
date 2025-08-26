from enum import Enum, auto


class LightState(Enum):
    """Simple state to toggle the indicator 'light'"""

    ON = auto()
    OFF = auto()


class MessageBox(Enum):
    """The different kinds of msg-boxes the view should be opening"""

    INFO = auto()
    WARNING = auto()
    ERROR = auto()
