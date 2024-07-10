"""Module which defines the templates for the tables in the database.""" ""


class Tables:
    """A class which provides static methods to fetch the templates for the tables in the database."""

    @staticmethod
    def fetch_templates() -> list[str]:
        """Returns a list of strings which represent the templates for the tables in the database."""
        return [
            Tables._create_song(),
            Tables._create_artist(),
            Tables._create_tag(),
            Tables._create_song_artist(),
            Tables._create_song_tag(),
        ]

    @staticmethod
    def _create_song() -> str:
        """Returns the template for the Song table."""
        return """
            CREATE TABLE IF NOT EXISTS "Song" (
                id SERIAL PRIMARY KEY,
                filePath VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                releaseDate DATE NOT NULL,
                format VARCHAR(255) NOT NULL
            )
        """

    @staticmethod
    def _create_artist() -> str:
        """Returns the template for the Artist table."""
        return """
            CREATE TABLE IF NOT EXISTS "Artist" (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        """

    def _create_tag() -> str:
        """Returns the template for the Tag table."""
        return """
            CREATE TABLE IF NOT EXISTS "Tag" (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        """

    def _create_song_artist() -> str:
        """Returns the template for the SongArtist table."""
        return """
            CREATE TABLE IF NOT EXISTS "SongArtist" (
                id SERIAL PRIMARY KEY,
                songId INTEGER NOT NULL,
                artistId INTEGER NOT NULL,
                FOREIGN KEY (songId) REFERENCES "Song"(id) ON DELETE CASCADE,
                FOREIGN KEY (artistId) REFERENCES "Artist"(id) ON DELETE CASCADE
            )
        """

    def _create_song_tag() -> str:
        """Returns the template for the SongTag table."""
        return """
            CREATE TABLE IF NOT EXISTS "SongTag" (
                id SERIAL PRIMARY KEY,
                songId INTEGER NOT NULL,
                tagId INTEGER NOT NULL,
                FOREIGN KEY (songId) REFERENCES "Song"(id) ON DELETE CASCADE,
                FOREIGN KEY (tagId) REFERENCES "Tag"(id) ON DELETE CASCADE
            )
        """
