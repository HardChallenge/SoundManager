"""This module contains the Handler class which defines the flow of information in the application."""
import psycopg2
import re
import shutil
import os
from queue import Queue

from tools.checker import Checker
from commands.create import Create
from commands.delete import Delete
from commands.update import Update
from commands.search import Search
from commands.archive import Archive
from commands.play import Play
from .validator import Validator
from .logger import Logger
from .repository import Repository


class Handler:
    """The main class which implements the logic of the application."""

    COMMANDS = [Create, Delete, Update, Search, Archive, Play]

    def __init__(self, appsettings: str):
        """
        Initializes the Handler class.

            - appsettings: str - the path to the appsettings.json file

        Returns: None
        """
        if not isinstance(appsettings, str):
            raise TypeError("appsettings must be a string")
        self._appsettings = appsettings

    def handle(self, command: str, jsonPath: str) -> None:
        """
        Handles the command received from the user.

            - command: str - the command received from the user
            - jsonPath: str - the path to the json file containing the command options

        Returns: None
        """
        try:
            match command.lower():
                case "create":
                    self.put_log("Create command received. Processing...", Logger.INFO)
                    id = Create.serve(jsonPath, self._repository, self._storage)
                    self.put_log(f"Song created successfully. ID: {id}", Logger.INFO)
                    self.print_result(None, id, command)

                case "delete":
                    self.put_log("Delete command received. Processing...", Logger.INFO)
                    Delete.serve(jsonPath, self._repository, self._storage)
                    self.put_log("Song deleted successfully.", Logger.INFO)
                    self.print_result(None, None, command)

                case "update":
                    self.put_log("Update command received. Processing...", Logger.INFO)
                    Update.serve(jsonPath, self._repository)
                    self.put_log("Song updated successfully.", Logger.INFO)
                    self.print_result(None, None, command)

                case "search":
                    self.put_log("Search command received. Processing...", Logger.INFO)
                    data = Search.serve(jsonPath, self._repository)
                    self.put_log("Search completed successfully.", Logger.INFO)
                    self.print_result(None, data, command)

                case "archive":
                    self.put_log("Archive command received. Processing...", Logger.INFO)
                    Archive.serve(jsonPath, self._repository, self._storage)
                    self.put_log("Songs archived successfully.", Logger.INFO)
                    self.print_result(None, None, command)

                case "play":
                    self.put_log("Play command received. Processing...", Logger.INFO)
                    Play.serve(jsonPath, self._repository)
                    self.put_log("Song played successfully.", Logger.INFO)
                    self.print_result(None, None, command)
                case _:
                    raise ValueError(f"Unknown command received ({command})")
        except Exception as err:
            err_msg = str(err).strip()
            self.put_log(err_msg, Logger.ERROR)
            self.print_result(err_msg, None, command)

    def start(self) -> None:
        """Starts the application by validating the settings and initializing the logger and database."""
        data = Validator.validate_appsettings(self._appsettings)

        self._log_queue = Queue()
        self._storage = data["storage"]

        self._repository = Repository(data["connection"])
        self.put_log("Repository initialized successfully.", Logger.INFO)

        self.refresh(data["restart"])
        self.sync_db()

        self._logger = Logger(data["logger"], self._log_queue)
        self._logger.start()

    def stop(self) -> None:
        """Stops the application by closing the database connection and stopping the logger."""
        self._repository.close_connection()
        self.put_log("Database connection closed successfully.", Logger.INFO)
        self.put_log("Handler is stopping...", Logger.INFO)
        self._logger.stop()

    def sync_db(self) -> bool:
        """Checks if the files from the DB exist in the storage folder, otherwise deletes them from the DB."""
        query = 'SELECT filepath FROM "Song"'
        result = self._repository.execute(query, Repository.QUERY)
        for row in result:
            if not Checker.check_file_existence(row[0], self._storage):
                self.put_log(
                    f"File {row[0]} from DB doesn't exist, deleting...", Logger.WARNING
                )
                self._repository.delete_song("filepath", f"'{row[0]}'")
        return True

    def refresh(self, restart: bool) -> None:
        """
        Refreshes the database and storage folder if requested.

            - restart: bool - whether to restart the database or not

        Returns: None
        """
        if restart:
            self.refresh_db()
            self.refresh_dir()

    def refresh_db(self) -> None:
        """Refreshes the database by clearing and recreating the tables."""
        self.put_log("Restarting database...", Logger.INFO)
        try:
            self._repository.clear_tables()
            self._repository.create_tables()
        except psycopg2.Error as e:
            err_msg = str(e).strip()
            raise psycopg2.Error(f"Database restart failed! {err_msg}")
        self.put_log("Database restarted successfully.", Logger.INFO)

    def refresh_dir(self) -> None:
        """Refreshes the storage folder by deleting and creating it."""
        self.put_log("Clearing storage folder...", Logger.INFO)
        try:
            shutil.rmtree(self._storage)
            os.mkdir(self._storage)
        except OSError as e:
            err_msg = str(e).strip()
            raise OSError(f"Storage clearing failed! {err_msg}")
        self.put_log("Storage cleared successfully.", Logger.INFO)

    def put_log(self, msg: str, level: int) -> None:
        """
        Puts a log message in the queue for the logger to process.

            - msg: str - the message to log
            - level: int - the level of the message

        Returns: None
        """
        self._log_queue.put((msg, level))

    def valid_command(self, command: str) -> tuple[bool, list]:
        """
        Checks if the command from the user is valid or not.

            - command: str - the command received from the user

        Returns: tuple[bool, list] - a tuple containing the validity of the command and the data
        """
        if len((data := re.split(r"\s+", command))) == 2:
            self.put_log(f"Command received ({command}). Processing...", Logger.INFO)
            return (True, data)
        else:
            self.put_log(
                f"Invalid command received ({command}). Returning...", Logger.WARNING
            )
            return (False, data)

    def print_result(self, err: str, data, command: str) -> None:
        """
        Prints the result of the command after execution.

            - err: str - the error message if an error occured
            - data: any - the data to print
            - command: str - the command received from the user

        Returns: None
        """
        match command:
            case "create":
                if err:
                    print(f"Error occured while creating. {err}")
                else:
                    print(f"Song created successfully. ID: {data}")
            case "delete":
                if err:
                    print(f"Error occured while deleting. {err}")
                else:
                    print("Song deleted successfully.")
            case "update":
                if err:
                    print(f"Error occured while updating. {err}")
                else:
                    print("Song updated successfully.")
            case "search":
                if err:
                    print(f"Error occured while searching. {err}")
                else:
                    print("Search completed successfully.\n --------------------------")
                    for song in data:
                        print(f"> name: {song[1]}")
                        print(f"> releaseDate: {song[2]}")
                        print(f"> format: {song[3]}")
                        print(f"> artists: {song[4]}")
                        print(f"> tags: {song[5]}\n --------------------------")
            case "archive":
                if err:
                    print(f"Error occured while archiving. {err}")
                else:
                    print(
                        "Songs archived successfully. Please check the storage folder."
                    )
            case "play":
                if err:
                    print(f"Error occured while playing. {err}")
                else:
                    print("Song played successfully.")
            case _:
                print(f"Unknown command received ({command})")

    def help(self) -> str:
        """Returns the help message for the application."""
        result = []
        for command in Handler.COMMANDS:
            result.append(command.help())
        return "\n".join(result)
