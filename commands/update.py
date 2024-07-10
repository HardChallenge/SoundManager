"""Module responsible for the update command."""
from tools.repository import Repository
from tools.validator import Validator


class Update:
    """A class which provides static methods to update a song from the database."""

    @staticmethod
    def serve(jsonPath: str, repository: Repository) -> None:
        """
        Serves the update command, defining the logic behind it.

            - jsonPath: str - the path to update options json file
            - repository: Repository - the repository object

        Returns: None
        """
        data = Validator.validate_update(jsonPath)

        query = 'SELECT 1 FROM "Song" WHERE id = {}'.format(data["id"])
        if not repository.execute(query, Repository.QUERY):
            raise ValueError(f"Song with id {data['id']} does not exist.")

        repository.update_song(data["id"], data)
        for artist in data["newArtists"]:
            repository.create_song_artist(data["id"], artist)

        for tag in data["newTags"]:
            repository.create_song_tag(data["id"], tag)

    @staticmethod
    def help() -> str:
        """Returns the help message for the update command."""
        return "   > update <path-to-json> => Updates a song from the repository"
