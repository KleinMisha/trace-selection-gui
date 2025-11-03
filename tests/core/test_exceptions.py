"""
Unit tests for app/exceptions.py
"""

from typing import Type, cast
from unittest.mock import Mock, create_autospec

import pytest

from app.core.exceptions import (
    ApplicationError,
    ErrorController,
    FileHandlingError,
    InvalidInputError,
    UnsupportedFileTypeError,
    with_error_handling,
)
from app.state_variables import EventSeverity

exception_types = [
    ApplicationError,
    FileHandlingError,
    UnsupportedFileTypeError,
    InvalidInputError,
]


@pytest.fixture()
def error_controller() -> ErrorController:
    """mock the ErrorController / Error Handling Controller"""
    return create_autospec(ErrorController, instance=True)


@pytest.mark.parametrize("exception", exception_types)
def test_handle_error_on_failure(
    error_controller: ErrorController, exception: Type[ApplicationError]
) -> None:
    """When you decorate a function that raises one of the predefined exceptions, the error should get handled"""

    @with_error_handling(EventSeverity.ERROR)
    def func_that_raises_error(self: ErrorController) -> None:
        raise exception("dummy function")

    func_that_raises_error(error_controller)
    cast(Mock, error_controller.handle_error).assert_called_once_with(
        EventSeverity.ERROR, message=f"{exception.__name__}: dummy function"
    )


def test_regular_func_call_on_success(error_controller: ErrorController) -> None:
    """decorator should not do anything if the function does not raise an exception.

    checks that some mock positional argument indeed gets passed onwards into the original function call
    """

    successful_function = Mock(return_value=None)
    decorated_function = with_error_handling(EventSeverity.ERROR)(successful_function)

    decorated_function(error_controller, 23)
    successful_function.assert_called_once_with(error_controller, 23)
    cast(Mock, error_controller.handle_error).assert_not_called()


def test_do_not_handle_unexpected_exceptions(error_controller: ErrorController) -> None:
    """make sure you only catch exceptions you might expect. Others should still actually raise an exception and let the application crash"""

    @with_error_handling(EventSeverity.ERROR)
    def func_raises_general_exception(self: ErrorController) -> None:
        raise Exception("dummy function")

    with pytest.raises(Exception, match="dummy function"):
        func_raises_general_exception(error_controller)

    cast(Mock, error_controller.handle_error).assert_not_called()
