"""This module is reponsible for the archive command. It allows the user to archive songs from the storage folder."""

import re
from zipfile import ZipFile
import string
import secrets
from commands.search import Search
from tools.repository import Repository


class Archive:
    """A class which provides static methods to archive the songs from the storage."""

    @staticmethod
    def serve(jsonPath: str, repository: Repository, storage: str) -> str:
        """
        Serves the archive command, defining the logic behind it.

            - jsonPath: str - the path to archive options json file
            - repository: Repository - the repository object
            - storage: str - the path to the storage folder

        Returns: str - the name of the archive created
        """

        songs = Search.serve(jsonPath, repository)

        if not songs:
            raise ValueError("No songs found.")

        print(Archive.display_songs(songs))

        overlapping = True
        while overlapping:
            command = input().strip()
            while not Archive.command_matches(command):
                print(
                    "Invalid command. Syntax: Opt,Opt,... where Opt = <number> or <number>..<number>"
                )
                command = input().strip()

            intervals = Archive.parse_command(command)
            if Archive.intervals_overlap(intervals):
                print("Overlapping intervals. Try again.")
            else:
                overlapping = False

        archive_name = Archive.archive_songs(songs, intervals, storage)
        print(f"Archive created successfully. Name: {archive_name}")

    @staticmethod
    def archive_songs(songs: list[tuple], intervals: list[tuple], storage: str) -> str:
        """
        Archive the songs from 'songs' list after applying the intervals from 'intervals' and place them in the 'storage' folder.

            - songs: list[tuple] - the list of songs to archive
            - intervals: list[tuple] - the list of intervals to archive the songs
            - storage: str - the path to the storage folder

        Returns: str - the name of the archive created
        """

        songs_to_archive = []
        for interval in intervals:
            songs_to_archive.extend(songs[interval[0] : interval[1]])

        archive_name = Archive.generate_random_name()
        with ZipFile(f"{storage}/{archive_name}.zip", "w") as archive:
            for song in songs_to_archive:
                archive.write(song[0], arcname=song[0].rsplit("/", 1)[1])

        return archive_name

    @staticmethod
    def generate_random_name(length: int = 8) -> str:
        """
        Returns random name with the specified length.

            - length: int - the length of the name to generate (optional)

        Returns: str - the random name generated
        """
        characters = string.ascii_letters + string.digits
        random_name = "".join(secrets.choice(characters) for _ in range(length))
        return random_name

    @staticmethod
    def intervals_overlap(intervals: list[tuple]) -> bool:
        """
        Checks if the intervals from 'intervals' list overlap.

            - intervals: list[tuple] - the list of intervals to check

        Returns: bool - True if the intervals overlap, False otherwise
        """
        intervals.sort(key=lambda item: item[0])
        for i in range(len(intervals) - 1):
            _, end1 = intervals[i]
            start2, _ = intervals[i + 1]

            if start2 + 1 <= end1:
                return True

        return False

    @staticmethod
    def parse_command(command: str) -> list[tuple]:
        """
        Parses the command and returns a list of intervals based on the following syntax: Opt,Opt,... where Opt = <number> or <number>..<number>

            - command: str - the command to parse

        Returns: list[tuple] - the list of intervals parsed
        """
        result = []
        for option in command.split(","):
            if ".." in option:
                start, end = option.split("..")
                start, end = int(start) - 1, int(end)
                result.append((start, end))
            else:
                result.append((int(option) - 1, int(option)))
        return result

    @staticmethod
    def display_songs(songs: list[tuple]) -> str:
        """
        Creates a help message for the archive command based on the songs from 'songs' list.

            - songs: list[tuple] - the list of songs to display

        Returns: str - the help message created
        """
        result = ["Choose what songs to archive:"]
        index = 0
        while index < len(songs):
            result.append(f"{index + 1}. {songs[index][1]} by {songs[index][4]}")
            index += 1

        return "\n".join(result)

    @staticmethod
    def command_matches(command: str) -> bool:
        """
        Checks if the command matches the following syntax: Opt,Opt,... where Opt = <number> or <number>..<number>

            - command: str - the command to check

        Returns: bool - True if the command matches the syntax, False otherwise
        """

        option = r"([0-9]+|[0-9]+\.\.[0-9]+)"
        pattern = f"^{option}(,{option})*$"
        return re.match(pattern, command)

    @staticmethod
    def help() -> str:
        """Returns a help message for the archive command."""
        return "   > archive <path-to-json> => Archives songs from the storage folder"
