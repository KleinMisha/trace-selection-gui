"""Test basics of adding/removing items"""

from trace_selection.label_list_app.label_list_model import LabelList


def test_add_label() -> None:
    model = LabelList()
    model.add_label("first_label")
    assert "first_label" in model.get_labels()


def test_remove_label() -> None:
    model = LabelList()
    model.add_label("first_label")
    model.add_label("second_label")
    model.remove_label("first_label")
    assert "first_label" not in model.get_labels()
    assert "second_label" in model.get_labels()
