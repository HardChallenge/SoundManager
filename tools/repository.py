"""Module responsible with handling the database connection."""
import psycopg2
from .tables import Tables


class Repository:
    """
    A class which provides methods to interact with the database.

    Tables handled: Artist, Song, Tag, SongArtist, SongTag
    """

    QUERY = 0
    COMMAND = 1

    def __init__(self, connection: dict):
        """
        Initializes the Repository class.

            - connection: dict - a dictionary containing the connection parameters

        Keys: host, port, database, user, password
        Returns: None
        """
        self.conn = self.try_connection(**connection)
        if self.conn is None:
            raise Exception("Connection failed.")

    def try_connection(self, **kwargs) -> psycopg2.connect:
        """
        Tries to connect to the database.

                - kwargs: dict - a dictionary containing the connection parameters

        Keys: host, port, database, user, password
        Returns: None | psycopg2.connection - the connection object or None if the connection failed
        """
        conn = psycopg2.connect(**kwargs)
        return conn

    def close_connection(self) -> None:
        """Closes the connection to the database."""
        self.conn.close()

    def clear_tables(self) -> None:
        """Deletes all the tables from the database if they exist."""
        cursor = self.conn.cursor()
        table_names = ["Artist", "Song", "Tag", "SongArtist", "SongTag"]

        for table_name in table_names:
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')

        cursor.close()
        self.conn.commit()

    def create_tables(self) -> None:
        """Creates all the tables in the database."""
        cursor = self.conn.cursor()

        for table in Tables.fetch_templates():
            cursor.execute(table)

        cursor.close()
        self.conn.commit()

    def execute(self, command: str, type: int, fetchall: bool = True) -> list:
        """
        Executes a command or a query on the database.

            - command: str - the command to be executed
            - type: int - the type of the command (Repository.COMMAND or Repository.QUERY)
            - fetchall: bool - whether to fetch all the results or not (default: True)

        Returns: list - the result of the command or query
        """
        cursor = self.conn.cursor()
        cursor.execute(command)
        result = cursor.fetchall() if fetchall else None
        cursor.close()
        if type == Repository.COMMAND:
            self.conn.commit()

        return result

    def delete_song(self, param: str, data) -> None:
        """
        Deletes a song from the database by a given parameter.

            - param: str - the parameter to search by
            - data: any - the value of the parameter

        Returns: None
        """
        try:
            command = 'DELETE FROM "Song" WHERE {} = {}'.format(param, data)
            self.execute(command, Repository.COMMAND, fetchall=False)
        except psycopg2.Error as e:
            raise psycopg2.Error(f"Deleting song by {param} failed, error: {e}")

    def create_artist(self, artist: str) -> int:
        """
        Tries to fetch an artist from the database. If it doesn't exist, creates it.

              - artist: str - the name of the artist to be created

        Returns: int - the id of the artist from the database
        """
        result = self.fetch_artist_id(artist)
        if result == -1:
            command = "INSERT INTO \"Artist\" (name) VALUES ('{}') RETURNING id".format(
                artist
            )
            result = self.execute(command, Repository.COMMAND)
            return result[0][0]
        return result

    def create_tag(self, tag: str) -> int:
        """
        Tries to fetch a tag from the database. If it doesn't exist, creates it.

            - tag: str - the name of the tag to be created

        Returns: int - the id of the tag from the database
        """
        result = self.fetch_tag_id(tag)
        if result == -1:
            command = "INSERT INTO \"Tag\" (name) VALUES ('{}') RETURNING id".format(
                tag
            )
            result = self.execute(command, Repository.COMMAND)
            return result[0][0]
        return result

    def create_song_artists(self, song_id: int, artists_id: list) -> None:
        """
        Creates the relations between a song and its artists.

            - song_id: int - the id of the song
            - artists_id: list - the list of ids of the artists

        Returns: None
        """
        if len(artists_id) == 0:
            return None
        command = 'INSERT INTO "SongArtist" (songId, artistId) VALUES '
        for artist_id in artists_id:
            command += f"({song_id}, {artist_id}),"
        command = command[:-1]
        command += " RETURNING id"
        self.execute(command, Repository.COMMAND)

    def create_song_tags(self, song_id: int, tags_id: list) -> None:
        """
        Creates the relations between a song and its tags.

            - song_id: int - the id of the song
            - tags_id: list - the list of ids of the tags

        Returns: None
        """
        if len(tags_id) == 0:
            return
        command = 'INSERT INTO "SongTag" (songId, tagId) VALUES '
        for tag_id in tags_id:
            command += f"({song_id}, {tag_id}),"
        command = command[:-1]
        command += " RETURNING id"
        self.execute(command, Repository.COMMAND)

    def fetch_artist_id(self, artist: str) -> int:
        """
        Tries to fetch an artist from the database.

            - artist: str - the name of the artist to be fetched

        Returns: int - the id of the artist from the database or -1 if it doesn't exist
        """
        query = "SELECT * FROM \"Artist\" WHERE name = '{}'".format(artist)
        result = self.execute(query, Repository.QUERY)
        if len(result) == 0:
            return -1
        else:
            return result[0][0]

    def fetch_tag_id(self, tag: str) -> int:
        """
        Tries to fetch a tag from the database.

            - tag: str - the name of the tag to be fetched

        Returns: int - the id of the tag from the database or -1 if it doesn't exist
        """
        query = "SELECT * FROM \"Tag\" WHERE name = '{}'".format(tag)
        result = self.execute(query, Repository.QUERY)
        if len(result) == 0:
            return -1
        else:
            return result[0][0]

    def fetch_song_data(self, song_id: int) -> tuple:
        """
        Fetches the data of a song from the database.

            - song_id: int - the id of the song to be fetched

        Returns a tuple containing (filePath, name, releaseDate, format, [artists], [tags]).
        """

        query = 'SELECT filepath, name, releasedate, format from "Song" WHERE id = {}'.format(
            song_id
        )
        result = self.execute(query, Repository.QUERY)

        filePath, name, releaseDate, format = result[0]

        query = 'SELECT "Artist".name from "Artist" \
            join "SongArtist" on "Artist".id = "SongArtist".artistid \
            WHERE "SongArtist".songid = {}'.format(
            song_id
        )

        result = self.execute(query, Repository.QUERY)
        artists = [item[0] for item in result]

        query = 'SELECT "Tag".name from "Tag" \
            join "SongTag" on "Tag".id = "SongTag".tagid \
            WHERE "SongTag".songid = {}'.format(
            song_id
        )
        result = self.execute(query, Repository.QUERY)
        tags = [item[0] for item in result]

        return filePath, name, releaseDate, format, artists, tags

    def create_song_tag(self, song_id: int, tag: str) -> int:
        """
        Creates a relation between a song and a tag in the 'SongTag' table.

            - song_id: int - the id of the song
            - tag: str - the name of the tag

        Returns: int - the id of the relation
        """
        tag_id = self.fetch_tag_id(tag)
        if tag_id == -1:
            tag_id = self.create_tag(tag)

        command = 'INSERT INTO "SongTag" (songid, tagid) SELECT {}, {} WHERE NOT EXISTS (SELECT 1 FROM "SongTag" WHERE songId = {} AND tagId = {}) RETURNING id'.format(
            song_id, tag_id, song_id, tag_id
        )

        return self.execute(command, Repository.COMMAND)

    def create_song_artist(self, song_id: int, artist: str) -> int:
        """
        Creates a relation between a song and an artist in the 'SongArtist' table.

            - song_id: int - the id of the song
            - artist: str - the name of the artist

        Returns: int - the id of the relation
        """
        artist_id = self.fetch_artist_id(artist)
        if artist_id == -1:
            artist_id = self.create_artist(artist)

        command = 'INSERT INTO "SongArtist" (songid, artistid) SELECT {}, {} WHERE NOT EXISTS (SELECT 1 FROM "SongArtist" WHERE songId = {} AND artistId = {}) RETURNING id'.format(
            song_id, artist_id, song_id, artist_id
        )

        return self.execute(command, Repository.COMMAND)

    def update_song(self, song_id: int, data: dict) -> None:
        """
        Updates a song from the database.

            - song_id: int - the id of the song to be updated
            - data: dict - the data to be updated

        Keys: newName, newReleaseDate, newFormat
        Returns: None
        """
        setters = []
        if data["newName"]:
            setters.append(f"name = '{data['newName']}'")
        if data["newReleaseDate"]:
            setters.append(f"releaseDate = '{data['newReleaseDate']}'")
        if data["newFormat"]:
            setters.append(f"format = '{data['newFormat']}'")

        command = 'UPDATE "Song" SET {} WHERE id = {} RETURNING id'.format(
            ", ".join(setters), song_id
        )
        self.execute(command, Repository.COMMAND)
