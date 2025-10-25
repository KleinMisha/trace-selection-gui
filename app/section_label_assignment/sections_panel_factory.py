"""
Factory: Takes care of instantiating this component's MVC, and creates a Controller that the MainController can communicate with.
NOTE: The Returned Controller should satisfy the Protocols/APIs as defined in the app/main_app/controller_protocols.py

NOTE: It also takes care of placing the component in its respective placeholder in the main UI
"""

from PyQt6.QtWidgets import QWidget

from app.component_factory_helpers import fill_component_to_placeholder
from app.section_label_assignment.sections_panel_config import SectionsPanelConfig
from app.section_label_assignment.sections_panel_controller import (
    SectionsPanelController,
)
from app.section_label_assignment.sections_panel_model import SectionsPanelModel
from app.section_label_assignment.sections_panel_view import SectionsPanelView


def create_sections_panel(
    placeholder: QWidget | None, config: SectionsPanelConfig
) -> SectionsPanelController:
    model = SectionsPanelModel()
    view = SectionsPanelView(parent=placeholder)
    controller = SectionsPanelController(model, view, config)

    # ensure the component fills the placeholder correctly
    if placeholder:
        fill_component_to_placeholder(view, placeholder, force_layout=True)

    return controller
