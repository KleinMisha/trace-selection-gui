"""
Main entry-point to start running the full application.

Stich everything together.
Instantiate all the specific components, and start the Model,View and Controller
"""

import sys

from PyQt6.QtWidgets import QApplication

from app.interactive_plot.plot_factory import create_plot_controller
from app.item_list.item_list_factory import create_item_list
from app.label_assignment.label_panel_factory import create_label_panel
from app.main_app.main_controller import ComponentControllers, MainController
from app.main_app.main_model import MainModel
from app.main_app.main_view import MainView
from app.section_label_assignment.sections_panel_factory import create_sections_panel
from app.theme_manager.theme_factory import create_theme_controller


def main():
    # must start with a QApplication before creating QWidgets
    app = QApplication(sys.argv)

    # Start setting up the main controller
    model = MainModel()
    view = MainView()
    view.show()

    components: ComponentControllers = {
        "interactive_plot": create_plot_controller(
            placeholder=view.InterActivePlotView
        ),
        "label_panel": create_label_panel(placeholder=view.LabelPanelView),
        "sections_panel": create_sections_panel(placeholder=view.SectionsPanelView),
        "item_list": create_item_list,
        "theme_manager": create_theme_controller(placeholder=view.ThemeView),
    }
    controller = MainController(model, view, components=components)
    _ = controller

    # start the application
    app.exec()


if __name__ == "__main__":
    main()
