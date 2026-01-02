"""
unit tests for app/configuration_manager.py
"""

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self, Type, cast

import pytest

from app.core.config_manager import ConfigManager


@dataclass
class User:
    """
    Mock the Config of a component controller: Use a combination of data types.
    """

    name: str
    age: int
    email: str
    height: float

    @classmethod
    def from_raw(cls: Type[Self], settings: dict[str, Any]) -> Self:
        """specify how to parse the dictionary of JSON / TOML data supplied. Allows the user to provide values in a more user-friendly manner."""
        return cls(**settings)


@dataclass
class Country:
    """
    Mock the Config of a component controller: Use a combination of data types.
    """

    name: str
    language: str

    @classmethod
    def from_raw(cls: Type[Self], settings: dict[str, Any]) -> Self:
        """specify how to parse the dictionary of JSON / TOML data supplied. Allows the user to provide values in a more user-friendly manner."""
        return cls(**settings)


@pytest.fixture
def config_data() -> dict[str, Any]:
    """mock JSON style data with sections"""
    json_data = {
        "user": {
            "name": "Joe",
            "age": 42,
            "height": 42.0,
            "email": "fake@emailprovider.com",
        },
        "country": {"name": "France", "language": "French"},
    }
    return json_data


def test_loading_from_file(config_data: dict[str, Any]) -> None:
    """test that registered configs get created properly. use some mix of different config types"""
    manager = ConfigManager()
    manager.register("user", User)
    manager.register("country", Country)

    with tempfile.NamedTemporaryFile(
        "w+", encoding="utf-8", suffix=".json"
    ) as temp_json:
        json.dump(config_data, temp_json)
        temp_json.flush()
        temp_json.seek(0)

        manager.load(Path(temp_json.name))

        user = cast(User, manager.get_config("user"))
        expected_user_data = config_data["user"]
        assert user.name == expected_user_data["name"]
        assert user.age == expected_user_data["age"]
        assert user.height == expected_user_data["height"]
        assert user.email == expected_user_data["email"]

        country = cast(Country, manager.get_config("country"))
        expected_country_data = config_data["country"]
        assert country.name == expected_country_data["name"]
        assert country.language == expected_country_data["language"]
