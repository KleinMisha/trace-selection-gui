"""
Managing Configuration settings
------
As a user, we want to adjust settings from a single configuration file
From the developer perspective / part of the code --> These should not need to know how values are stored/parsed. These should be able to receive a simple dataclass with all the relevant values for their individual components.
This class solves this cross-application concern.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, Self, Type


class Config(Protocol):
    """
    Configuration settings are simply dataclasses with some variables

    """

    @classmethod
    def from_raw(cls, settings: dict[str, Any]) -> Self:
        """specify how to parse the dictionary of JSON / TOML data supplied. Allows the user to provide values in a more user-friendly manner.

        NOTE: If the way things are entered in the config file matches exactly the fields of the dataclass, simply return cls(**settings)
        """
        ...


class ConfigWithShortcuts(Config, Protocol):
    """If configurations include keyboard shortcuts

    * implement the following API
    * only important for wiring things within the component's controller

    """

    def get_shortcuts(self) -> dict[Enum, str]:
        """dictionary of all keyboard shortcuts for this component"""
        ...


@dataclass
class ConfigManager:
    """
    Separates reading/writing configuration settings from file from parts of the code that need to access them.

    The ConfigManager turns the values in the file into easy useable (data)classes.
    """

    _registry: dict[str, Type[Config]] = field(default_factory=dict)
    _instances: dict[str, Config] = field(default_factory=dict)

    def register(self, name: str, config_class: Type[Config]) -> None:
        new_entry = {name: config_class}
        self._registry.update(new_entry)

    def get_config(self, name: str) -> Config:
        """hides implementation of a dictionary to outside"""
        return self._instances[name]

    def load(self, file_name: Path) -> None:
        """
        Read the file (JSON/TOML/etc.) and creates the individual configuration objects
        ---
        Assumes the config file has named sections (sub-dictionaries or tables) with values specific to particular components.
        """

        # read file: Specific for type of file
        with open(file_name, mode="r", encoding="utf-8") as f:
            config_values = json.load(f)

        # build the config objects: This is "all that other parts of the code need / want to know"
        for name, config in self._registry.items():
            new_entry = {name: config.from_raw(config_values[name])}
            self._instances.update(new_entry)

    def write(self, file_name: Path) -> None:
        """Save config to file for later use"""

        # rebuild the dictionary based on the config object(s)

        # write to file

        raise NotImplementedError
