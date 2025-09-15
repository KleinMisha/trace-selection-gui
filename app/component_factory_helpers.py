"""
Generic part of the component factories.
Essentially, this part is the same for all.
The individual components still keep their "_factory.py" file that wraps around the functions shown here.

This way...
1. avoids code duplication: Would otherwise need to move all of this into every individual factory file.
    This method allows us to test the component_factory individually.
2. still keeping the individual factories avoids main.py from importing all the models, views, and controllers, just imports the factories, keeps it simple
"""

from PyQt6.QtWidgets import QVBoxLayout, QWidget


def fill_component_to_placeholder(component: QWidget, placeholder: QWidget) -> None:
    """ensures the component view fills the placeholder correctly"""
    # undo the background used as visual indicator when creating the UI for the MainView
    placeholder.setStyleSheet("background-color: transparent;")

    # Get all existing child widgets before creating layout
    existing_children = [
        child for child in component.children() if isinstance(child, QWidget)
    ]

    # Give the component a top-level layout and register / add its child components
    component_layout = QVBoxLayout(component)
    component_layout.setContentsMargins(0, 0, 0, 0)
    for child in existing_children:
        child.setParent(None)  # Remove from old positioning
        component_layout.addWidget(child)  # Add to layout
    # Add view to placeholder
    layout = QVBoxLayout(placeholder)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(component)
