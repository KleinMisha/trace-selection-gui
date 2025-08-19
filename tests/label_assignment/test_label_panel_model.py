"""
Test 'business logic'
NOTE: Encapsulated code makes these tests quite simple
"""

import pytest

from app.label_assignment.label_panel_model import LabelPanelModel


@pytest.fixture
def available_labels() -> list[str]:
    """A mock set of available labels"""
    return ["first label", "second label", "third label", "fourth label"]


def test_move_to_next(available_labels: list[str]) -> None:
    """test happy case: moving to the next when not yet at the end of the list"""
    model = LabelPanelModel(available_labels=available_labels, current_idx=0)

    for times_moved in range(1, len(available_labels) - 1):
        model.move_to_next()
        assert model.current_idx == times_moved


def test_do_not_move_past_last_label(available_labels: list[str]) -> None:
    """make sure you just do not move past the final label. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = LabelPanelModel(
        available_labels=available_labels, current_idx=len(available_labels) - 1
    )
    model.move_to_next()
    assert model.current_idx == len(available_labels) - 1


def test_move_to_previous(available_labels: list[str]) -> None:
    """test happy case: Move back when not at the first label"""
    model = LabelPanelModel(
        available_labels=available_labels, current_idx=len(available_labels) - 1
    )
    for times_moved in range(1, model.current_idx + 1):
        model.move_to_previous()
        assert model.current_idx == (len(available_labels) - 1) - times_moved


def test_do_not_move_beyond_first(available_labels: list[str]) -> None:
    """make sure you just do not move back when already at the first label. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = LabelPanelModel(available_labels=available_labels, current_idx=0)
    model.move_to_previous()
    assert model.current_idx == 0


def test_resetting_assigned_labels(available_labels: list[str]) -> None:
    """should be simple setting operation in simplest implementation. Technically not needed to test, but serves as safety valve if code gets refactored and implementation changes."""
    # the first trace only has the first label assigned
    model = LabelPanelModel(
        available_labels=available_labels, assigned_labels=["first label"]
    )

    # the next trace has the first two labels
    model.reset_assigned_labels(labels_new_trace=["first label", "second label"])
    assert model.assigned_labels == ["first label", "second label"]

    # another trace only has the third label assigned
    model.reset_assigned_labels(labels_new_trace=["third label"])
    assert "first label" not in model.assigned_labels
    assert "second label" not in model.assigned_labels
    assert model.assigned_labels == ["third label"]


def test_updating_available_labels(available_labels: list[str]) -> None:
    """should be simple setting operation in simplest implementation. Technically not needed to test, but serves as safety valve if code gets refactored and implementation changes."""
    # start with the labels set in the fixture above
    model = LabelPanelModel(available_labels=available_labels)
    original_labels = available_labels.copy()

    # expand the available labels
    incl_additional_label = original_labels.copy()
    incl_additional_label.append("one more label")
    model.update_available_labels(incl_additional_label)
    assert len(model.available_labels) == len(original_labels) + 1
    assert model.available_labels == original_labels + ["one more label"]

    # remove one of the available labels
    excl_last_label = original_labels.copy()
    excl_last_label.pop()
    model.update_available_labels(excl_last_label)
    assert len(model.available_labels) == len(original_labels) - 1
    assert model.available_labels == original_labels[:-1]

    # remove internal label: remove the second label
    excl_internal_label = original_labels.copy()
    excl_internal_label.remove(original_labels[1])
    model.update_available_labels(excl_internal_label)
    assert len(model.available_labels) == len(original_labels) - 1
    assert model.available_labels == original_labels[:1] + original_labels[2:]


def test_current_label_value_after_updates(available_labels: list[str]) -> None:
    """Make sure that the current label (if not removed) does not change when you update the list"""
    # start with the labels set in the fixture above and the pointer being at the first label (will not be removed whatsoever)
    model = LabelPanelModel(available_labels=available_labels, current_idx=0)
    original_labels = available_labels.copy()
    index_before = model.current_idx
    label_before = model.current_label

    # expand the available labels
    incl_additional_label = original_labels.copy()
    incl_additional_label.append("one more label")
    model.update_available_labels(incl_additional_label)
    assert model.current_idx == index_before
    assert model.current_label == label_before

    # remove one of the available labels
    excl_last_label = original_labels.copy()
    excl_last_label.pop()
    model.update_available_labels(excl_last_label)
    assert model.current_idx == index_before
    assert model.current_label == label_before

    # remove internal label: remove the second label
    excl_internal_label = original_labels.copy()
    excl_internal_label.remove(original_labels[1])
    model.update_available_labels(excl_internal_label)
    assert model.current_idx == index_before
    assert model.current_label == label_before


def test_current_label_after_deletion_original(available_labels: list[str]) -> None:
    """check where the index is pointing at when removing the label you pointed at before the update"""
    # start with the labels set in the fixture above and the pointer being at the first label (will not be removed whatsoever)
    model = LabelPanelModel(available_labels=available_labels, current_idx=1)
    original_labels = available_labels.copy()
    index_before = model.current_idx

    # remove the second label (at index 1)
    # remove internal label: remove the second label
    excl_internal_label = original_labels.copy()
    excl_internal_label.remove(original_labels[1])
    model.update_available_labels(excl_internal_label)
    assert model.current_idx == index_before - 1
    assert model.current_label == original_labels[index_before - 1]


def test_current_label_after_removing_last_label(available_labels: list[str]) -> None:
    """Make sure that when you reduce the list of available labels, and you were originally pointing at the final one, that you moved the index one down"""
    # start by pointing at the final label
    model = LabelPanelModel(
        available_labels=available_labels, current_idx=len(available_labels) - 1
    )
    original_labels = available_labels.copy()
    index_before = model.current_idx

    # remove the final label
    excl_last_label = original_labels.copy()
    excl_last_label.pop()
    model.update_available_labels(excl_last_label)
    assert model.current_idx == index_before - 1
    assert model.current_label == original_labels[-2]
