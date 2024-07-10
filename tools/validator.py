"""Module responsible for validating the json files needed by the application."""
import os
import json
from datetime import datetime
from common import extensions


class Validator:
    """A class which provides static methods to validate the json files."""

    @staticmethod
    def _check_file(path: str) -> bool:
        """
        Checks if the path is a file and can be read.

            - path: str - the path to the file

        Returns: bool - True if the path has the required properties, False otherwise
        """
        return (
            os.path.exists(path) and os.path.isfile(path) and os.access(path, os.R_OK)
        )

    @staticmethod
    def _check_dir(path: str) -> bool:
        """
        Checks if the path is a directory.

            - path: str - the path to the directory

        Returns: bool - True if the path has the required properties, False otherwise
        """
        return os.path.exists(path) and os.path.isdir(path)

    @staticmethod
    def validate_appsettings(jsonPath: str) -> dict:
        """
        Validates the appsettings.json file.

            - jsonPath: str - the path to appsettings.json file

        Returns: dict - the dictionary with the data if successful, raises an exception otherwise
        """
        valid_keys = {"storage", "logger", "restart", "connection"}
        data = Validator.primary_validator(jsonPath, valid_keys)

        valid_connection_keys = {"host", "user", "password", "database", "port"}
        if valid_connection_keys != set(data["connection"].keys()):
            raise TypeError(
                f"Required keys in appsetings(db connection) are {valid_connection_keys}"
            )

        exclude_values = {data["restart"], data["connection"]["port"]}
        string_only = {data["storage"], data["logger"]} | set(
            data["connection"].values()
        ) - exclude_values
        if not all(isinstance(value, str) for value in string_only):
            raise TypeError("All values besides 'restart' must be strings.")

        if not isinstance(data["restart"], bool):
            raise TypeError("Restart value must be a boolean.")

        if not isinstance(data["connection"]["port"], int):
            raise TypeError("Port value must be an integer.")

        if not Validator._check_dir(data["storage"]):
            raise TypeError("Storage path doesn't exist or it's not a directory.")

        if not Validator._check_file(data["logger"]):
            raise TypeError(
                "Logger path doesn't exist or it's not a file or can't be read."
            )

        return data

    @staticmethod
    def validate_create(jsonPath: str) -> dict:
        """
        Validates the json file for 'create' command.

            - jsonPath: str - the path to create options json file

        Returns: dict - the dictionary with the data if successful, raises an exception otherwise
        """
        valid_keys = {
            "filePath",
            "name",
            "format",
            "releaseDate",
            "artists",
            "tags",
            "auto",
        }
        data = Validator.primary_validator(jsonPath, valid_keys)

        if not isinstance(data["artists"], list):
            raise TypeError("Artists value must be a list.")
        if len(data["artists"]) == 0:
            raise ValueError("Songs must have at least one artist.")

        if not isinstance(data["tags"], list):
            raise TypeError("Tags value must be a list.")

        string_only = {
            data["filePath"],
            data["name"],
            data["format"],
            data["releaseDate"],
        }

        string_only.update(set(data["artists"]), set(data["tags"]))
        if not all(isinstance(value, str) for value in string_only):
            raise TypeError("All values except 'auto' must be strings.")

        if not Validator._check_file(data["filePath"]):
            raise TypeError(
                f"File {data['filePath']} not found or it's not a file or can't be read."
            )

        if data["format"] not in extensions.SUPPORTED_FORMATS:
            raise ValueError(f"Format {data['format']} is not supported.")

        if not isinstance(data["auto"], bool):
            raise TypeError("Auto value must be a boolean.")

        try:
            datetime.strptime(data["releaseDate"], "%Y-%m-%d")
        except Exception as e:
            raise TypeError(
                f"Format date needs to be YEAR-MONTH-DAY ({str(e).strip()})"
            )

        return data

    @staticmethod
    def validate_delete(jsonPath: str) -> dict:
        """
        Validates the json file for 'delete' command.

            - jsonPath: str - the path to delete options json file

        Returns: dict - the dictionary with the data if successful, raises an exception otherwise
        """
        valid_keys = {"id"}
        data = Validator.primary_validator(jsonPath, valid_keys)

        if not isinstance(data["id"], int):
            raise TypeError("Id value must be an integer.")

        if data["id"] < 0:
            raise ValueError("Id value must be a positive integer.")

        return data

    @staticmethod
    def validate_update(jsonPath: str) -> dict:
        """
        Validates the json file for 'update' command.

            - jsonPath: str - the path to update options json file

        Returns: dict - the dictionary with the data if successful, raises an exception otherwise
        """
        valid_keys = {
            "id",
            "newName",
            "newFormat",
            "newReleaseDate",
            "newArtists",
            "newTags",
        }
        data = Validator.primary_validator(jsonPath, valid_keys)

        if not isinstance(data["newArtists"], list):
            raise TypeError("Artists value must be a list.")

        if not isinstance(data["newTags"], list):
            raise TypeError("Tags value must be a list.")

        string_only = {data["newName"], data["newFormat"], data["newReleaseDate"]}
        string_only.update(set(data["newArtists"]), set(data["newTags"]))
        if not all(isinstance(value, str) for value in string_only):
            raise TypeError("All values beside 'id' must be strings.")

        if not isinstance(data["id"], int):
            raise TypeError("Id value must be an integer.")

        if data["id"] < 0:
            raise ValueError("Id value must be a positive integer.")

        if (
            data["newFormat"] != ""
            and data["newFormat"] not in extensions.SUPPORTED_FORMATS
        ):
            raise ValueError(f"Format {data['newFormat']} is not supported.")

        try:
            datetime.strptime(data["newReleaseDate"], "%Y-%m-%d") if data[
                "newReleaseDate"
            ] else None
        except Exception as e:
            raise TypeError(
                f"Format date needs to be YEAR-MONTH-DAY ({str(e).strip()})"
            )

        return data

    @staticmethod
    def validate_search(jsonPath: str) -> dict:
        """
        Validates the json file for 'search' command.

            - jsonPath: str - the path to search options json file

        Returns: dict - the dictionary with the data if successful, raises an exception otherwise
        """
        valid_keys = {"name", "format", "releaseDate", "artists", "tags"}
        data = Validator.primary_validator(jsonPath, valid_keys)

        list_only = [data["releaseDate"], data["artists"], data["tags"]]
        if not all(isinstance(value, list) for value in list_only):
            raise TypeError("Release date, artists and tags must be lists.")

        string_only = {data["name"], data["format"]}
        string_only.update(
            set(data["artists"]), set(data["tags"]), set(data["releaseDate"])
        )
        if not all(isinstance(value, str) for value in string_only):
            raise TypeError("All values must be strings.")

        if len(data["releaseDate"]) > 2:
            raise ValueError("Release date can't have more than 2 values.")

        try:
            for date in data["releaseDate"]:
                datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"Format date needs to be YEAR-MONTH-DAY ({str(e).strip()})"
            )

        return data

    @staticmethod
    def validate_play(jsonPath: str) -> dict:
        """
        Validates the json file for 'play' command.

            - jsonPath: str - the path to play options json file

        Returns: dict - the dictionary with the data if successful, raises an exception otherwise
        """
        valid_keys = {"songId"}
        data = Validator.primary_validator(jsonPath, valid_keys)

        if not isinstance(data["songId"], int):
            raise TypeError("SongId must be an integer.")

        return data

    @staticmethod
    def primary_validator(jsonPath: str, valid_keys: set) -> dict:
        """
        Checks if the json file is accessible and has the required keys.

                - jsonPath: str - the path to the json file
                - valid_keys: set - the set of required keys

        Returns: dict - the dictionary with the data if successful, raises an exception otherwise
        """

        if not Validator._check_file(jsonPath):
            raise TypeError(
                f"File {jsonPath} not found or it's not a file or can't be read."
            )

        with open(jsonPath, "r") as file:
            data = json.loads(file.read())

        if valid_keys != set(data.keys()):
            raise TypeError(f"Required keys for command are {valid_keys}")

        return data
