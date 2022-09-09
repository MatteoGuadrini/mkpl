# ``mkpl``: Make playlist

``mkpl`` is a _command line tool_ for create playlist file (**M3U format**).

## Installation

To install ``mkpl``, see here:

```console
$ pip install make_playlist               # for python enviroment

$ dnf copr enable matteoguadrini/mkpl
$ dnf install python-mkpl -y     # for Red Hat, CentOS, Mageia and fedora

$ git clone https://github.com/MatteoGuadrini/mkpl.git && cd mkpl
$ python setup.py install        # for others
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

<a href="https://www.telethon.it/sostienici/dona-ora"> <img src="https://www.telethon.it/dev/_nuxt/img/c6d474e.svg" alt="Telethon" title="Telethon" width="200" height="104" /> </a>

[Adopt the future](https://www.ioadottoilfuturo.it/)


## Treeware  

This package is [Treeware](https://treeware.earth). If you use it in production, 
then we ask that you [**buy the world a tree**](https://plant.treeware.earth/matteoguadrini/mkpl) to thank us for our work. 
By contributing to the Treeware forest you’ll be creating employment for local families and restoring wildlife habitats.

[![Treeware](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=Treeware&query=%24.total&url=https%3A%2F%2Fpublic.offset.earth%2Fusers%2Ftreeware%2Ftrees)](https://treeware.earth)


## Acknowledgments

Thanks to Mark Lutz for writing the _Learning Python_ and _Programming Python_ books that make up my python foundation.

Thanks to Kenneth Reitz and Tanya Schlusser for writing the _The Hitchhiker’s Guide to Python_ books.

Thanks to Dane Hillard for writing the _Practices of the Python Pro_ books.

Special thanks go to my wife, who understood the hours of absence for this development. 
Thanks to my children, for the daily inspiration they give me and to make me realize, that life must be simple.

Thanks Python!