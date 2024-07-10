"""Module responsible for the delete command."""
import os
from tools.repository import Repository
from tools.validator import Validator


class Delete:
    """A class which provides static methods to delete a song from the storage and database."""

    @staticmethod
    def serve(jsonPath: str, repository: Repository) -> None:
        """
        Serves the delete command, defining the logic behind it.

            - jsonPath: str - the path to delete options json file
            - repository: Repository - the repository object

        Returns: None
        """
        data = Validator.validate_delete(jsonPath)

        command = 'SELECT filepath FROM "Song" WHERE id = {}'.format(data["id"])
        filePath = repository.execute(command, Repository.COMMAND)
        if len(filePath) == 0:
            raise ValueError(f"Song with id {data['id']} does not exist.")

        repository.delete_song("id", data["id"])
        os.remove(filePath[0][0])

    @staticmethod
    def help() -> str:
        """Returns the help message for the delete command."""
        return "   > delete <path-to-json> => Deletes a song from the repository"
