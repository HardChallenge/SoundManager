"""Module responsible with checking if a file exists in the storage."""
import os


class Checker:
    """A class which provides static methods to check if a file exists in the storage."""

    @staticmethod
    def check_file_existence(file_path: str, storage_path: str) -> bool:
        """
        Checks if the file exists in the storage folder.

            - file_path: str - the path to the file
            - storage_path: str - the path to the storage folder

        Returns: bool - True if the file exists, False otherwise
        """
        file_name = os.path.basename(file_path)
        return os.path.exists(os.path.join(storage_path, file_name))
