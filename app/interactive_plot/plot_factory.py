"""
Factory: Takes care of instantiating this component's MVC, and creates a Controller that the MainController can communicate with.
NOTE: The Returned Controller should satisfy the Protocols/APIs as defined in the app/main_app/controller_protocols.py

NOTE: It also takes care of placing the component in its respective placeholder in the main UI
"""

from PyQt6.QtWidgets import QWidget

from app.core.component_factory_helpers import fill_component_to_placeholder
from app.interactive_plot.plot_config import InterActivePlotConfig
from app.interactive_plot.plot_controller import InteractivePlotController
from app.interactive_plot.plot_model import InteractivePlotModel
from app.interactive_plot.plot_view import InterActivePlotView


def create_plot_controller(
    placeholder: QWidget | None, config: InterActivePlotConfig
) -> InteractivePlotController:
    """To be called by the main.py when setting up the entire app"""
    MIN_TIME = config.min_time or 0.0
    MAX_TIME = config.max_time or 3600.0
    MIN_HEIGHT = config.min_height or 0.0
    MAX_HEIGHT = config.max_height or 10.0
    model = InteractivePlotModel(
        t_min=MIN_TIME, t_max=MAX_TIME, z_min=MIN_HEIGHT, z_max=MAX_HEIGHT
    )
    view = InterActivePlotView(parent=placeholder)
    controller = InteractivePlotController(model, view, config)
    if placeholder:
        fill_component_to_placeholder(view, placeholder, force_layout=False)
    return controller
