"""
Factory: Takes care of instantiating this component's MVC, and creates a Controller that the MainController can communicate with.
NOTE: The Returned Controller should satisfy the Protocols/APIs as defined in the app/main_app/controller_protocols.py

NOTE: It also takes care of placing the component in its respective placeholder in the main UI
"""

from PyQt6.QtWidgets import QWidget

from app.section_label_assignment.sections_panel_controller import (
    SectionsPanelController,
)
from app.section_label_assignment.sections_panel_model import SectionsPanelModel
from app.section_label_assignment.sections_panel_view import SectionsPanelView


def create_sections_panel(
    placeholder: QWidget | None = None,
) -> SectionsPanelController:
    model = SectionsPanelModel()
    view = SectionsPanelView(parent=placeholder)
    controller = SectionsPanelController(model, view)
    return controller
