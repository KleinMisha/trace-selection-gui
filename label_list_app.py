"""
Standalone app to keep track of a list of items.
(mainly used during development + testing)
"""

import sys

from PyQt6.QtWidgets import QApplication

from trace_selection.label_list_app.label_list_controller import LabelListController
from trace_selection.label_list_app.label_list_model import LabelList
from trace_selection.label_list_app.label_list_view import PyQtView


def main() -> None:
    app = QApplication(sys.argv)

    model = LabelList()  # start with empty list for now.
    view = PyQtView()
    controller = LabelListController(model, view)
    _ = controller

    view.show()

    app.exec()


if __name__ == "__main__":
    main()
