"""
Generic part of the component factories.
Essentially, this part is the same for all.
The individual components still keep their "_factory.py" file that wraps around the functions shown here.

This way...
1. avoids code duplication: Would otherwise need to move all of this into every individual factory file.
    This method allows us to test the component_factory individually.
2. still keeping the individual factories avoids main.py from importing all the models, views, and controllers, just imports the factories, keeps it simple
"""

from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget


def fill_component_to_placeholder(
    component: QWidget, placeholder: QWidget, force_layout: bool = True
) -> None:
    """ensures the component view fills the placeholder correctly"""
    # undo the background used as visual indicator when creating the UI for the MainView
    placeholder.setStyleSheet("background-color: transparent;")
    # Make the component expand to fill available space
    component.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    if force_layout:
        _force_component_layout(component)

    # Create a top-level layout for the placeholder and add the component's View to the placeholder's layout
    placeholder_layout = QVBoxLayout(placeholder)
    placeholder_layout.setContentsMargins(0, 0, 0, 0)
    placeholder_layout.addWidget(component)


def _force_component_layout(component: QWidget) -> None:
    """Force a top-level layout onto the component view in case the component otherwise does not scale / translate properly into the desired placeholder"""

    # Get all existing child widgets before creating layout
    existing_children = [
        child for child in component.children() if isinstance(child, QWidget)
    ]

    # Give the component a top-level layout and register / add its child components
    component_layout = QVBoxLayout(component)
    component_layout.setContentsMargins(0, 0, 0, 0)
    for child in existing_children:
        child.setParent(None)
        component_layout.addWidget(child)
