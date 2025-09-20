"""
Tests main controller's logic: Are signals correctly passed between controllers?
"""

from enum import Enum
from pathlib import Path
from typing import Any, cast
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
    mock_item_list_factory = Mock(side_effect=mock_factory)
    monkeypatch.setattr(
        "app.item_list.item_list_factory.create_item_list", mock_factory
    )

    return {
        "interactive_plot": mock_plot_ctrl,
        "label_panel": mock_label_ctrl,
        "sections_panel": mock_sections_ctrl,
        "item_list": mock_item_list_factory,
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


def test_menu_open_file(main_controller: MainController) -> None:
    """tests if handling this incoming signal from the View is done correctly

    NOTE: See how we here no longer have to test what is called inside _process_next_request() (and the other methods). The other tests take care of that already
    """
    with (
        patch.object(main_controller, attribute="_post_open_request") as mock_one,
        patch.object(main_controller, attribute="_process_next_request") as mock_two,
    ):
        main_controller.handle_menu_file_open()
        mock_one.assert_called_once_with(FileType.RAW_DATA)
        mock_two.assert_called_once()


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
    ):
        main_controller.handle_menu_load_labels()
        mock_one.assert_called_once_with(FileType.LABELS)
        mock_two.assert_called_once()


def test_menu_import_section_labels(main_controller: MainController) -> None:
    """tests if handling this incoming signal from the View is done correctly"""
    with (
        patch.object(main_controller, attribute="_post_open_request") as mock_one,
        patch.object(main_controller, attribute="_process_next_request") as mock_two,
    ):
        main_controller.handle_menu_load_sections()
        mock_one.assert_called_once_with(FileType.SECTION_LABELS)
        mock_two.assert_called_once()


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
        patch.object(main_controller, attribute="_reset_components") as mock_reset,
    ):
        main_controller.handle_file_name_selected(mock_path)
        mock_setter.assert_called_once_with(mock_path)
        mock_open.assert_called_once_with(file_type)
        mock_reset.assert_called_once()
        mock_processor.assert_called_once()

    # now check that the request has been popped
    assert len(main_controller._pending_file_dialog_requests) == 0


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


def test_reset_components(
    main_controller: MainController, components: ComponentControllers
) -> None:
    """Test the correct sequence of calls are made to reset all components when changing focus"""
    mock_labels = ["mock", "mock", "mock"]
    mock_sections = {(1, 2): ["mock"]}

    class MockTrace:
        def __init__(
            self,
            t: list[float],
            z: list[float],
            labels: list[str],
            section_labels: dict[tuple[int, int], list[str]],
        ) -> None:
            self.t = t
            self.z = z
            self.labels = labels
            self.section_labels = section_labels

    mock_trace = MockTrace(
        t=[float(n) for n in range(100)],
        z=[float(n) for n in range(100)],
        labels=mock_labels,
        section_labels=mock_sections,
    )
    cast(Any, type(main_controller.model)).current_trace = PropertyMock(
        return_value=mock_trace
    )
    expected_boundaries = [6, 23, 34, 45]

    with (
        patch.object(
            components["sections_panel"],
            attribute="get_section_boundaries",
            return_value=expected_boundaries,
        ) as mock_one,
        patch.object(
            components["interactive_plot"], attribute="reset_for_new_trace"
        ) as mock_two,
        patch.object(
            components["label_panel"], attribute="reset_for_new_trace"
        ) as mock_three,
        patch.object(
            components["sections_panel"], attribute="reset_for_new_trace"
        ) as mock_four,
    ):
        main_controller._reset_components()
        mock_one.assert_called_once()
        mock_two.assert_called_once_with(
            mock_trace, [float(b) for b in expected_boundaries]
        )
        mock_three.assert_called_once_with(mock_labels)
        mock_four.assert_called_once_with(mock_sections)


def test_updating_model_data_current_trace(
    main_controller: MainController, components: ComponentControllers
) -> None:
    """Tests updating the model's data (the labels and section labels for the current trace) happens using the correct API calls"""
    mock_labels = ["mock", "mock", "mock"]
    mock_sections = {(1, 2): ["mock"]}
    with (
        patch.object(
            components["label_panel"],
            attribute="get_assigned_labels",
            return_value=mock_labels,
        ) as mock_one,
        patch.object(
            main_controller.model, attribute="update_trace_labels"
        ) as mock_two,
        patch.object(
            components["sections_panel"],
            attribute="get_section_labels",
            return_value=mock_sections,
        ) as mock_three,
        patch.object(
            main_controller.model, attribute="update_trace_section_labels"
        ) as mock_four,
    ):
        main_controller._update_current_trace()
        mock_one.assert_called_once()
        mock_two.assert_called_once_with(mock_labels)
        mock_three.assert_called_once()
        mock_four.assert_called_once_with(mock_sections)


def test_move_to_next_trace(main_controller: MainController) -> None:
    """test changing focus to next trace leads to correct calls"""
    expected_percentage = 50.0
    expected_trace_id = "mock"
    cast(Any, type(main_controller.model)).current_trace_id = PropertyMock(
        return_value=expected_trace_id
    )
    cast(Any, type(main_controller.model)).progress_percentage = PropertyMock(
        return_value=expected_percentage
    )
    with (
        patch.object(main_controller, attribute="_update_current_trace") as mock_one,
        patch.object(main_controller.model, attribute="move_to_next_trace") as mock_two,
        patch.object(main_controller.view, attribute="display_trace_id") as mock_three,
        patch.object(main_controller, attribute="_reset_components") as mock_four,
        patch.object(main_controller.view, attribute="update_progressbar") as mock_five,
    ):
        main_controller.handle_move_to_next_trace()
        mock_one.assert_called_once()
        mock_two.assert_called_once()
        mock_three.assert_called_once_with(expected_trace_id)
        mock_four.assert_called_once()
        mock_five.assert_called_once_with(expected_percentage)


def test_move_to_previous_trace(main_controller: MainController) -> None:
    """test changing focus to next trace leads to correct calls"""
    expected_percentage = 50.0
    expected_trace_id = "mock"
    cast(Any, type(main_controller.model)).current_trace_id = PropertyMock(
        return_value=expected_trace_id
    )
    cast(Any, type(main_controller.model)).progress_percentage = PropertyMock(
        return_value=expected_percentage
    )
    with (
        patch.object(main_controller, attribute="_update_current_trace") as mock_one,
        patch.object(
            main_controller.model, attribute="move_to_previous_trace"
        ) as mock_two,
        patch.object(main_controller.view, attribute="display_trace_id") as mock_three,
        patch.object(main_controller, attribute="_reset_components") as mock_four,
        patch.object(main_controller.view, attribute="update_progressbar") as mock_five,
    ):
        main_controller.handle_move_to_prev_trace()
        mock_one.assert_called_once()
        mock_two.assert_called_once()
        mock_three.assert_called_once_with(expected_trace_id)
        mock_four.assert_called_once()
        mock_five.assert_called_once_with(expected_percentage)


def test_jump_to_trace(main_controller: MainController) -> None:
    """test changing focus to next trace leads to correct calls"""
    expected_percentage = 50.0
    expected_trace_id = "mock"
    expected_trace_index = 23
    cast(Any, type(main_controller.model)).current_trace_id = PropertyMock(
        return_value=expected_trace_id
    )
    cast(Any, type(main_controller.model)).progress_percentage = PropertyMock(
        return_value=expected_percentage
    )
    with (
        patch.object(main_controller, attribute="_update_current_trace") as mock_one,
        patch.object(
            main_controller.model,
            attribute="find_index_from_id",
            return_value=expected_trace_index,
        ) as mock_two,
        patch.object(main_controller.model, attribute="jump_to_index") as mock_three,
        patch.object(main_controller.view, attribute="display_trace_id") as mock_four,
        patch.object(main_controller, attribute="_reset_components") as mock_five,
        patch.object(main_controller.view, attribute="update_progressbar") as mock_six,
    ):
        main_controller.handle_jump_to_trace(expected_trace_id)
        mock_one.assert_called_once()
        mock_two.assert_called_once_with(expected_trace_id)
        mock_three.assert_called_once_with(expected_trace_index)
        mock_four.assert_called_once_with(expected_trace_id)
        mock_five.assert_called_once()
        mock_six.assert_called_once_with(expected_percentage)


@pytest.mark.parametrize(
    "method_name",
    [
        "handle_move_to_next_trace",
        "handle_move_to_prev_trace",
        "handle_jump_to_trace",
    ],
)
def test_no_change_of_focus_without_data_loaded(
    main_controller: MainController, method_name: str
) -> None:
    """make sure you break out of these functions as soon as you fail the check that you do not have any data loaded"""
    # initialize the system without any loaded data
    cast(Any, type(main_controller))._data_is_loaded = PropertyMock(return_value=False)
    handler = main_controller.__getattribute__(method_name)
    # make sure to not call the first function that is part of the logic (common for all the methods in question)
    with patch.object(
        main_controller, attribute="_update_current_trace"
    ) as mock_updater:
        if method_name == "handle_jump_to_trace":
            result = handler("mock")
        else:
            result = handler()
        assert result is None
        mock_updater.assert_not_called()


def test_handle_open_item_list_from_labels_panel(
    main_controller: MainController,
) -> None:
    """test correctly displaying the popup window.
    NOTE: Because of all the mock components made in the fixture (see above), this process becomes easier.
    No need to mock again. Only patch the return of functions.
    """
    expected_labels = ["mock", "mock", "mock"]
    with patch.object(
        main_controller.components["label_panel"],
        attribute="get_available_labels",
        return_value=expected_labels,
    ) as _:
        # send the signal to open the window:
        main_controller.handle_open_item_list_from_label_panel()

        # check the controller creates a new window with the available labels set according to what the labels panel says it are:
        cast(
            Mock, main_controller.components["label_panel"].get_available_labels
        ).assert_called_once()
        cast(Mock, main_controller.components["item_list"]).assert_called_once_with(
            expected_labels
        )

        # To have the window persist after exiting the` handle_open_item_list_...()`, the main controller should store the window as an instance variable
        assert main_controller.popup_window_from_labels == main_controller.components[
            "item_list"
        ](expected_labels)
        mock_window = cast(ItemListController, main_controller.popup_window_from_labels)

        # Make sure to connect the logic for when you close the window
        cast(Mock, mock_window.connect_window_closed_signal).assert_called_once_with(
            main_controller.handle_close_item_list_from_label_panel
        )

        # Make sure to actually show the new window
        cast(Mock, mock_window.show).assert_called_once()


def test_only_one_popup_from_labels_panel_exists(
    main_controller: MainController,
) -> None:
    """Check that when pressing the button in the labels panel multiple times, that only a single window is shown"""
    expected_labels = ["mock", "mock", "mock"]
    with patch.object(
        main_controller.components["label_panel"],
        attribute="get_available_labels",
        return_value=expected_labels,
    ) as _:
        # send the signal to open the window a couple of times:
        main_controller.handle_open_item_list_from_label_panel()
        main_controller.handle_open_item_list_from_label_panel()
        main_controller.handle_open_item_list_from_label_panel()

        # check subsequent logic is only called once
        cast(Mock, main_controller.components["item_list"]).assert_called_once_with(
            expected_labels
        )
        mock_window = cast(ItemListController, main_controller.popup_window_from_labels)
        cast(Mock, mock_window.show).assert_called_once()


def test_close_item_list_from_labels_panel(main_controller: MainController) -> None:
    """check the control flow from opening the window -> closing it --> then check the available labels are updated correctly"""

    mock_items = ["mock", "mocker", "most mockest"]
    with patch.object(
        main_controller.components["label_panel"],
        attribute="update_available_labels",
    ) as mock_updater:
        main_controller.handle_close_item_list_from_label_panel(mock_items)
        mock_updater.assert_called_once_with(mock_items)
        assert main_controller.popup_window_from_labels is None


def test_handle_open_item_list_from_sections_panel(
    main_controller: MainController,
) -> None:
    """test correctly displaying the popup window.
    NOTE: Because of all the mock components made in the fixture (see above), this process becomes easier.
    No need to mock again. Only patch the return of functions.
    """
    expected_labels = ["mock", "mock", "mock"]
    with patch.object(
        main_controller.components["sections_panel"],
        attribute="get_available_labels",
        return_value=expected_labels,
    ) as _:
        # send the signal to open the window:
        main_controller.handle_open_item_list_from_sections_panel()

        # check the controller creates a new window with the available labels set according to what the labels panel says it are:
        cast(
            Mock, main_controller.components["sections_panel"].get_available_labels
        ).assert_called_once()
        cast(Mock, main_controller.components["item_list"]).assert_called_once_with(
            expected_labels
        )

        # To have the window persist after exiting the` handle_open_item_list_...()`, the main controller should store the window as an instance variable
        assert main_controller.popup_window_from_sections == main_controller.components[
            "item_list"
        ](expected_labels)
        mock_window = cast(
            ItemListController, main_controller.popup_window_from_sections
        )

        # Make sure to connect the logic for when you close the window
        cast(Mock, mock_window.connect_window_closed_signal).assert_called_once_with(
            main_controller.handle_close_item_list_from_sections_panel
        )

        # Make sure to actually show the new window
        cast(Mock, mock_window.show).assert_called_once()


def test_close_item_list_from_sections_panel(main_controller: MainController) -> None:
    """check the control flow from opening the window -> closing it --> then check the available labels are updated correctly"""

    mock_items = ["mock", "mocker", "most mockest"]
    with patch.object(
        main_controller.components["sections_panel"],
        attribute="update_available_labels",
    ) as mock_updater:
        main_controller.handle_close_item_list_from_sections_panel(mock_items)
        mock_updater.assert_called_once_with(mock_items)
        assert main_controller.popup_window_from_sections is None


def test_only_one_popup_from_sections_panel_exists(
    main_controller: MainController,
) -> None:
    """Check that when pressing the button in the labels panel multiple times, that only a single window is shown"""
    expected_labels = ["mock", "mock", "mock"]
    with patch.object(
        main_controller.components["sections_panel"],
        attribute="get_available_labels",
        return_value=expected_labels,
    ) as _:
        # send the signal to open the window a couple of times:
        main_controller.handle_open_item_list_from_sections_panel()
        main_controller.handle_open_item_list_from_sections_panel()
        main_controller.handle_open_item_list_from_sections_panel()

        # check subsequent logic is only called once
        cast(Mock, main_controller.components["item_list"]).assert_called_once_with(
            expected_labels
        )
        mock_window = cast(
            ItemListController, main_controller.popup_window_from_sections
        )
        cast(Mock, mock_window.show).assert_called_once()


def test_opening_both_item_lists(main_controller: MainController) -> None:
    """You should be able to open both windows as separate pop up windows"""
    expected_labels = ["label", "label", "label"]
    expected_section_labels = ["section", "section", "section"]
    with (
        patch.object(
            main_controller.components["label_panel"],
            attribute="get_available_labels",
            return_value=expected_labels,
        ) as _,
        patch.object(
            main_controller.components["sections_panel"],
            attribute="get_available_labels",
            return_value=expected_section_labels,
        ) as _,
    ):
        # call both methods
        main_controller.handle_open_item_list_from_label_panel()
        main_controller.handle_open_item_list_from_sections_panel()

        # check the windows are displaying the correct lists
        expected_calls = [call(expected_labels), call(expected_section_labels)]
        cast(Mock, main_controller.components["item_list"]).assert_has_calls(
            expected_calls
        )
        assert main_controller.popup_window_from_labels == main_controller.components[
            "item_list"
        ](expected_labels)
        assert main_controller.popup_window_from_sections == main_controller.components[
            "item_list"
        ](expected_section_labels)
