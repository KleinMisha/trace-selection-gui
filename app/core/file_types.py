"""
File types used as input/output data.
"""

from enum import Enum, auto
from pathlib import Path


class FileAction(Enum):
    """The kinds of actions performed on a file"""

    OPEN = auto()
    SAVE = auto()


class FileType(Enum):
    """
    The different file types known in the application.
    ----

    VALUE = (ENTER DESCRIPTION HERE, ACTION_TO_EXTENSIONS)
    with
    the description: The text that will appear in the file-dialogue's drop down before the file extensions.
    the allowed extensions supplied as: dict[FileAction: tuple[str]], which maps what file formats are excepted for opening/saving the particular file types
    """

    RAW_DATA = (
        "Time traces",
        {FileAction.OPEN: (".txt", ".npy"), FileAction.SAVE: (".npy",)},
    )
    LABELS = (
        "Whole-trace labels",
        {FileAction.OPEN: (".json",), FileAction.SAVE: (".json",)},
    )
    SECTION_LABELS = (
        "Section labels",
        {FileAction.OPEN: (".json",), FileAction.SAVE: (".json",)},
    )

    def __init__(
        self, description: str, extensions: dict[FileAction, tuple[str, ...]]
    ) -> None:
        self.description = description
        self.extensions = extensions

    def extensions_for(self, action: FileAction) -> tuple[str, ...]:
        return self.extensions[action]

    def to_filter(self, action: FileAction) -> str:
        """build a filter string that Qt uses as keyword argument in the FileDialogue"""
        allowed_extensions = " ".join(
            [f"*{ext}" for ext in self.extensions_for(action)]
        )
        return f"{self.description} ({allowed_extensions})"


def is_valid_file_extension(
    file: Path, file_type: FileType, file_action: FileAction
) -> bool:
    """Checks if the selected file has the correct file extension"""
    allowed_extensions = file_type.extensions_for(file_action)
    return file.suffix in allowed_extensions


def create_file_filter(file_type: FileType, file_action: FileAction) -> str:
    """Builds the qt file filter string for the given file type/menu bar action combination"""
    return file_type.to_filter(file_action)
