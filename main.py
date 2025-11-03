"""
Main entry-point to start running the full application.

Stich everything together.
Instantiate all the specific components, and start the Model,View and Controller
"""

import sys
from pathlib import Path
from typing import cast

from PyQt6.QtWidgets import QApplication

from app.config_manager import ConfigManager
from app.interactive_plot.plot_config import InterActivePlotConfig
from app.interactive_plot.plot_factory import create_plot_controller
from app.item_list.item_list_factory import create_item_list
from app.label_assignment.label_panel_config import LabelPanelConfig
from app.label_assignment.label_panel_factory import create_label_panel
from app.main_app.main_config import MainConfig
from app.main_app.main_controller import ComponentControllers, MainController
from app.main_app.main_model import MainModel
from app.main_app.main_view import MainView
from app.section_label_assignment.sections_panel_config import SectionsPanelConfig
from app.section_label_assignment.sections_panel_factory import create_sections_panel
from app.theme_manager.theme_config import ThemeConfig
from app.theme_manager.theme_factory import create_theme_controller

CONFIG_FILE = Path(__file__).parent / "config.json"


def main():
    # must start with a QApplication before creating QWidgets
    app = QApplication(sys.argv)

    # build the configuration from settings in file
    config_manger = ConfigManager()
    config_manger.register("main", MainConfig)
    config_manger.register("label_assignment", LabelPanelConfig)
    config_manger.register("section_assignment", SectionsPanelConfig)
    config_manger.register("plot", InterActivePlotConfig)
    config_manger.register("theme", ThemeConfig)
    config_manger.load(CONFIG_FILE)

    main_config = cast(MainConfig, config_manger.get_config("main"))
    label_config = cast(LabelPanelConfig, config_manger.get_config("label_assignment"))
    sections_config = cast(
        SectionsPanelConfig, config_manger.get_config("section_assignment")
    )
    plot_config = cast(InterActivePlotConfig, config_manger.get_config("plot"))
    theme_config = cast(ThemeConfig, config_manger.get_config("theme"))
    # Start setting up the main controller
    model = MainModel()
    view = MainView()
    view.show()

    components: ComponentControllers = {
        "interactive_plot": create_plot_controller(
            placeholder=view.InterActivePlotView, config=plot_config
        ),
        "label_panel": create_label_panel(
            placeholder=view.LabelPanelView, config=label_config
        ),
        "sections_panel": create_sections_panel(
            placeholder=view.SectionsPanelView, config=sections_config
        ),
        "item_list": create_item_list,
        "theme_manager": create_theme_controller(
            placeholder=view.ThemeView, config=theme_config
        ),
    }
    controller = MainController(model, view, components=components, config=main_config)
    _ = controller

    # start the application
    app.exec()


if __name__ == "__main__":
    main()
