"""
Test 'business logic'
NOTE: Encapsulated code makes these tests quite simple
"""

import pytest

from app.section_label_assignment.sections_panel_model import (
    Section,
    SectionsPanelModel,
)


@pytest.fixture
def available_labels() -> list[str]:
    """A mock set of available labels"""
    return ["first label", "second label", "third label", "fourth label"]


@pytest.fixture
def sections() -> list[Section]:
    """A mock set of Sections"""
    LeBron = Section(start_frame=6, end_frame=23)
    jordan = Section(start_frame=23, end_frame=45)
    kobe = Section(start_frame=8, end_frame=24)
    return [LeBron, jordan, kobe]


@pytest.fixture
def nicknames() -> tuple[dict[tuple[int, int], list[str]], list[Section]]:
    nicknames_dict = {
        (32, 34): ["Shaq", "Big Diesel", "Big Aristotle", "Superman", "Shaq-foo"],
        (34, None): ["Giannis", "Greek Freak", "The Alphabet"],
        (15, None): ["The Joker"],
        (None, 30): ["Baby-faced assassin", "Chef Curry", "Steph"],
    }

    shaq = Section(
        32,
        34,
        assigned_labels=["Shaq", "Big Diesel", "Big Aristotle", "Superman", "Shaq-foo"],
    )
    giannis_antetokounmpo = Section(
        34, None, assigned_labels=["Giannis", "Greek Freak", "The Alphabet"]
    )
    jokic = Section(15, None, assigned_labels=["The Joker"])
    curry = Section(None, 30, ["Baby-faced assassin", "Chef Curry", "Steph"])
    nicknames_sections = [shaq, giannis_antetokounmpo, jokic, curry]
    return nicknames_dict, nicknames_sections


def test_move_to_next_label(available_labels: list[str]) -> None:
    """test happy case: moving to the next when not yet at the end of the list"""
    model = SectionsPanelModel(available_labels=available_labels, current_label_index=0)

    for times_moved in range(1, len(available_labels) - 1):
        model.move_to_next_label()
        assert model.current_label_index == times_moved


def test_do_not_move_past_last_label(available_labels: list[str]) -> None:
    """make sure you just do not move past the final label. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = SectionsPanelModel(
        available_labels=available_labels, current_label_index=len(available_labels) - 1
    )
    model.move_to_next_label()
    assert model.current_label_index == len(available_labels) - 1


def test_move_to_previous_label(available_labels: list[str]) -> None:
    """test happy case: Move back when not at the first label"""
    model = SectionsPanelModel(
        available_labels=available_labels, current_label_index=len(available_labels) - 1
    )
    for times_moved in range(1, model.current_label_index + 1):
        model.move_to_previous_label()
        assert model.current_label_index == (len(available_labels) - 1) - times_moved


def test_do_not_move_beyond_first_label(available_labels: list[str]) -> None:
    """make sure you just do not move back when already at the first label. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = SectionsPanelModel(available_labels=available_labels, current_label_index=0)
    model.move_to_previous_label()
    assert model.current_label_index == 0


def test_move_to_next_section(sections: list[Section]) -> None:
    """test happy case: moving to the next when not yet at the end of the list"""
    model = SectionsPanelModel(sections=sections, current_section_index=0)

    for times_moved in range(1, len(sections) - 1):
        model.move_to_next_section()
        assert model.current_section_index == times_moved


def test_do_not_move_past_last_section(sections: list[Section]) -> None:
    """make sure you just do not move past the final section. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = SectionsPanelModel(
        sections=sections, current_section_index=len(sections) - 1
    )
    model.move_to_next_section()
    assert model.current_section_index == len(sections) - 1


def test_move_to_previous_section(sections: list[Section]) -> None:
    """test happy case: Move back when not at the first label"""
    model = SectionsPanelModel(
        sections=sections, current_section_index=len(sections) - 1
    )
    for times_moved in range(1, model.current_section_index + 1):
        model.move_to_previous_section()
        assert model.current_section_index == (len(sections) - 1) - times_moved


def test_do_not_move_beyond_first_section(sections: list[Section]) -> None:
    """make sure you just do not move back when already at the first section. This will prevent the UI from otherwise crashing when eventually accessing the current label"""
    model = SectionsPanelModel(sections=sections, current_section_index=0)
    model.move_to_previous_section()
    assert model.current_section_index == 0


def test_assigning_new_label(
    available_labels: list[str], sections: list[Section]
) -> None:
    """happy case: new label should get added to list of assigned labels"""
    model = SectionsPanelModel(available_labels=available_labels, sections=sections)
    model.assign_current_label()
    assert model.current_section.assigned_labels == [model.available_labels[0]]

    model.move_to_next_label()
    model.assign_current_label()
    assert model.current_section.assigned_labels == model.available_labels[:2]


def test_assigning_duplicate_label(
    available_labels: list[str], sections: list[Section]
) -> None:
    """duplicate label should not get added to the list of assigned labels"""
    model = SectionsPanelModel(available_labels=available_labels, sections=sections)
    model.assign_current_label()
    model.assign_current_label()
    assert model.current_section.assigned_labels.count(available_labels[0]) == 1
    assert len(model.current_section.assigned_labels) == 1
    assert model.current_section.assigned_labels == [model.available_labels[0]]


def test_removing_assigned_label(
    available_labels: list[str], sections: list[Section]
) -> None:
    """happy case: unassign a previously assigned label"""
    model = SectionsPanelModel(available_labels=available_labels, sections=sections)
    model.assign_current_label()
    model.unassign_current_label()
    assert len(model.current_section.assigned_labels) == 0


def test_removing_already_removed_label(
    available_labels: list[str], sections: list[Section]
) -> None:
    """removing something not assigned yet (or already removed) should just result in nothing happening"""

    # duplicate removal
    model = SectionsPanelModel(available_labels=available_labels, sections=sections)
    model.assign_current_label()
    model.move_to_next_label()
    model.assign_current_label()
    model.unassign_current_label()
    model.unassign_current_label()
    assert len(model.current_section.assigned_labels) == 1
    assert model.current_section.assigned_labels == [model.available_labels[0]]

    # removal before assigning the first time
    model = SectionsPanelModel(available_labels=available_labels, sections=sections)
    model.unassign_current_label()
    assert len(model.current_section.assigned_labels) == 0
    model.assign_current_label()
    model.move_to_next_label()
    model.unassign_current_label()
    assert len(model.current_section.assigned_labels) == 1
    assert model.current_section.assigned_labels == [model.available_labels[0]]


def test_updating_available_labels(available_labels: list[str]) -> None:
    """should be simple setting operation in simplest implementation. Technically not needed to test, but serves as safety valve if code gets refactored and implementation changes."""
    # start with the labels set in the fixture above
    model = SectionsPanelModel(available_labels=available_labels)
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
    model = SectionsPanelModel(available_labels=available_labels, current_label_index=0)
    original_labels = available_labels.copy()
    index_before = model.current_label_index
    label_before = model.current_label

    # expand the available labels
    incl_additional_label = original_labels.copy()
    incl_additional_label.append("one more label")
    model.update_available_labels(incl_additional_label)
    assert model.current_label_index == index_before
    assert model.current_label == label_before

    # remove one of the available labels
    excl_last_label = original_labels.copy()
    excl_last_label.pop()
    model.update_available_labels(excl_last_label)
    assert model.current_label_index == index_before
    assert model.current_label == label_before

    # remove internal label: remove the second label
    excl_internal_label = original_labels.copy()
    excl_internal_label.remove(original_labels[1])
    model.update_available_labels(excl_internal_label)
    assert model.current_label_index == index_before
    assert model.current_label == label_before


def test_current_label_after_deletion_original(available_labels: list[str]) -> None:
    """check where the index is pointing at when removing the label you pointed at before the update"""
    # start with the labels set in the fixture above and the pointer being at the first label (will not be removed whatsoever)
    model = SectionsPanelModel(available_labels=available_labels, current_label_index=1)
    original_labels = available_labels.copy()
    index_before = model.current_label_index

    # remove the second label (at index 1)
    # remove internal label: remove the second label
    excl_internal_label = original_labels.copy()
    excl_internal_label.remove(original_labels[1])
    model.update_available_labels(excl_internal_label)
    assert model.current_label_index == index_before - 1
    assert model.current_label == original_labels[index_before - 1]


def test_current_label_after_removing_last_label(available_labels: list[str]) -> None:
    """Make sure that when you reduce the list of available labels, and you were originally pointing at the final one, that you moved the index one down"""
    # start by pointing at the final label
    model = SectionsPanelModel(
        available_labels=available_labels, current_label_index=len(available_labels) - 1
    )
    original_labels = available_labels.copy()
    index_before = model.current_label_index

    # remove the final label
    excl_last_label = original_labels.copy()
    excl_last_label.pop()
    model.update_available_labels(excl_last_label)
    assert model.current_label_index == index_before - 1
    assert model.current_label == original_labels[-2]


def test_creating_a_new_section() -> None:
    """
    Should be trivial as simplest implementation is just some basic builtin python operations,
    but better safe then sorry. When refactoring code, you might change things unintentionally"""
    model = SectionsPanelModel()
    assert len(model.sections) == 0
    model.create_new_section()
    assert len(model.sections) == 1
    assert isinstance(model.sections[0], Section)
    assert model.current_section == model.sections[0]
    assert model.current_section.start_frame is None
    assert model.current_section.end_frame is None


def removing_last_added_section(sections: list[Section]) -> None:
    """
    Should be trivial as simplest implementation is just some basic builtin python operations,
    but better safe then sorry. When refactoring code, you might change things unintentionally
    """
    model = SectionsPanelModel(sections=sections)
    model.remove_last_section()
    LeBron = Section(start_frame=6, end_frame=23)
    jordan = Section(start_frame=23, end_frame=45)
    assert model.sections == [LeBron, jordan]


def removing_when_no_section_yet(sections: list[Section]) -> None:
    """
    Should be implemented in a way such that nothing happens when you try to remove a section while not having created one first
    (or trying to remove one more than you have in total)
    """

    # removing before you created the first one
    model = SectionsPanelModel()
    model.remove_last_section()
    assert model.sections == []

    # Remove more sections then available
    model = SectionsPanelModel(sections=sections)
    for _ in range(len(sections) + 1):
        model.remove_last_section()

    assert model.sections == []


def test_changing_the_starting_frame_of_section(sections: list[Section]) -> None:
    """Simple test to see if you can adjust the start of a current section"""
    model = SectionsPanelModel(sections=sections)
    assert model.current_section.start_frame == 6
    model.set_start_section(0)
    assert model.current_section.start_frame == 0


def test_changing_the_final_frame_of_section(sections: list[Section]) -> None:
    """Simple test to see if you can adjust the end of a current section"""
    model = SectionsPanelModel(sections=sections)
    assert model.current_section.end_frame == 23
    model.set_end_section(42)
    assert model.current_section.end_frame == 42


def test_resetting_sections_from_dictionary(
    sections: list[Section],
    nicknames: tuple[dict[tuple[int, int], list[str]], list[Section]],
) -> None:
    """
    Mimic changing to a different trace, with its own section labels
    NOTE: Yes, I had to keep it fun for myself ;). It is a legit test to perform though, but could've used less incoming sections.
    """
    # The outgoing sections
    original_sections = sections.copy()
    LeBron = Section(start_frame=6, end_frame=23)

    # The incoming sections
    nicknames_dict, expected_sections = nicknames

    # perform operation
    model = SectionsPanelModel(sections=sections)
    model.reset_sections(section_labels=nicknames_dict)
    assert LeBron in original_sections
    assert LeBron not in model.sections
    assert model.sections == expected_sections


def test_creating_dictionary_from_sections(
    nicknames: tuple[dict[tuple[int, int], list[str]], list[Section]],
) -> None:
    """Test producing the dictionary of section labels that is compatible with the time trace tools from the list of sections kept internally in the Model"""
    expected_dictionary, nicknames_sections = nicknames
    model = SectionsPanelModel(sections=nicknames_sections)
    assert model.sections_to_dictionary() == expected_dictionary


def test_determining_section_boundaries(
    nicknames: tuple[dict[tuple[int, int], list[str]], list[Section]],
) -> None:
    """Test producing the list of frame numbers where sections start / end goes as expected"""
    expected_boundaries = [32, 34, 34, 15, 30]
    _, nicknames_sections = nicknames
    model = SectionsPanelModel(sections=nicknames_sections)
    assert model.determine_section_boundaries() == expected_boundaries
