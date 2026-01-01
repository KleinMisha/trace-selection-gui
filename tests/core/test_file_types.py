"""
Test for app/core/file_types.py
"""

from pathlib import Path

import pytest

from app.core.file_types import (
    FileAction,
    FileType,
    create_file_filter,
    is_valid_file_extension,
)


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


@pytest.mark.parametrize(
    "file_type, file_action", [(ft, fa) for ft in FileType for fa in FileAction]
)
def test_valid_files(file_type: FileType, file_action: FileAction) -> None:
    """happy path: opening/saving into a file with the correct extension"""
    basename = "dummy_file"
    allowed_extensions = file_type.extensions_for(file_action)
    for ext in allowed_extensions:
        file_path = Path(f"/path/to/{basename}{ext}")
        assert is_valid_file_extension(file_path, file_type, file_action)


@pytest.mark.parametrize(
    "file_type, file_action", [(ft, fa) for ft in FileType for fa in FileAction]
)
def test_invalid_file(file_type: FileType, file_action: FileAction) -> None:
    """Selecting some other file type should fail the check"""
    file_path = Path("/path/to/dummy.mock")
    assert not is_valid_file_extension(file_path, file_type, file_action)
