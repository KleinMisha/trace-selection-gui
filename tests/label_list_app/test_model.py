"""Test basics of adding/removing items"""

from app.item_list.item_list_model import ItemList


def test_add_label() -> None:
    model = ItemList()
    model.add_item("first_label")
    assert "first_label" in model.get_items()


def test_remove_label() -> None:
    model = ItemList()
    model.add_item("first_label")
    model.add_item("second_label")
    model.remove_item("first_label")
    assert "first_label" not in model.get_items()
    assert "second_label" in model.get_items()
