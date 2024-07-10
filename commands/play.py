"""Module responsible for the play command. Uses a combination of pydub and simpleaudio to play the song."""
import simpleaudio
import subprocess
import mimetypes
import os
from pydub import AudioSegment
from tools.repository import Repository
from tools.validator import Validator


class Play:
    """A class which provides static methods to play a song from the storage."""

    @staticmethod
    def serve(jsonPath: str, repository: Repository) -> None:
        """
        Serves the play command, defining the logic behind it.

            - jsonPath: str - the path to play options json file
            - repository: Repository - the repository object

        Returns: None
        """
        data = Validator.validate_play(jsonPath)

        query = 'SELECT * from "Song" WHERE id = {}'.format(data["songId"])
        result = repository.execute(query, Repository.QUERY)
        if len(result) == 0:
            raise ValueError(f"Song with id {data['songId']} does not exist.")

        filePath = result[0][1]
        os.system(f"open {filePath}")
        # try:
        #     sound = AudioSegment.from_file(
        #         filePath,
        #         format=fmt,
        #     )
        #     play_obj = simpleaudio.play_buffer(
        #         sound.raw_data,
        #         num_channels=sound.channels,
        #         bytes_per_sample=sound.sample_width,
        #         sample_rate=sound.frame_rate,
        #     )
        #     input("Press enter to stop playing...")
        #     play_obj.stop()
        # except Exception as err:
        #     raise ValueError(f"Error while playing song: {err}")

    @staticmethod
    def help() -> str:
        """Returns the help message for the play command."""
        return "   > play <path-to-json> => Plays a song from the storage folder"
