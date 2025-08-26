from enum import Enum, auto


class LightState(Enum):
    """Simple state to toggle the indicator 'light'"""

    ON = auto()
    OFF = auto()
