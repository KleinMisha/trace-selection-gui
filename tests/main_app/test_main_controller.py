"""
Tests main controller's logic: Are signals correctly passed between controllers?
"""

from enum import Enum
from pathlib import Path
from typing import Any, Callable, Type, cast
from unittest.mock import Mock, PropertyMock, call, create_autospec, patch

import pytest

from app.item_list.item_list_factory import create_item_list
from app.main_app.component_controller_protocols import (
    InteractivePlotController,
    ItemListController,
    LabelPanelController,
    SectionsPanelController,
)
from app.main_app.main_controller import (
    ComponentControllers,
    FileAction,
    FileType,
    MainController,
    UnknownFileAction,
    UnknownFileType,
)
from app.main_app.main_model import MainModel
from app.main_app.main_view import MainView


@pytest.fixture
def model() -> MainModel:
    """Mock the MainModel: type-hinting it here as MainModel, so that PyLance understands it has all the attributes and methods a MainView should have"""
    return create_autospec(MainModel, instance=True)


@pytest.fixture
def view() -> MainView:
    """Mock the MainView: type-hinting it here as MainView, so that PyLance understands it has all the attributes and methods a MainView should have"""
    return create_autospec(MainView, instance=True)


@pytest.fixture
def components(monkeypatch: pytest.MonkeyPatch) -> ComponentControllers:
    """Mock the typed dictionary of component controllers (or factories). Intentionally type-hinting it here as ComponentControllers to make PyLance understand what attributes entries should have"""
    mock_plot_ctrl = create_autospec(InteractivePlotController, instance=True)
    mock_label_ctrl = create_autospec(LabelPanelController, instance=True)
    mock_sections_ctrl = create_autospec(SectionsPanelController, instance=True)

    # mock the item list factory
    def mock_factory(item_list: list[str]) -> ItemListController:
        return mock_item_list_ctrl

    mock_item_list_ctrl = create_autospec(ItemListController, instance=True)

    # Use pytest.MonkeyPatch to patch the actual version of the factory the MainController will see
    monkeypatch.setattr(
        "app.item_list.item_list_factory.create_item_list", mock_factory
    )

    return {
        "interactive_plot": mock_plot_ctrl,
        "label_panel": mock_label_ctrl,
        "sections_panel": mock_sections_ctrl,
        "item_list": mock_factory,
    }


@pytest.fixture
def main_controller(
    model: MainModel, view: MainView, components: ComponentControllers
) -> MainController:
    """Moved the creation of the MainController into this fixture to avoid passing an entire grocery list of arguments into all the test functions"""
    return MainController(model, view, components=components)


def test_close_app() -> None: ...


@pytest.mark.parametrize(
    "file_type, expected_window_title",
    [
        (FileType.LABELS, "File to read labels from"),
        (FileType.SECTION_LABELS, "File to read section labels from"),
        (FileType.RAW_DATA, "File to read raw data from"),
    ],
)
def test_process_open_file_request(
    main_controller: MainController, file_type: FileType, expected_window_title: str
) -> None:
    """post a request to open a file, then check the correct file dialog is opened"""

    main_controller._post_open_request(file_type)
    main_controller._process_next_request()
    cast(Mock, main_controller.view.ask_open_file).assert_called_once_with(
        window_title=expected_window_title
    )


@pytest.mark.parametrize(
    "file_type, expected_window_title",
    [
        (FileType.LABELS, "File to save labels into"),
        (FileType.SECTION_LABELS, "File to save section labels into"),
    ],
)
def test_process_save_file_request(
    main_controller: MainController, file_type: FileType, expected_window_title: str
) -> None:
    """post a request to save a file, then check the correct file dialog is opened"""

    main_controller._post_save_request(file_type)
    main_controller._process_next_request()
    cast(Mock, main_controller.view.ask_save_file).assert_called_once_with(
        window_title=expected_window_title
    )


def test_process_unknown_action(main_controller: MainController) -> None:
    """Should raise an exception if we attempt to process a request with some unknown action

    NOTE: As long as you won't define more than 99 file actions this test works ;-).
    """

    class FakeState(Enum):
        UNKNOWN = 99

    main_controller._pending_file_dialog_requests.append(
        (FileType.LABELS, cast(FileAction, FakeState.UNKNOWN))
    )
    with pytest.raises(UnknownFileAction):
        main_controller._process_next_request()


def test_process_without_pending_requests(main_controller: MainController) -> None:
    """Should break out of the function immediately, as there is no new request to process"""
    main_controller._process_next_request()
    cast(Mock, main_controller.view.ask_save_file).assert_not_called()
    cast(Mock, main_controller.view.ask_open_file).assert_not_called()


@pytest.mark.parametrize(
    "file_type, method_name",
    [
        (FileType.RAW_DATA, "load_experiment_data"),
        (FileType.LABELS, "load_labels"),
        (FileType.SECTION_LABELS, "load_section_labels"),
    ],
)
def test_open_file(
    main_controller: MainController, file_type: FileType, method_name: str
) -> None:
    """happy case: test the correct method of loading data is called"""
    with patch.object(
        target=main_controller.model, attribute=method_name
    ) as mock_loader:
        main_controller._open_file(file_type)
        mock_loader.assert_called_once()


def test_open_unknown_file_type(main_controller: MainController) -> None:
    """edge case: Attempt to open a file type for which no load method is defined"""

    class FakeState(Enum):
        UNKNOWN = 99

    with pytest.raises(UnknownFileType):
        main_controller._open_file(cast(FileType, FakeState.UNKNOWN))


@pytest.mark.parametrize(
    "file_type, method_name",
    [
        (FileType.LABELS, "write_labels"),
        (FileType.SECTION_LABELS, "write_section_labels"),
    ],
)
def test_save_file(
    main_controller: MainController, file_type: FileType, method_name: str
) -> None:
    """happy case: test the correct method of writing data is called"""
    with patch.object(
        target=main_controller.model, attribute=method_name
    ) as mock_loader:
        main_controller._save_file(file_type)
        mock_loader.assert_called_once()


def test_save_unknown_file_type(main_controller: MainController) -> None:
    """edge case: Attempt to save a file type for which no writer method is defined"""

    class FakeState(Enum):
        UNKNOWN = 99

    with pytest.raises(UnknownFileType):
        main_controller._save_file(cast(FileType, FakeState.UNKNOWN))


def test_menu_open_file(main_controller: MainController) -> None:
    """tests if handling this incoming signal from the View is done correctly

    NOTE: See how we here no longer have to test what is called inside _process_next_request() (and the other methods). The other tests take care of that already
    """
    with (
        patch.object(main_controller, attribute="_post_open_request") as mock_one,
        patch.object(main_controller, attribute="_process_next_request") as mock_two,
        patch.object(main_controller, "_reset_components") as mock_three,
    ):
        main_controller.handle_menu_file_open()
        mock_one.assert_called_once_with(FileType.RAW_DATA)
        mock_two.assert_called_once()
        mock_three.assert_called_once()


def test_menu_save_as(main_controller: MainController) -> None:
    """
    tests if handling this incoming signal from the View is done correctly

    #TODO: adjust when tracking unsaved changes to the data if appropriate
    """
    with (
        patch.object(main_controller, attribute="_update_current_trace") as mock_one,
        patch.object(main_controller, attribute="_post_save_request") as mock_two,
        patch.object(main_controller, "_process_next_request") as mock_three,
    ):
        main_controller.handle_menu_file_save_as()
        mock_one.assert_called_once()
        mock_two.assert_has_calls(
            [call(FileType.LABELS), call(FileType.SECTION_LABELS)]
        )
        assert mock_two.call_count == 2
        mock_three.assert_called_once()


def test_menu_save_before_path_known(main_controller: MainController) -> None:
    """In this case you should trigger a call to the handler for 'Save as...'"""

    with (
        patch.object(
            main_controller, attribute="_out_file_paths_are_set", return_value=False
        ) as _,
        patch.object(
            main_controller, attribute="handle_menu_file_save_as"
        ) as mock_save_as,
    ):
        main_controller.handle_menu_file_save()
        mock_save_as.assert_called_once()


def test_menu_save_after_path_known(main_controller: MainController) -> None:
    """In this case you can immediately proceed with saving the data"""

    with (
        patch.object(
            main_controller, attribute="_out_file_paths_are_set", return_value=True
        ) as _,
        patch.object(main_controller, attribute="_update_current_trace") as mock_one,
        patch.object(main_controller, attribute="_save_file") as mock_two,
    ):
        main_controller.handle_menu_file_save()
        mock_one.assert_called_once()
        mock_two.assert_has_calls(
            [call(FileType.LABELS), call(FileType.SECTION_LABELS)]
        )
        assert mock_two.call_count == 2


def test_menu_import_labels(main_controller: MainController) -> None:
    """tests if handling this incoming signal from the View is done correctly"""
    with (
        patch.object(main_controller, attribute="_post_open_request") as mock_one,
        patch.object(main_controller, attribute="_process_next_request") as mock_two,
        patch.object(main_controller, "_reset_components") as mock_three,
    ):
        main_controller.handle_menu_load_labels()
        mock_one.assert_called_once_with(FileType.LABELS)
        mock_two.assert_called_once()
        mock_three.assert_called_once()


def test_menu_import_section_labels(main_controller: MainController) -> None:
    """tests if handling this incoming signal from the View is done correctly"""
    with (
        patch.object(main_controller, attribute="_post_open_request") as mock_one,
        patch.object(main_controller, attribute="_process_next_request") as mock_two,
        patch.object(main_controller, "_reset_components") as mock_three,
    ):
        main_controller.handle_menu_load_sections()
        mock_one.assert_called_once_with(FileType.SECTION_LABELS)
        mock_two.assert_called_once()
        mock_three.assert_called_once()


def test_not_yet_set_file_paths(main_controller: MainController) -> None:
    """Tests the check is not passed if any of these paths are not set yet"""

    # do not set anything (defaults are empty paths)
    cast(Any, type(main_controller.model)).path_to_labels = PropertyMock(
        return_value=Path("")
    )
    cast(Any, type(main_controller.model)).path_to_section_labels = PropertyMock(
        return_value=Path("")
    )
    assert not main_controller._out_file_paths_are_set()

    # set only one of the paths
    cast(Any, type(main_controller.model)).path_to_labels = PropertyMock(
        return_value=Path("mock/mock/mock")
    )
    cast(Any, type(main_controller.model)).path_to_section_labels = PropertyMock(
        return_value=Path("")
    )
    assert not main_controller._out_file_paths_are_set()

    # double-check: only set the other path
    cast(Any, type(main_controller.model)).path_to_labels = PropertyMock(
        return_value=Path("")
    )
    cast(Any, type(main_controller.model)).path_to_section_labels = PropertyMock(
        return_value=Path("mock/mock/mock")
    )
    assert not main_controller._out_file_paths_are_set()


def test_find_previously_set_file_paths(main_controller: MainController) -> None:
    """Test you indeed pass the check when both file paths are set"""
    cast(Any, type(main_controller.model)).path_to_labels = PropertyMock(
        return_value=Path("mock/mock/mock/mock/mock")
    )
    cast(Any, type(main_controller.model)).path_to_section_labels = PropertyMock(
        return_value=Path("mock/mock/mock")
    )
    assert main_controller._out_file_paths_are_set()


@pytest.mark.parametrize(
    "file_type, method_name",
    [
        (FileType.RAW_DATA, "set_file_path_to_experiment_data"),
        (FileType.LABELS, "set_file_path_to_labels"),
        (FileType.SECTION_LABELS, "set_file_path_to_section_labels"),
    ],
)
def test_handle_filename_selected(
    main_controller: MainController, file_type: FileType, method_name: str
) -> None:
    """Check the first split that is done when a new filename is send from the View to the Controller"""
    main_controller._post_open_request(file_type)
    assert len(main_controller._pending_file_dialog_requests) == 1
    mock_path = Path("mock/mock/mock")

    with (
        patch.object(
            target=main_controller.model, attribute=method_name
        ) as mock_setter,
        patch.object(
            main_controller, attribute="_process_next_request"
        ) as mock_processor,
        patch.object(main_controller, attribute="_open_file") as mock_open,
    ):
        main_controller.handle_file_name_selected(mock_path)
        mock_setter.assert_called_once_with(mock_path)
        mock_open.assert_called_once_with(file_type)
        mock_processor.assert_called_once()

    # now check that the request has been popped
    assert len(main_controller._pending_file_dialog_requests) == 0


def test_handle_filename_unknown_file_type(main_controller: MainController) -> None:
    """check it raises the desired exception"""

    class FakeState(Enum):
        UNKNOWN = 99

    main_controller._post_open_request(cast(FileType, FakeState.UNKNOWN))
    with pytest.raises(UnknownFileType):
        main_controller.handle_file_name_selected(Path(""))


@pytest.mark.parametrize(
    "file_action, method_name",
    [(FileAction.OPEN, "_open_file"), (FileAction.SAVE, "_save_file")],
)
def test_handle_filename_known_actions(
    main_controller: MainController, file_action: FileAction, method_name: str
) -> None:
    """Check the second split works as desired"""
    if file_action == FileAction.OPEN:
        main_controller._post_open_request(FileType.LABELS)
    elif file_action == FileAction.SAVE:
        main_controller._post_save_request(FileType.LABELS)

    with patch.object(main_controller, attribute=method_name) as mock_method:
        main_controller.handle_file_name_selected(Path(""))
        mock_method.assert_called_once_with(FileType.LABELS)


def test_handle_filename_unknown_action(main_controller: MainController) -> None:
    """check it raises the desired exception"""

    class FakeState(Enum):
        UNKNOWN = 99

    main_controller._pending_file_dialog_requests.append(
        (FileType.LABELS, cast(FileAction, FakeState.UNKNOWN))
    )
    with pytest.raises(UnknownFileAction):
        main_controller.handle_file_name_selected(Path(""))


def test_move_to_next_trace() -> None: ...
def test_move_to_previous_trace() -> None: ...
def test_jump_to_trace() -> None: ...
