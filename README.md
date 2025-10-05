<img src="img/mkpl_logo.svg" alt="mkpl" title="mkpl" align="right" width="150"/> **make_playlist**: Playlist maker
======

``mkpl`` is a _command line tool_ to create playlist files (**[M3U](https://en.wikipedia.org/wiki/M3U) format**), automatically.

## Installation

To install ``mkpl``, see here:

```console
$ pip install make_playlist               # for python enviroment

$ git clone https://github.com/MatteoGuadrini/mkpl.git && cd mkpl
$ pip install .                           # for others
```

## Command arguments

``mkpl`` have many command line arguments. They are explained in this table:

| short | long              | description                                   | args                      |
|-------|-------------------|-----------------------------------------------|---------------------------|
| -d    | --directories     | Directories that contains multimedia file     | Path of directories       |
| -e    | --exclude-dirs    | Exclude directory paths                       | Path of directories       |
| -i    | --include         | Include other file format                     | Format of file. ex. mp3   |
| -p    | --pattern         | Regular expression inclusion pattern          | Regular expression string |
| -P    | --exclude-pattern | Regular expression exclusion pattern          | Regular expression string |
| -f    | --format          | Select only a file format                     | Format of file. ex. mp3   |
| -s    | --size            | Minimum size (bytes, kb, mb, ...)             | Bytes (kb, mb, gb, ...)   |
| -A    | --max-size        | Maximum size (bytes, kb, mb, ...)             | Bytes (kb, mb, gb, ...)   |
| -M    | --length          | Minimum length                                | Seconds                   |
| -X    | --max-length      | Maximum length                                | Seconds                   |
| -m    | --max-tracks      | Maximum number of tracks                      | Number                    |
| -t    | --title           | Playlist title                                | Title string              |
| -g    | --encoding        | Text encoding                                 | UTF-8,ASCII,UNICODE       |
| -I    | --image           | Playlist image                                | Image path                |
| -l    | --link            | Add remote file links                         | Http links                |
| -F    | --file            | Add files                                     | Files                     |
| -j    | --join            | Join one or more other playlist files         | Playlist files            |
| -n    | --cache           | Cache playlist results                        | Seconds                   |
| -U    | --url-chars       | Substitute some chars with URL Encoding       |                           |
| -r    | --recursive       | Recursive search                              |                           |
| -a    | --absolute        | Absolute file name                            |                           |
| -s    | --shuffle         | Casual order                                  |                           |
| -u    | --unique          | The same files are not placed in the playlist |                           |
| -c    | --append          | Continue playlist instead of override it      |                           |
| -w    | --windows         | Windows style folder separator                |                           |
| -x    | --unix            | Unix style folder separator                   |                           |
| -v    | --verbose         | Enable verbosity (debug mode)                 |                           |
| -S    | --split           | Split playlist by directories                 |                           |
| -R    | --interactive     | Asks each file for confirmation               |                           |
| -C    | --count           | Count elements into playlist                  |                           |
| -E    | --explain-error   | Explain error with traceback                  |                           |
| -o    | --orderby-name    | Order playlist files by name                  |                           |
| -O    | --orderby-date    | Order playlist files by creation date         |                           |
| -T    | --orderby-track   | Order playlist files by track                 |                           |
| -y    | --orderby-year    | Order playlist files by year                  |                           |
| -Z    | --orderby-size    | Order playlist files by size                  |                           |
| -L    | --orderby-length  | Order playlist files by length                |                           |
| -N    | --add-info        | Add file information to playlist              |                           |

## Examples

1. Create a playlist for one music album:

    ```bash
    cd myalbum
    mkpl myalbum.m3u
    # or
    mkpl
    ```
   
2. Create a playlist for one music album and add other multimedia files (`-F` option):

    ```bash
    cd myalbum_special
    mkpl myalbum_special.m3u -F music_video.mp4 other_stuff/song1.mp3 other_stuff/song2.mp3
    ```

3. Create a playlist of a film saga

    ```bash
    mkpl -d HarryPotter -f mkv HP_saga.m3u
    ```

4. Create a shuffled playlist with my music collection; include only files with minimum size of 2 Megabyte...and with range

    ```bash
    mkpl -d "my_mp3_collection" "my_mp4_collection" -rs -z 2mb "my music.m3u"
    # Range between 2 and 4 Megabytes
    mkpl -d "my_mp3_collection" "my_mp4_collection" -rs -z 2mb -A 4Mb "my music.m3u"
    ```
   
5. Create a shuffled playlist with my music collection and exclude dirs

    ```bash
    mkpl -d "my_mp3_collection" "my_mp4_collection" -r -s -e "my_mp3_collection/metallica" "my_mp3_collection/dk" -- "my music.m3u"
    ```
   
6. Create a TV series playlist with max 15 tracks

    ```bash
    mkpl -d "my_series/GOT" -m 15 "got_first_15.m3u"
    ```
   
7. Add into _my music_ playlist new songs and don't add same file

    ```bash
    mkpl -d "new_collection" -rsu "my music.m3u" -a
    ```
   
8. Create playlist with music and video files if files is greater then 10MB

    ```bash
    mkpl -d "my_files" -r -z 10485760 "multimedia.m3u"
    ```
   
9. Create playlist with only number one and two tracks with regular expression

    ```bash
    mkpl -d "my_mp3_collection" -r -p "^[12]|[012]{2}" "my music.m3u"
    ```

10. Create a playlist for one music album and set the title:

     ```bash
     cd myalbum
     mkpl myalbum.m3u -t "My Album"
     ```
   
11. Create a playlist and add _UTF-8_ encoding

    ```bash
    mkpl -d "new_collection" -r "my music.m3u" -g "UTF-8"
    ```

12. Create a playlist and set image

    ```bash
    mkpl -d "new_collection" -r "my music.m3u" -I "new_collection/playlist_cover.jpg"
    ```

13. Create a playlist and add remote file links

    ```bash
    mkpl -d "new_collection" -r "my music.m3u" -l http://192.168.1.123/mp3/song1.mp3, http://192.168.1.123/mp3/song2.mp4
    ```
    
14. Create a playlist and set Windows backslash (\\) folder separator (for Windows OS)

    ```bash
    mkpl -d "new_collection" -r "my music.m3u" -w
    ```

15. Split playlist into _N_ playlists fon _N_ directories

    ```bash
    mkpl -d "folder1" "folder2" "folder3" -r "my_music.m3u" -S
    ```
    Result:
    ```console
    $> ls
    my_music.m3u
    folder1.m3u
    folder2.m3u
    folder3.m3u
    ...
    ```

16. Sort playlist files by name (`-o`), by creation date (`-O`), by track number (`-T`), by year (`-y`), by size (`-Z`) or by length (`-L`):

    ```bash
    mkpl -d "new_collection" -r "my music.m3u" -o
    mkpl -d "new_collection" -r "my music.m3u" -O
    mkpl -d "new_collection" -r "my music.m3u" -T
    mkpl -d "new_collection" -r "my music.m3u" -y
    mkpl -d "new_collection" -r "my music.m3u" -Z
    mkpl -d "new_collection" -r "my music.m3u" -L
    ```

17. Join the _"First playlist.m3u"_ and  _"Second playlist.m3u8"_ with new **"Third playlist.m3u"**:

    ```bash
    mkpl -d "new_collection" -r "Third playlist" -j "First playlist.m3u" "Second playlist.m3u8"
    ```

18. Counts the multimedia files:

    ```console
    mkpl -d "new_collection" -r "My new collection" -C
    4023
    ```

19. Asks confirmation for every file into folders:

    ```console
    mkpl -d "new_collection" -r "My new collection" -R
    Add file new_collection/sample1.mp3 to playlist? [Y/n]:y
    Add file new_collection/sample2.mp3 to playlist? [Y/n]:Y
    Add file new_collection/sample3.mp3 to playlist? [Y/n]:n
    Add file new_collection/sample4.mp3 to playlist? [Y/n]:N
    ```

20. Includes mp3 files with minimum length of 42 seconds...and range:

    ```bash
    mkpl -d "music_collection" -M 42 "My new collection"
    # Range of minimum of 42 seconds and maximum of 300 seonds
    mkpl -d "music_collection" -M 42 -X 300 "My new collection"
    ```

21. Add file infos to playlist with [#EXTINF](https://en.wikipedia.org/wiki/M3U#Extended_M3U) tag:

    ```bash
    mkpl -d "HeavyMetal/Master of Puppets" -N "master"
    cat "master.m3u"
    #EXTM3U
    #EXTINF:516,Metallica - Master of Puppets
    HeavyMetal/Master Of Puppets/02 - Master Of Puppets.mp3
    #EXTINF:312,Metallica - Battery
    HeavyMetal/Master Of Puppets/01 - Battery.mp3
    #EXTINF:397,Metallica - The Thing That Should Not Be
    HeavyMetal/Master Of Puppets/03 - The Thing That Should Not Be.mp3
    #EXTINF:508,Metallica - Orion
    HeavyMetal/Master Of Puppets/07 - Orion (Instrumental).mp3
    #EXTINF:497,Metallica - Disposable Heroes
    HeavyMetal/Master Of Puppets/05 - Disposable Heroes.mp3
    #EXTINF:330,Metallica - Damage, Inc.
    HeavyMetal/Master Of Puppets/08 - Damage, Inc..mp3
    #EXTINF:340,Metallica - Leper Messiah
    HeavyMetal/Master Of Puppets/06 - Leper Messiah.mp3
    #EXTINF:387,Metallica - Welcome Home (Sanitarium)
    HeavyMetal/Master Of Puppets/04 - Welcome Home (Sanitarium).mp3
    ```

## Use it like Python module

`mkpl` can also be used as a Python module to customize your scripts.

```python
from make_playlist import *

# Prepare playlist list: find multimedia files with name starts between a and f
playlist = make_playlist('/Music/collections',
                         ('mp3', 'mp4', 'aac'),
                         '^[a-f].*',
                         recursive=True,
                         unique=True)

# Write playlist to file
write_playlist('/Music/AtoF.m3u', 'wt', playlist)
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

Thanks to Mark Lutz for writing the _Learning Python_ and _Programming Python_ books that make up my python foundation.

Thanks to Kenneth Reitz and Tanya Schlusser for writing the _The Hitchhiker’s Guide to Python_ books.

Thanks to Dane Hillard for writing the _Practices of the Python Pro_ books.

Special thanks go to my wife, who understood the hours of absence for this development. 
Thanks to my children, for the daily inspiration they give me and to make me realize, that life must be simple.

Thanks, Python!