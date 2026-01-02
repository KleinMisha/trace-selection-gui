"""
Compile the Qt-Designer files (.ui) to Python code.
This makes calling variables from Views much easier (as now they can simply import the compiled objects)
"""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path("app/")


def find_ui_files(root_directory: Path) -> list[Path]:
    """search the code's directory to find all the ui files"""
    return list(root_directory.rglob("*.ui"))


def compile_ui_to_py(ui_file: Path, py_file: Path) -> bool:
    """
    Compiles an individual file and returns a boolean to indicate if it succeeded
    NOTE: Catch this boolean in the main() function to determine if compiling all files was a success
    """
    print(f" -{ui_file} \N{RIGHTWARDS ARROW} {py_file}")
    try:
        subprocess.run(
            ["uv", "run", "python", "-m", "PyQt6.uic.pyuic", str(ui_file), "-o", str(py_file)],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"\N{CHECK MARK} compiled: {ui_file} \N{RIGHTWARDS ARROW} {py_file}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\N{CROSS MARK} Failed to compile {ui_file}")
        print(f"  Error message: {e.stderr}")

        return False

    except FileNotFoundError:
        print(
            "\N{CROSS MARK}. Make sure you have PyQt installed in this environment:`uv add PyQt6`"
        )
        return False


def main() -> int:
    print("  Finding .ui files ...")
    ui_files = find_ui_files(ROOT_DIR)

    print(f"Found {len(ui_files)} .ui files. \nWill attempt to compile: ")
    py_files = []
    for ui_file in ui_files:
        directory = ui_file.parent
        file_name = f"{ui_file.stem}_ui.py"
        py_file = directory / file_name
        py_files.append(py_file)
        print(f" -{ui_file} \N{RIGHTWARDS ARROW} {py_file}")

    successes = 0
    print("  Compiling .ui files ...")
    for ui_file, py_file in zip(ui_files, py_files):
        successes += compile_ui_to_py(ui_file, py_file)

    print(f"Succesfully compiled {successes} out of {len(ui_files)} .ui files.")

    if successes < len(ui_files):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
