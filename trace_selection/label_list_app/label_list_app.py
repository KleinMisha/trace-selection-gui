"""
Standalone app to keep track of a list of items.
(mainly used during development + testing)
"""

import sys

from label_list_controller import LabelListController
from label_list_model import LabelList
from label_list_view import PyQtView
from PyQt6.QtWidgets import QApplication


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
