"""
Factory: Takes care of instantiating this component's MVC, and creates a Controller that the MainController can communicate with.
NOTE: The Returned Controller should satisfy the Protocols/APIs as defined in the app/main_app/controller_protocols.py

NOTE: It also takes care of placing the component in its respective placeholder in the main UI
"""

from PyQt6.QtWidgets import QWidget
from time_trace_tools.data_types.magnetic_tweezers_trace import MagneticTweezersTrace

from app.interactive_plot.plot_controller import InteractivePlotController
from app.interactive_plot.plot_model import InteractivePlotModel
from app.interactive_plot.plot_view import InterActivePlotView

# TODO: Add these things to a configuration file
MIN_TIME = 0.0
MAX_TIME = 3600.0
MIN_HEIGHT = -1.0
MAX_HEIGHT = 1.0


def create_plot_controller(placeholder: QWidget) -> InteractivePlotController:
    """To be called by the main.py when setting up the entire app"""
    model = InteractivePlotModel(
        t_min=MIN_TIME, t_max=MAX_TIME, z_min=MIN_HEIGHT, z_max=MAX_HEIGHT
    )
    view = InterActivePlotView(parent=placeholder)
    controller = InteractivePlotController(model, view)
    return controller
