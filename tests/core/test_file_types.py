"""
Test for app/core/file_types.py
"""

import pytest

from app.core.file_types import FileAction, FileType, create_file_filter


@pytest.mark.parametrize(
    "file_type,file_action,expected_str",
    [
        (FileType.RAW_DATA, FileAction.OPEN, "Time traces (*.txt *.npy)"),
        (FileType.RAW_DATA, FileAction.SAVE, "Time traces (*.npy)"),
        (FileType.LABELS, FileAction.OPEN, "Whole-trace labels (*.json)"),
        (FileType.LABELS, FileAction.SAVE, "Whole-trace labels (*.json)"),
        (FileType.SECTION_LABELS, FileAction.OPEN, "Section labels (*.json)"),
        (FileType.SECTION_LABELS, FileAction.OPEN, "Section labels (*.json)"),
    ],
)
def test_creating_file_filter(
    file_type: FileType, file_action: FileAction, expected_str: str
) -> None:
    """Test that the file filter strings are created properly"""

    filter_str = create_file_filter(file_type, file_action)
    assert filter_str == expected_str
