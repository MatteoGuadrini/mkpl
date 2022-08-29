# ``mkpl``: Make playlist

``mkpl`` is a _command line tool_ for create playlist file (**M3U format**).

## Installation

To install ``mkpl``, see here:

```console
$ pip install mkpl
```

## Command arguments

``mkpl`` have many command line arguments. They are explained in this table:

| short | long           | description                                   | args                      |
|-------|----------------|-----------------------------------------------|---------------------------|
| -d    | --directories  | Directories that contains multimedia file     | Path of directories       |
| -e    | --exclude-dirs | Exclude directory paths                       | Path of directories       |
| -i    | --include      | Include other file format                     | Format of file. ex. mp3   |
| -p    | --pattern      | Regular expression inclusion pattern          | Regular expression string |
| -f    | --format       | Select only a file format                     | Format of file. ex. mp3   |
| -s    | --size         | Start size in bytes                           | Bytes number              |
| -m    | --max-tracks   | Maximum number of tracks                      | Number                    |
| -r    | --recursive    | Recursive search                              |                           |
| -a    | --absolute     | Absolute file name                            |                           |
| -s    | --shuffle      | Casual order                                  |                           |
| -u    | --unique       | The same files are not placed in the playlist |                           |
| -c    | --append       | Continue playlist instead of override it      |                           |

## Examples

1. Create a playlist for one music album:

    ```bash
    cd myalbum
    mkpl myalbum.m3u
    ```

2. Create a playlist of a film saga

    ```bash
    mkpl -d HarryPotter -f mkv HP_saga.m3u
    ```

3. Create a shuffled playlist with my music collection

    ```bash
    mkpl -d "my_mp3_collection" "my_mp4_collection" -rs "my music.m3u"
    ```
   
4. Create a shuffled playlist with my music collection and exclude dirs

    ```bash
    mkpl -d "my_mp3_collection" "my_mp4_collection" -r -s -e "my_mp3_collection/metallica" "my_mp3_collection/dk" "my music.m3u"
    ```
   
5. Create a TV series playlist with max 15 tracks

    ```bash
    mkpl -d "my_series/GOT" -m 15 "got_first_15.m3u"
    ```
   
6. Add into _my_music_ playlist new songs and don't add same file

    ```bash
    mkpl -d "new_collection" -rsu "my music.m3u" -a
    ```
   
7. Create playlist with music and video files if files is greater then 10MB

    ```bash
    mkpl -d "my_files" -r -z 10485760 "multimedia.m3u"
    ```
   
8. Create playlist with only number one and two tracks wit regular expression

    ```bash
    mkpl -d "my_mp3_collection" -r -p "^[12]|[012]{2}" "my music.m3u"
    ```