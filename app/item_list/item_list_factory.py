"""
Factory: Takes care of instantiating this component's MVC, and creates a Controller that the MainController can communicate with.

NOTE: Because this will be a popup window ---> We do not pass it a placeholder widget, but let MainController know of this factory
"""

from typing import Optional

from app.item_list.item_list_controller import ItemListController
from app.item_list.item_list_model import ItemList as ItemListModel
from app.item_list.item_list_view import PyQtView as ItemListView


def create_item_list(
    items: list[str], title: Optional[str] = None
) -> ItemListController:
    """To be called by the main.py when setting up the entire app"""
    model = ItemListModel(items)
    view = ItemListView(title=title)
    controller = ItemListController(model, view)
    return controller
