"""
Frequently used type definitions (avoids copying this allover the code)
"""

from typing import Sequence, TypeAlias, Union

# Type hint for anything that is a proper color input.
Color: TypeAlias = Union[
    str,  # "red", "#FF00FF", "0.5", "C0"
    tuple[float, float, float],  # RGB
    tuple[float, float, float, float],  # RGBA
    Sequence[float],  # list/array of floats
]
