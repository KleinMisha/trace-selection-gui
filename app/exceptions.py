"""
Custom exceptions we want to catch (covers 'expected errors due to user interactions with the application').
"""

import functools
from typing import Any, Callable, Protocol

from app.state_variables import EventSeverity


class ApplicationError(Exception):
    """
    Base exception
    ---
    Make all forms of expected exceptions a subclass of this.
    (an exception that is not a subclass of ApplicationError --> then we want the programme to crash as something unexpected is happening)
    """

    pass


class FileHandlingError(ApplicationError):
    """Raised when opening/loading a file has gone wrong. Catches 'expected' OSErrors"""

    pass


class UnsupportedFileTypeError(ApplicationError):
    """Raised when trying to open/close a file of the wrong kind"""

    pass


class InvalidInputError(ApplicationError):
    """Raised when the user enters an invalid value"""

    pass


class ErrorController(Protocol):
    """generic class that can handle errors. Will typically be the MainController"""

    def handle_error(self, severity: EventSeverity, message: str) -> None: ...


def with_error_handling(severity: EventSeverity) -> Callable[..., Any]:
    """
    Collects error handling at one place in the code.
    Using a decorator as this seemed to be the easiest/cleanest way.

    see -- <YOUTUBE LINK> --- for a tutorial on how this works
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(self: ErrorController, *args, **kwargs) -> Any:
            try:
                # attempt to apply the original function call
                result = func(self, *args, **kwargs)
                return result
            except ApplicationError as e:
                # on failure --> the ErrorHandler choses what to do. Typically show a message box.
                self.handle_error(severity, message=str(e))
                return None

        return wrapper

    return decorator


# Intentionally NOT made an ApplicationError
class MissingExperimentError(Exception):
    """
    To indicate you cannot perform certain operations before having loaded the experiment
    ---
    !NOTE: if this occurs, it is actually a programming error. The assertions in the code below are there to:
    ! 1. make the type-checker happy
    ! 2. specify a contract to all developers: please make sure the MainController guards against calling this method when there is no data.
    ! In short, just ensure you never call these methods before it would be possible.
    """

    def __init__(self, function_name: str) -> None:
        super().__init__(
            f"Called '{function_name}' before loading any data.\nAdd a guard clause at appropriate point in code (typically in the MainController)"
        )
