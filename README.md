<img src="img/mkpl_logo.svg" alt="mkpl" title="mkpl" align="right" width="150"/> **make_playlist**: Playlist maker
======

``mkpl`` is a _command line tool_ to create playlist files (**[M3U](https://en.wikipedia.org/wiki/M3U) format**), automatically.

## Table of Contents

- [Installation](#installation)
- [Command Arguments](#command-arguments)
- [Examples](#examples)
- [Python Module Usage](#use-it-like-python-module)
- [Contributing](#open-source)
- [License & Acknowledgments](#acknowledgments)

## Installation

To install ``mkpl``, choose one of the following methods:

### Option 1: PyPI Installation (Recommended)

```console
$ pip install make_playlist
```

### Option 2: From Source

```console
$ git clone https://github.com/MatteoGuadrini/mkpl.git
$ cd mkpl
$ pip install .
```

## Command Arguments

``mkpl`` supports numerous command-line arguments for flexible playlist creation. Below is a comprehensive reference:

### Basic Options

| Short | Long | Description | Arguments |
|-------|------|-------------|-----------|
| -d | --directories | Directories containing multimedia files | Path of directories |
| -e | --exclude-dirs | Exclude specific directory paths | Path of directories |
| -r | --recursive | Recursively search directories | — |

### File Format Options

| Short | Long | Description | Arguments |
|-------|------|-------------|-----------|
| -f | --format | Select only a specific file format | Format (e.g., mp3, mkv) |
| -i | --include | Include additional file formats | Format list (e.g., mp3 mp4) |
| -p | --pattern | Include files matching regex pattern | Regular expression |
| -P | --exclude-pattern | Exclude files matching regex pattern | Regular expression |

### File Size & Duration Filters

| Short | Long | Description | Arguments |
|-------|------|-------------|-----------|
| -z | --size | Minimum file size | Bytes, kb, mb, gb (e.g., 2mb) |
| -A | --max-size | Maximum file size | Bytes, kb, mb, gb (e.g., 4mb) |
| -M | --length | Minimum track length | Seconds |
| -X | --max-length | Maximum track length | Seconds |

### Playlist Configuration

| Short | Long | Description | Arguments |
|-------|------|-------------|-----------|
| -t | --title | Set playlist title | Title string |
| -g | --encoding | Set text encoding | UTF-8, ASCII, UNICODE |
| -I | --image | Set playlist cover image | Image file path |
| -m | --max-tracks | Limit number of tracks | Number |

### File Management

| Short | Long | Description | Arguments |
|-------|------|-------------|-----------|
| -F | --file | Add additional files | File paths |
| -l | --link | Add remote file links | HTTP/HTTPS URLs |
| -j | --join | Join other playlist files | Playlist file paths |
| -k | --other-playlists | Include other playlists | Playlist file paths |

### Sorting & Ordering

| Short | Long | Description |
|-------|------|-------------|
| -o | --orderby-name | Sort by filename |
| -O | --orderby-date | Sort by creation date |
| -T | --orderby-track | Sort by track number |
| -y | --orderby-year | Sort by year metadata |
| -Z | --orderby-size | Sort by file size |
| -L | --orderby-length | Sort by track duration |
| -s | --shuffle | Randomize track order |
| -D | --descending | Reverse sort order |

### Output & Processing

| Short | Long | Description |
|-------|------|-------------|
| -a | --absolute | Use absolute file paths |
| -u | --unique | Remove duplicate files |
| -c | --append | Append to existing playlist |
| -w | --windows | Use Windows path separators |
| -x | --unix | Use Unix path separators |
| -U | --url-chars | Apply URL encoding to paths |
| -N | --add-info | Include file metadata (#EXTINF) |

### Interactive & Utility Options

| Short | Long | Description |
|-------|------|-------------|
| -R | --interactive | Confirm each file before adding |
| -C | --count | Count files without creating playlist |
| -S | --split | Split into separate playlists by directory |
| -Y | --filter | Filter by metadata (artist, album, etc.) |
| -n | --cache | Cache results (seconds) |
| -v | --verbose | Enable debug output |
| -E | --explain-error | Show detailed error traceback |
| -V | --version | Display version information |

## Examples

### Basic Usage

1. **Create a playlist for one music album:**

    ```bash
    cd myalbum
    mkpl myalbum.m3u
    # or use default naming
    mkpl
    ```

### Directory & Format Filtering

2. **Create playlist from specific format:**

    ```bash
    mkpl -d HarryPotter -f mkv HP_saga.m3u
    ```

3. **Create shuffled playlist with size filters:**

    ```bash
    mkpl -d "my_mp3_collection" "my_mp4_collection" -rs -z 2mb -A 4mb "my music.m3u"
    ```

4. **Exclude specific directories:**

    ```bash
    mkpl -d "my_mp3_collection" "my_mp4_collection" -r -s -e "my_mp3_collection/metallica" "my_mp3_collection/dk" -- "my music.m3u"
    ```

### Advanced Filtering

5. **Limit by track count:**

    ```bash
    mkpl -d "my_series/GOT" -m 15 "got_first_15.m3u"
    ```

6. **Filter by track number with regex:**

    ```bash
    mkpl -d "my_mp3_collection" -r -p "^[12]|[012]{2}" "my music.m3u"
    ```

7. **Filter by duration range:**

    ```bash
    mkpl -d "music_collection" -M 42 -X 300 "My new collection"
    ```

### File Management

8. **Add external files to playlist:**

    ```bash
    cd myalbum_special
    mkpl myalbum_special.m3u -F music_video.mp4 other_stuff/song1.mp3 other_stuff/song2.mp3
    ```

9. **Add remote file links:**

    ```bash
    mkpl -d "new_collection" -r "my music.m3u" -l http://192.168.1.123/mp3/song1.mp3 http://192.168.1.123/mp3/song2.mp4
    ```

10. **Merge playlists:**

    ```bash
    mkpl -d "Rock'n'Roll" -- "RockNRoll.m3u"
    mkpl -d "Hard Rock" -j "RockNRoll.m3u" -- "Rock.m3u"
    ```

### Metadata & Formatting

11. **Add playlist metadata:**

    ```bash
    mkpl -d "new_collection" -r "my music.m3u" -t "My Collection" -g "UTF-8" -I "new_collection/cover.jpg"
    ```

12. **Include track information (#EXTINF):**

    ```bash
    mkpl -d "HeavyMetal/Master of Puppets" -N "master"
    cat "master.m3u"
    #EXTM3U
    #EXTINF:516,Metallica - Master of Puppets
    HeavyMetal/Master Of Puppets/02 - Master Of Puppets.mp3
    ```

### Sorting & Organization

13. **Sort by various criteria:**

    ```bash
    mkpl -d "new_collection" -r "my music.m3u" -o        # by name
    mkpl -d "new_collection" -r "my music.m3u" -O        # by date
    mkpl -d "new_collection" -r "my music.m3u" -T        # by track
    mkpl -d "new_collection" -r "my music.m3u" -y        # by year
    mkpl -d "new_collection" -r "my music.m3u" -Z        # by size
    mkpl -d "new_collection" -r "my music.m3u" -L -D     # by length (descending)
    ```

14. **Split into multiple playlists:**

    ```bash
    mkpl -d "folder1" "folder2" "folder3" -r "my_music.m3u" -S
    # Results in: my_music.m3u, folder1.m3u, folder2.m3u, folder3.m3u
    ```

### Metadata Filtering

15. **Filter by artist and album:**

    ```bash
    mkpl -d "HeavyMetal" -Y artist=Metallica -Y album="Master of Puppets" -- "MoP.m3u"
    ```

### Interactive & Utility Operations

16. **Count files:**

    ```bash
    mkpl -d "new_collection" -r -C
    # Output: 4023
    ```

17. **Interactive confirmation for each file:**

    ```bash
    mkpl -d "new_collection" -r -R
    Add file new_collection/sample1.mp3 to playlist? [Y/n]: y
    ```

18. **Append to existing playlist without duplicates:**

    ```bash
    mkpl -d "new_collection" -rsu "my music.m3u" -a
    ```

## Use it like Python module

You can use `mkpl` programmatically in your Python projects to build and write playlists dynamically.

### Quick Start

Import the main functions:

```python
from make_playlist import make_playlist, write_playlist
```

Basic example — create and write a playlist:

```python
# Find multimedia files whose names start with a-f
playlist = make_playlist(
    '/Music/collections',
    ('mp3', 'mp4', 'aac'),
    pattern='^[a-f].*',
    recursive=True,
    unique=True
)

write_playlist('/Music/AtoF.m3u', 'wt', playlist)
```

### Important Notes

- `make_playlist()` returns a `Playlist` object containing `PlaylistEntry` items
- You can iterate, filter, or convert results to a list before writing
- Most CLI flags are exposed as keyword arguments (e.g., `recursive`, `unique`, `add_info`, `encoding`, `title`, `image`)
- Use `encoding='utf-8'` parameter for UTF-8 encoded output
- `pathlib.Path` objects are fully supported

### Python Examples

**Example 1: Write UTF-8 playlist with metadata**

```python
from pathlib import Path

plist = make_playlist(
    Path('/Music/collections'),
    ('mp3',),
    recursive=True
)

write_playlist(
    Path('/Music/AtoF.m3u'),
    'wt',
    plist,
    encoding='utf-8',
    title='A–F Collection',
    image=Path('/Music/cover.jpg')
)
```

**Example 2: Inspect and filter results**

```python
results = make_playlist(
    '/Music/collections',
    ('mp3', 'flac'),
    recursive=True
)

for entry in results:
    print(f"File: {entry.file}")
    if entry.extinf:
        print(f"Info: {entry.extinf}")
```

**Example 3: Advanced filtering with metadata**

```python
playlist = make_playlist(
    '/Music/HeavyMetal',
    ('mp3',),
    recursive=True,
    filters=[
        ('artist', 'Metallica'),
        ('album', 'Master of Puppets')
    ],
    add_info=True
)

write_playlist('/Music/MoP.m3u', 'wt', playlist)
```

### API Reference

See function docstrings for complete parameter documentation:

```python
help(make_playlist)
help(write_playlist)
```
   
## Open source
_mkpl_ is an open source project. Any contribute, It's welcome.

**A great thanks**.

For donations, press this

For me

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/guos)

For [Telethon](http://www.telethon.it/)

The Telethon Foundation is a non-profit organization recognized by the Ministry of University and Scientific and Technological Research.
They were born in 1990 to respond to the appeal of patients suffering from rare diseases.
Come today, we are organized to dare to listen to them and answers, every day of the year.

[Adopt the future](https://www.ioadottoilfuturo.it/)


## Treeware  

This package is [Treeware](https://treeware.earth). If you use it in production, 
then we ask that you [**buy the world a tree**](https://plant.treeware.earth/matteoguadrini/mkpl) to thank us for our work. 
By contributing to the Treeware forest you’ll be creating employment for local families and restoring wildlife habitats.

[![Buy us a tree](https://img.shields.io/badge/Treeware-%F0%9F%8C%B3-lightgreen?style=for-the-badge)](https://plant.treeware.earth/MatteoGuadrini/mkpl)


## Acknowledgments

Special thanks to:

- **Mark Lutz** — _Learning Python_ and _Programming Python_ books
- **Kenneth Reitz & Tanya Schlusser** — _The Hitchhiker's Guide to Python_
- **Dane Hillard** — _Practices of the Python Pro_
- **My family** — For continuous support and inspiration

Thanks, Python!