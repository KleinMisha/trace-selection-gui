"""
Tests main controller's logic: Are signals correctly passed between controllers?
"""

from typing import Any, Callable, Mapping, Type, TypeVar, cast
from unittest.mock import Mock, create_autospec

import pytest

from app.item_list.item_list_controller import ItemListController
from app.item_list.item_list_model import ItemList as ItemListModel
from app.item_list.item_list_view import PyQtView as ItemListView
from app.main_app.main_controller import Component, ComponentController, MainController
from app.main_app.main_model import MainModel
from app.main_app.main_view import MainView

T = TypeVar("T", bound=ComponentController)
Components = Mapping[Component, ComponentController]


def create_mock_component_controller(
    model_class: object, view_class: object, controller_class: Type[T]
) -> T:
    """
    Uses unittest's handy-dandy builtin methods to automatically create a mock object based on the real object.
    Because the controller objects we should mock here contain objects as their attributes (model, view), we should here create "a deep copy equivalent of the mock"

    NOTE: unittest's create_autospec() will create an instance of the supplied class in protocol form. That is. it makes an actual mock for you. Each instance method will come with builtin methods that wrapped around it to assert
    it has been called, called just once, called with a specific set of arguments, etc.
    """

    mock_controller = create_autospec(controller_class, instance=True)

    # now assign mocks to the newly created mock instance above
    mock_controller.model = create_autospec(model_class, instance=True)
    mock_controller.view = create_autospec(view_class, instance=True)

    return mock_controller


def assert_called_once_with(method: Callable, *args: Any) -> None:
    """
    Due to limitations in Python's typing system, I just made this wrapper function to enable autocomplete/ let PyLance understand
    a) the method belongs to the original class
    b) now it is a mock, it should also have the .assert_called_once_with() method, and other things
    """
    return cast(Mock, method).assert_called_once_with(*args)


@pytest.fixture
def components() -> Components:
    """
    create the mock controllers for the components here
    """
    mock_components = {
        Component.ITEM_LIST: create_mock_component_controller(
            ItemListModel, ItemListView, ItemListController
        )
    }
    return mock_components


@pytest.fixture
def model() -> MainModel:
    """Using create_autospec() makes this process allot easier. Automatically takes care of the mock for MainModel having the appropriate attributes and methods"""
    return create_autospec(MainModel, instance=True)


@pytest.fixture
def view() -> MainView:
    return create_autospec(MainView, instance=True)


def test_close_app() -> None: ...
def test_menu_open_file(
    model: MainModel, view: MainView, components: Components
) -> None:
    """
    1. Tell MainView to open a file dialogue
    2. Set the path attribute of the MainModel
    3. Tells mainModel to load the file from the given path
    4. Tell view (both main and components) to reflect changes.
    """

    controller = MainController(model, view, components)
    controller.handle_menu_file_open()

    # TODO: REMOVE THE LINES BELOW. NOT CORRECT. JUST TESTING HOW TO CALL THE MOCKS IN A WAY THAT THE VSCode IDE UNDERSTANDS WHAT I AM TRYING TO ACHIEVE HERE
    item_cntrl: ItemListController = cast(
        ItemListController, controller.components[Component.ITEM_LIST]
    )

    # TODO: remove. This is just an example. Option 1: do the cast here
    Mock(item_cntrl.model.add_item).assert_called_once_with("new item")

    # todo: Option2: hide the cast operation in a wrapper function.
    assert_called_once_with(item_cntrl.model.add_item, "new item")


def test_menu_open_invalid_file(
    model: MainModel, view: MainView, components: Components
) -> None: ...
def test_menu_save_as() -> None: ...
def test_menu_save_as_invalid_file() -> None:
    """
    todo: check if actually needed given writing will not actually fail when you do not select the correct file extension
    """


def test_menu_save_before_path_known() -> None: ...
def test_menu_save_after_path_known() -> None: ...


def test_move_to_next_trace() -> None: ...
def test_move_to_previous_trace() -> None: ...
def test_jump_to_trace() -> None: ...
