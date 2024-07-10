"""Module for the search command."""
from tools.repository import Repository
from tools.validator import Validator


class Search:
    """A class which provides static methods to search for a song in the database."""

    @staticmethod
    def serve(jsonPath: str, repository: Repository) -> list[tuple]:
        """
        Serves the search command, defining the logic behind it.

            - jsonPath: str - the path to search options json file
            - repository: Repository - the repository object

        Returns: list[tuple] - the list of songs found
        """
        data = Validator.validate_search(jsonPath)

        query = 'SELECT id from "Song"'
        result = repository.execute(query, Repository.QUERY)

        song_ids = set([item[0] for item in result])
        song_by_artists = Search.search_by_artists(data["artists"], repository)
        song_by_tags = Search.search_by_tags(data["tags"], repository)
        song_by_metadata = Search.search_by_metadata(data, repository)

        song_by_artists, song_by_tags, song_by_metadata = [
            item if item != None else song_ids
            for item in [song_by_artists, song_by_tags, song_by_metadata]
        ]

        search_results_ids = (
            song_ids & song_by_artists & song_by_tags & song_by_metadata
        )

        data = []
        for id in search_results_ids:
            song = repository.fetch_song_data(id)
            data.append(song)

        return data

    @staticmethod
    def search_by_artists(artists: list[str], repository: Repository) -> set[int]:
        """
        Searches for the songs which have ALL the artists from the 'artists' list.
        Due to pattern matching, an 'artist' can be only a substring of the actual artist name.

            - artists: list[str] - the list of artists to search for
            - repository: Repository - the repository object

        Returns: set[int] | None - the set of ids of the songs found or None if the 'artists' list is empty
        """

        if not artists:
            return None

        condition = [f"'%{artist.lower()}%'" for artist in artists]
        search_condition = ",".join(condition)
        query = 'SELECT "Song".id from "Song" \
            join "SongArtist" on "Song".id = "SongArtist".songid \
            join "Artist" on "SongArtist".artistid = "Artist".id \
            WHERE LOWER("Artist".name) LIKE ANY(ARRAY[{}]) GROUP BY "Song".id HAVING COUNT(DISTINCT "Artist".id) = {}'.format(
            search_condition, len(artists)
        )

        result = repository.execute(query, Repository.QUERY)
        if not result:
            return set()
        else:
            return set([item[0] for item in result])

    @staticmethod
    def search_by_tags(tags: list[str], repository: Repository) -> set[int]:
        """
        Searches for the songs which have ALL the tags from the 'tags' list.

            - tags: list[str] - the list of tags to search for
            - repository: Repository - the repository object

        Returns: set[int] | None - the set of ids of the songs found or None if the 'tags' list is empty
        """

        if not tags:
            return None

        condition = [f"'%{tag.lower()}%'" for tag in tags]
        search_condition = ",".join(condition)
        query = 'SELECT "Song".id from "Song" \
            join "SongTag" on "Song".id = "SongTag".songid \
            join "Tag" on "SongTag".tagid = "Tag".id \
            WHERE LOWER("Tag".name) LIKE ANY (ARRAY[{}]) GROUP BY "Song".id HAVING COUNT(DISTINCT "Tag".id) = {}'.format(
            search_condition, len(tags)
        )

        result = repository.execute(query, Repository.QUERY)
        if not result:
            return set()

        return set([item[0] for item in result])

    @staticmethod
    def search_by_metadata(metadata: dict, repository: Repository) -> set[int]:
        """
        Searches for the songs which have the metadata from the 'metadata' dictionary.

            - metadata: dict - the dictionary containing the metadata to search for
            - repository: Repository - the repository object

        Returns: set[int] | None - the set of ids of the songs found or None if the 'metadata' dictionary does not
        contain the keys 'name', 'format' and 'releaseDate'
        """
        if (
            not metadata["name"]
            and not metadata["format"]
            and not metadata["releaseDate"]
        ):
            return None

        where_condition = []
        if metadata["name"]:
            where_condition.append(
                f'LOWER("Song".name) LIKE \'%{metadata["name"].lower()}%\''
            )

        if metadata["format"]:
            where_condition.append(
                f'LOWER("Song".format) LIKE \'%{metadata["format"].lower()}%\''
            )

        if metadata["releaseDate"]:
            if len(metadata["releaseDate"]) == 1:
                where_condition.append(
                    f'"Song".releaseDate = \'{metadata["releaseDate"][0]}\''
                )
            else:
                where_condition.append(
                    f'"Song".releaseDate BETWEEN \'{metadata["releaseDate"][0]}\' AND \'{metadata["releaseDate"][1]}\''
                )

        query = 'SELECT id from "Song" WHERE {}'.format(" AND ".join(where_condition))
        result = repository.execute(query, Repository.QUERY)
        if not result:
            return set()

        return set([item[0] for item in result])

    @staticmethod
    def help() -> str:
        """Returns the help message for the search command."""
        return "   > search <path-to-json> => Searches for a song in the database"
