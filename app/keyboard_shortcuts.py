"""
Helper methods to deal with keyboard shortcuts
"""

from string import ascii_lowercase

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import QAbstractButton

# Type Alias for Qt elements that accept shortcuts
AcceptsShortCut = QAction | QAbstractButton


MODIFIER_SYNONYMS = {
    "ctrl": "Ctrl",
    "control": "Ctrl",
    "cmd": "Ctrl",
    "command": "Ctrl",
    "meta": "Meta",
    "^": "Meta",
    "windows": "Meta",
    "shift": "Shift",
    "alt": "Alt",
    "opt": "Alt",
    "option": "Alt",
}
MODIFIER_KEYS = set(MODIFIER_SYNONYMS.keys())


LETTERS = set(ascii_lowercase)
NUMBERS = {str(num) for num in range(10)}
NAV_KEYS = {"=", "-", "+", "up", "down", "left", "right", ",", "."}
FUNCTION_KEYS = {f"f{number}" for number in range(1, 13)}
NON_MODIFIER_KEYS = LETTERS | NUMBERS | NAV_KEYS | FUNCTION_KEYS


KNOWN_KEYS = MODIFIER_KEYS | NON_MODIFIER_KEYS


def assign_shortcut(
    target: AcceptsShortCut, shortcut: str, description_prefix: str | None = None
) -> None:
    """
     Assigns keyboard shortcut and makes description reflect this change
     ---
    Sets the descriptive text in the menu bar (`QAction`) or in the tooltip (`QAbstractbutton`) as
    >> f"{`description_prefix`} \t {`shortcut(with symbols)`}"
    **_If no `description_prefix` is provided, the description will be set to (f"{`shortcut(with symbols)`}")_**
    """

    # assign the shortcut:
    key_sequence = QKeySequence(shortcut)
    target.setShortcut(key_sequence)
    # make description reflect the shortcut
    key_icons = key_sequence.toString(QKeySequence.SequenceFormat.NativeText)
    display_text = (
        f"{description_prefix}\t{key_icons}" if description_prefix else f"{key_icons}"
    )

    if isinstance(target, QAction):
        # menu actions allow you to directly connect a shortcut to their trigger signal
        target.setText(display_text)

    elif isinstance(target, QAbstractButton):
        # for buttons: add text to tooltip
        target.setToolTip(display_text)


def clean_shortcut(shortcut: str) -> str:
    """parses entered shortcut to valid name of a shortcut that Qt can use"""
    parts = [part.strip() for part in shortcut.split("+")]
    keys = []
    for part in parts:
        # get the modifier key (from optionally its synnonym), otherwise just the key itself
        key = MODIFIER_SYNONYMS.get(part.lower(), part.upper())
        keys.append(key)
    return "+".join(keys)


def is_valid(shortcut: str) -> bool:
    """checks if entry is a valid keyboard sequence"""
    keys = [part.strip() for part in shortcut.split("+") if part.strip()]

    # empty key combo
    if len(keys) == 0:
        return False

    if _is_incomplete(shortcut):
        return False

    if not _has_modifier(keys):
        return False

    if _has_multiple_non_modifiers(keys):
        print("multiple non-mod keys")
        return False

    if _has_duplicate_keys(keys):
        return False

    return all(key.lower() in KNOWN_KEYS for key in keys)


def _is_incomplete(shortcut: str) -> bool:
    """leading/trailing '+'-sign means the key combination is incomplete."""

    has_leading_plus = shortcut.replace(" ", "")[0] == "+"

    second_to_last = (
        shortcut.replace(" ", "")[-2] if shortcut.replace(" ", "")[-2] else None
    )
    has_trailing_plus = shortcut.rstrip().endswith("+") and second_to_last != "+"

    return has_leading_plus or has_trailing_plus


def _has_duplicate_keys(keys: list[str]) -> bool:
    """cannot use a key combination with multiple of the same key in it"""
    # Should also check that you do not enter something like "Option + Alt" or "Ctrl + Command" as these are physically still duplicate keys
    keys_normed_names = [
        MODIFIER_SYNONYMS.get(key.lower(), key.upper()) for key in keys
    ]
    number_unique_keys = len(set(keys_normed_names))
    number_of_entered_keys = len(keys)
    return number_of_entered_keys > number_unique_keys


def _has_modifier(keys: list[str]) -> bool:
    return any(key.lower() in MODIFIER_KEYS for key in keys)


def _has_multiple_non_modifiers(keys: list[str]) -> bool:
    """Qt does not allow for two non-modifiers (not: ctrl, alt, shift, meta) in a single key combination.

    for example, 'A+O' or 'Shift + 7 + D' are not valid key combinations.
    """
    return sum([key.lower() in NON_MODIFIER_KEYS for key in keys]) > 1
