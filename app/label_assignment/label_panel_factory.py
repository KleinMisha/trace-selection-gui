"""
Factory: Takes care of instantiating this component's MVC, and creates a Controller that the MainController can communicate with.
NOTE: The Returned Controller should satisfy the Protocols/APIs as defined in the app/main_app/controller_protocols.py

NOTE: It also takes care of placing the component in its respective placeholder in the main UI
"""

from PyQt6.QtWidgets import QWidget
from app.label_assignment.label_panel_model import LabelPanelModel
from app.label_assignment.label_panel_view import LabelPanelView
from app.label_assignment.label_panel_controller import LabelPanelController


def create_label_panel(placeholder: QWidget | None = None) -> LabelPanelController:
    """To be called by the main.py when setting up the entire app"""
    model = LabelPanelModel()
    view = LabelPanelView(parent=placeholder)
    controller = LabelPanelController(model, view)
    return controller
