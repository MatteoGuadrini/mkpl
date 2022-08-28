# ``mkpl``: Make playlist

``mkpl`` is a _command line tool_ for create playlist file (**M3U format**).

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

