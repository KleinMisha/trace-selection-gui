from PyQt6.QtWidgets import QWidget

from app.component_factory_helpers import fill_component_to_placeholder
from app.theme_manager.theme_controller import ThemeController
from app.theme_manager.theme_model import ThemeModel
from app.theme_manager.theme_view import ThemeView


def create_theme_controller(placeholder: QWidget | None) -> ThemeController:
    """
    To be called by the main.py when setting up the entire app

    ?TODO: Initial configuration can be set here via a configuration setting ?
    """
    model = ThemeModel()
    view = ThemeView()
    controller = ThemeController(model, view)
    if placeholder:
        fill_component_to_placeholder(view, placeholder, force_layout=True)
    return controller
