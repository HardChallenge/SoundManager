# SoundManager

![Version](https://img.shields.io/badge/version-v1.0-blue)
[![GitHub contributors](https://img.shields.io/github/contributors/HardChallenge/SoundManager)](https://github.com/HardChallenge/SoundManager/graphs/contributors)
![Total Views](https://views.whatilearened.today/views/github/HardChallenge/SoundManager.svg)
[![GitHub issues](https://img.shields.io/github/issues/HardChallenge/SoundManager)](https://github.com/HardChallenge/SoundManager/issues)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/HardChallenge/SoundManager/blob/main/LICENSE)


**Sound Manager** facilitates seamless storage, management, and metadata operations for audio files, enhanced by asynchronous logging for efficient monitoring.
---

## Contents

- [Introduction](#introduction)
- [Functionalities](#functionalities)
- [Requirements](#requirements)
- [Technologies](#technologies)
- [Setup Guide](#setup-guide)
- [Usage](#usage)

---

## Introduction


**Sound Manager** is an application designed for storing and managing audio files within a predefined directory named 'storage', while performing CRUD operations on metadata stored in PostgreSQL database tables. 

Additionally, the application features an asynchronous logging system that records all events to the 'logger' file, ensuring efficient monitoring of operations. This platform enables users to upload, view, and manage collections of music tracks in an organized and user-friendly manner, making it ideal for music enthusiasts. 


--- 

## Functionalities

- **Audio File Upload**: Users can easily upload audio files to the designated 'storage' directory for centralized storage.
- **Metadata Management**: Provides CRUD operations for managing metadata associated with each audio file in a PostgreSQL database.
- **Playback and Visualization**: Enables users to play uploaded audio files directly within the command line interface.
- **Asynchronous Logging**: Logs all operations and events asynchronously to a 'logger' file, ensuring streamlined monitoring and tracking.

---

## Technologies

- **Backend**: Python3, PostgreSQL, JSON

---

## Requirements

The project was developed on python3.11.1 using:

    ffmpeg==1.4
    psycopg2==2.9.9
    simpleaudio==1.0.4
    pydub==0.25.1

1. For playing audio, _pydub_ and _simpleaudio_ are used as third-party applications. This only allows to listen to .wav files, but you can play other formats if you install _ffmpeg_. More details here: https://github.com/jiaaro/pydub#installation


2. When starting **main.py**, an appsettings.json is required with the following syntax:
```json
{
    "storage": "file_path",
    "logger": "file_path",
    "restart": true,
    "connection":{
        "host": "database_host",
        "user": "database_user",
        "password": "database_password",
        "database": "database_name"
    }
}
```
* If restart == true, then the whole database will be wiped, starting the program with fresh tables

*IMPORTANT: If restart is set on true, then all of storage's files will be erased, starting with an empty directory!*
* If restart == false, tables will be created only if they don't exist

---

## Setup Guide

1. Clone the repository:

```bash
git clone https://github.com/HardChallenge/SoundManager.git
```

2. Change the directory:

```bash
cd SoundManager
```

3. Execute the main script:
```bash
python3 main.py
```

4. Execute a command with the following syntax:

    [command] [file_path]

Commands available: CREATE, DELETE, UPDATE, SEARCH, PLAY, ARCHIVE

---

## Usage

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

