"""
Factory: Takes care of instantiating this component's MVC, and creates a Controller that the MainController can communicate with.
NOTE: The Returned Controller should satisfy the Protocols/APIs as defined in the app/main_app/controller_protocols.py

NOTE: It also takes care of placing the component in its respective placeholder in the main UI
"""

from PyQt6.QtWidgets import QWidget

from app.component_factory_helpers import fill_component_to_placeholder
from app.label_assignment.label_panel_config import LabelPanelConfig
from app.label_assignment.label_panel_controller import LabelPanelController
from app.label_assignment.label_panel_model import LabelPanelModel
from app.label_assignment.label_panel_view import LabelPanelView


def create_label_panel(
    placeholder: QWidget | None, config: LabelPanelConfig
) -> LabelPanelController:
    """To be called by the main.py when setting up the entire app"""
    model = LabelPanelModel()
    view = LabelPanelView(parent=placeholder)
    controller = LabelPanelController(model, view, config)
    if placeholder:
        fill_component_to_placeholder(view, placeholder, force_layout=True)
    return controller
