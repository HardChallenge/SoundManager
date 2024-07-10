**DESCRIPTION**

_SongStorage_ is a tool which can store different songs in a pre-defined folder named "storage" and perform CRUD operations with metadata on PostgreSQL database tables. It comes also with a logger which executes asynchronously and stores all the events in the "logger" file.

Commands available: create, delete, update, search, archive, play

**REQUIREMENTS**

*Side note*: The project was developed on python3.11.1 using:

    ffmpeg==1.4
    psycopg2==2.9.9
    simpleaudio==1.0.4
    pydub==0.25.1

1. For playing audio, _pydub_ and _simpleaudio_ are used as third-party applications. This only allows to listen to .wav files, but you can play other formats if you install _ffmpeg_. More details here: https://github.com/jiaaro/pydub#installation


2. When starting **main.py**, an appsettings.json is required with the following syntax:
```json
{
    "storage": "string",
    "logger": "string",
    "restart": true,
    "connection":{
        "host": "string",
        "user": "string",
        "password": "string",
        "database": "string"
    }
}
```
* If restart == true, then the whole database will be wiped, starting the program with fresh tables

*IMPORTANT: If restart is set on true, then all of storage's files will be erased, starting with an empty directory!*
* If restart == false, tables will be created only if they don't exist

3. Every command from this tool requires a path to a .json file in order to execute. It must follow the next syntax:

**CREATE => returns Song.id if created successfully, -1 otherwise**
```json
{
    "filePath": "string",
    "name" : "string",
    "format": "string",
    "releaseDate": "YY-MM-DD",
    "artists": ["artist1", "artist2"],
    "tags": ["tag1", "tag2"],
    "auto": true
}
```
**If auto is true, only 'filePath' and 'tags' will be considered in inserting into database. Otherwise, all the fields will be taken into consideration.**

*IMPORTANT:* **The correct syntax of basename for 'filePath' if auto is true is: Artist1,Artist2,Artist2-SongName.format**

**DELETE => returns True if succesfully deleted, False otherwise**
```json
{
    "id": 1234
}
```

**UPDATE => returns True if succesfully updated, False otherwise**
```json
{
    "id": 1234,
    "newName": "string",
    "newFormat": "string",
    "newReleaseDate": "date",
    "newArtists": ["newArtist1", "newArtist2"],
    "newTags": ["newTag1", "newTag2"]
}
```
**If you don't want a field to be updated, give an empty string or list.**


**SEARCH => returns queried rows, None otherwise**
```json
{
    "name": "string",
    "format": "string",
    "releaseDate": ["date1", "date2"],
    "artists" : ["artist1", "artist2"],
    "tags" : ["tags1", "tags2"]
}
```
***IMPORTANT*: If releaseDate has 2 arguments, the search will be between 'date1' and 'date2'. If releaseDate has 1 argument, the search will be exactly on 'date1'. If it is an empty list, it will not search after that.**


**It will return *None* if songs doesn't exist or a list of tuples with:**

*(name, format, releaseDate, [artists], [tags])*

**PLAY => plays the song if it exists in songStorage folder**
```json
{
    "filePath": "string"
}
```

**ARCHIVE => archives songs found after a search in the database**

The json format is same as 'SEARCH'. You will be prompted to select the songs which you want to be archived.

**SYNTAX: Option,Option,...  (where argument option can either be a song number from the list (1-indexed) or a interval in the form of NUMBER..NUMBER)**

*IMPORTANT: The songs will be compressed and placed into a new archive in the storage folder.*