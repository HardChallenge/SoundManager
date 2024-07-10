"""Module responsible for the create command."""
import re
import os
import shutil
from tools.validator import Validator
from tools.repository import Repository
from tools.checker import Checker
from datetime import datetime
from common import extensions


class Create:
    """A class which provides static methods to create a new song in the storage and database."""

    @staticmethod
    def serve(jsonPath: str, repository: Repository, storage: str) -> int:
        """
        Serves the create command, defining the logic behind it.

            - jsonPath: str - the path to create options json file
            - repository: Repository - the repository object
            - storage: str - the path to the storage folder

        Returns: int - the id of the song created
        """

        raw_data = Validator.validate_create(jsonPath)

        data = (
            Create._fetch_from_path(raw_data["filePath"], raw_data["tags"])
            if raw_data["auto"]
            else raw_data
        )

        if Checker.check_file_existence(data["filePath"], storage):
            raise ValueError(f"File {data['filePath']} already exists in storage.")

        storage_file = os.path.join(storage, data["filePath"].rsplit("/", 1)[1])

        command = "INSERT INTO \"Song\" (filepath, name, releasedate, format) VALUES ('{}', '{}', '{}', '{}') RETURNING id".format(
            storage_file, data["name"], data["releaseDate"], data["format"]
        )

        result = repository.execute(command, Repository.COMMAND)

        song_id = result[0][0]
        artists_id = [repository.create_artist(artist) for artist in data["artists"]]
        tags_id = [repository.create_tag(tag) for tag in data["tags"]]

        repository.create_song_artists(song_id, artists_id)
        repository.create_song_tags(song_id, tags_id)

        shutil.copy(data["filePath"], storage)

        return song_id

    @staticmethod
    def _fetch_from_path(path: str, tags: list) -> dict:
        """
        Fetches the data from the path of the song (only if the auto option is set to true).
        The path must be in the following format: <artist1>,<artist2>,...,<artistN>-<name>.<format>

            - path: str - the path to the song
            - tags: list - the list of tags to add to the song

        Returns: dict - the data fetched from the path
        """

        file_name = path.rsplit("/", 1)[1]
        word = r"[a-zA-Z0-9]+"
        if not re.match(f"^{word}(,{word})*-{word}\.{word}$", file_name):
            raise ValueError(f"Invalid format on file {file_name}")

        artists_bound, title_bound = file_name.index("-"), file_name.index(".")
        artists = file_name[:artists_bound].split(",")
        name = file_name[artists_bound + 1 : title_bound]
        format = file_name[title_bound + 1 :]

        created_at = datetime.fromtimestamp(os.path.getctime(path))
        releaseDate = created_at.strftime("%Y-%m-%d")

        if format not in extensions.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format {format}")

        result = {
            "filePath": path,
            "name": name,
            "format": format,
            "releaseDate": releaseDate,
            "artists": artists,
            "tags": tags,
            "auto": True,
        }

        return result

    @staticmethod
    def help() -> str:
        """Returns a help message for the create command."""
        return "   > create <path-to-json> => Creates a new song in the storage and database"
