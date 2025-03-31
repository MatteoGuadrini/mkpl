#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# mkpl -- mkpl
#
#     Copyright (C) 2025 Matteo Guadrini <matteo.guadrini@hotmail.it>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""mkpl module. This is command line utility for playlist creation."""

# region imports
import argparse
import os.path
import re
from filecmp import cmp
from os.path import basename, dirname, exists, getctime, getsize, isdir, join, normpath
from pathlib import Path
from random import shuffle
from re import sub
from string import capwords

from mutagen import File, MutagenError, id3
from tempcache import TempCache

# endregion

# region globals
AUDIO_FORMAT = {
    "mp1",
    "mp2",
    "mp3",
    "aac",
    "ogg",
    "wav",
    "wma",
    "m4a",
    "aiff",
    "flac",
    "alac",
    "opus",
    "ape",
    "webm",
}
VIDEO_FORMAT = {
    "mp4",
    "avi",
    "xvid",
    "divx",
    "mkv",
    "mpeg",
    "mpg",
    "mov",
    "wmv",
    "flv",
    "vob",
    "asf",
    "m4v",
    "3gp",
    "f4a",
}
FILE_FORMAT = AUDIO_FORMAT.union(VIDEO_FORMAT)
__version__ = "1.12.0"


# endregion


# region functions
def get_args():
    """Get command-line arguments"""

    global FILE_FORMAT

    parser = argparse.ArgumentParser(
        description="Command line tool to create playlist files in M3U format.",
        epilog="See latest release from https://github.com/MatteoGuadrini/mkpl",
    )
    orderby_group = parser.add_mutually_exclusive_group()

    parser.add_argument("playlist", help="Playlist file", type=str)
    parser.add_argument("-v", "--verbose", help="Enable verbosity", action="store_true")
    parser.add_argument(
        "-V", "--version", help="Print version", action="version", version=__version__
    )
    parser.add_argument(
        "-d",
        "--directories",
        help="Directories that contains multimedia file",
        nargs=argparse.ONE_OR_MORE,
        default=["."],
    )
    parser.add_argument(
        "-e",
        "--exclude-dirs",
        help="Exclude directory paths",
        nargs=argparse.ONE_OR_MORE,
        default=[],
    )
    parser.add_argument(
        "-i",
        "--include",
        help="Include other file format",
        nargs=argparse.ONE_OR_MORE,
        metavar="FORMAT",
    )
    parser.add_argument(
        "-p", "--pattern", help="Regular expression inclusion pattern", default=None
    )
    parser.add_argument(
        "-P",
        "--exclude-pattern",
        help="Regular expression exclusion pattern",
        default=None,
    )
    parser.add_argument(
        "-f",
        "--format",
        help="Select only a file format",
        type=str,
        choices=FILE_FORMAT,
    )
    parser.add_argument(
        "-z",
        "--size",
        help="Minimum size (bytes, kb, mb, ...)",
        default="1",
        metavar="BYTES",
    )
    parser.add_argument(
        "-m",
        "--max-tracks",
        help="Maximum number of tracks",
        type=int,
        default=None,
        metavar="NUMBER",
    )
    parser.add_argument("-t", "--title", help="Playlist title", default=None)
    parser.add_argument(
        "-g",
        "--encoding",
        help="Text encoding",
        choices=("UTF-8", "ASCII", "UNICODE"),
        default=None,
    )
    parser.add_argument("-I", "--image", help="Playlist image", default=None)
    parser.add_argument(
        "-l",
        "--link",
        help="Add remote file links",
        nargs=argparse.ONE_OR_MORE,
        metavar="HTTP_LINK",
        default=[],
    )
    parser.add_argument(
        "-F",
        "--file",
        help="Add file",
        nargs=argparse.ONE_OR_MORE,
        default=[],
    )
    parser.add_argument(
        "-j",
        "--join",
        help="Join one or more other playlist files",
        nargs=argparse.ONE_OR_MORE,
        metavar="PLAYLISTS",
        default=[],
    )
    parser.add_argument(
        "-M", "--length", help="Minimum length", default=1, metavar="SECONDS", type=int
    )
    parser.add_argument(
        "-r", "--recursive", help="Recursive search", action="store_true"
    )
    parser.add_argument(
        "-a", "--absolute", help="Absolute file name", action="store_true"
    )
    parser.add_argument(
        "-u",
        "--unique",
        help="The same files are not placed in the playlist",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--append",
        help="Continue playlist instead of override it",
        action="store_true",
    )
    parser.add_argument(
        "-w", "--windows", help="Windows style folder separator", action="store_true"
    )
    parser.add_argument(
        "-S", "--split", help="Split playlist by directories", action="store_true"
    )
    parser.add_argument(
        "-R",
        "--interactive",
        help="Asks each file for confirmation",
        action="store_true",
    )
    parser.add_argument(
        "-C", "--count", help="Count elements into playlist", action="store_true"
    )
    orderby_group.add_argument(
        "-s", "--shuffle", help="Casual order", action="store_true"
    )
    orderby_group.add_argument(
        "-o", "--orderby-name", help="Order playlist files by name", action="store_true"
    )
    orderby_group.add_argument(
        "-O", "--orderby-date", help="Order playlist files by date", action="store_true"
    )
    orderby_group.add_argument(
        "-T",
        "--orderby-track",
        help="Order playlist files by track",
        action="store_true",
    )
    orderby_group.add_argument(
        "-y",
        "--orderby-year",
        help="Order playlist files by year",
        action="store_true",
    )
    orderby_group.add_argument(
        "-Z",
        "--orderby-size",
        help="Order playlist files by size",
        action="store_true",
    )
    orderby_group.add_argument(
        "-L",
        "--orderby-length",
        help="Order playlist files by length",
        action="store_true",
    )
    orderby_group.add_argument(
        "-U",
        "--url-chars",
        help="Substitute some chars with URL Encoding (Percent Encoding)",
        action="store_true",
    )
    orderby_group.add_argument(
        "-n",
        "--cache",
        help="Cache playlist results",
        type=int,
        metavar="SECONDS",
    )

    args = parser.parse_args()

    # Check extension of playlist file
    if not args.playlist.endswith(".m3u"):
        if args.encoding == "UNICODE":
            if not args.playlist.endswith(".m3u8"):
                args.playlist += ".m3u8"
        else:
            args.playlist += ".m3u"

    # Check if playlist is not a directory
    if isdir(args.playlist):
        parser.error(f"{args.playlist} is a directory")

    # Open playlist file
    args.open_mode = "at+" if args.append else "wt"
    args.enabled_extensions = False
    args.enabled_title = False
    args.enabled_encoding = False
    # Verify extension attribute in append mode
    if args.append:
        with open(args.playlist, mode=args.open_mode) as opened_playlist:
            opened_playlist.seek(0)
            first_three_lines = opened_playlist.readlines(100)
            for line in first_three_lines:
                if "#EXTM3U" in line:
                    args.enabled_extensions = True
                if "#PLAYLIST" in line:
                    args.enabled_title = True
                if "#EXTENC" in line:
                    args.enabled_encoding = True
            # Check if extensions are disabled and image is specified
            if getsize(args.playlist) > 0:
                if not args.enabled_extensions and args.image:
                    print(
                        f"warning: image {args.image} has not "
                        "been set because the extension flag"
                        " is not present in the playlist"
                    )
                    args.image = None

    # Check if image file exists
    if args.image:
        if not exists(args.image):
            parser.error(f"image file {args.image} does not exist")

    # Extend files format
    if args.include:
        FILE_FORMAT.update(set([fmt.strip("*").strip(".") for fmt in args.include]))

    # Select only one format
    if args.format:
        FILE_FORMAT = {args.format.strip("*").strip(".")}

    # Convert size string into number
    if args.size:
        args.size = human_size_to_byte(args.size)

    # Check link argument if it is a valid link
    if args.link:
        args.link = [link for link in args.link if re.match("https?://", link)]

    # Check if other files exists
    if args.file:
        args.file = [f for f in args.file if os.path.exists(f)]

    return args


def human_size_to_byte(size):
    """Convert human size into bytes

    :param size: size string
    :return: int
    """
    size_name = ("b", "kb", "mb", "gb", "tb", "pb", "eb", "zb", "yb")
    size_parts = re.search("([0-9]+) ?([a-zA-Z]+)?", size)
    num, unit = int(size_parts[1]), size_parts[2]
    if unit:
        unit = unit.lower()
        unit = unit if "b" in unit else unit + "b"
        idx = size_name.index(unit)
        factor = 1024**idx
        size_bytes = num * factor
    else:
        size_bytes = num
    return size_bytes


def confirm(file, default="y"):
    """Ask user to enter Y or N (case-insensitive)

    :file: file to add into playlist
    :default: default answer
    :return: True if the answer is Y.
    :rtype: bool
    """
    while (
        answer := input(
            "Add file {0} to playlist? {1}:".format(
                file, "[Y/n]" if default == "y" else "[y/N]"
            )
        ).lower()
    ) not in ("y", "n"):
        # Check if default
        if not answer:
            answer = default
            break
    return answer == "y"


def file_in_playlist(playlist, file, root=None):
    """Check if file is in the playlist"""
    for f in playlist:
        # Skip extended tags
        if f.startswith("#"):
            continue
        # Check if absolute path in playlist
        if root:
            f = join(root, f)
        # Make standard the path
        f = unix_to_dos(f, viceversa=True)
        # Compare two files
        if cmp(f, file):
            return True


def join_playlist(playlist, *others):
    """Join current playlist with others"""
    for file in others:
        try:
            # open playlist, remove extensions and extend current playlist file
            lines = open(file).readlines()
            playlist.extend(
                [line.rstrip() for line in lines if not line.startswith("#")]
            )
        except FileNotFoundError:
            print(f"warning: {file} file not found")
        except OSError as err:
            print(f"warning: {file} generated error: {err}")


def url_chars(playlist):
    """URL encoding converts characters into a format that can be transmitted over the Internet."""
    URL_CHARS = {
        " ": "%20",
        "!": "%21",
        '"': "%22",
        "#": "%23",
        "$": "%24",
        "%": "%25",
        "&": "%26",
        "'": "%27",
        "(": "%28",
        ")": "%29",
        "*": "%2A",
        "+": "%2B",
        ",": "%2C",
        "-": "%2D",
        ":": "%3A",
        ";": "%3B",
        "<": "%3C",
        "=": "%3D",
        ">": "%3E",
        "?": "%3F",
        "@": "%40",
        "[": "%5B",
        "]": "%5D",
        "^": "%5E",
        "_": "%5F",
        "`": "%60",
        "{": "%7B",
        "|": "%7C",
        "}": "%7D",
        "~": "%7E",
    }
    ret = []
    for file in playlist:
        for char in file:
            if URL_CHARS.get(char):
                file = file.replace(char, URL_CHARS.get(char))
        ret.append(file)

    return ret


def report_issue(exc):
    """Report issue"""
    print(
        "error: {0} on line {1}, with error {2}".format(
            type(exc).__name__, exc.__traceback__.tb_lineno, str(exc)
        )
    )
    exit(1)


def open_multimedia_file(path):
    """Open multimedia file

    :param path: multimedia file to open
    """
    try:
        file = File(path)
    except MutagenError:
        print(f"warning: file '{path}' loading failed")
        return False
    return file


def get_track(file):
    """Get file by track for sort"""
    file = open_multimedia_file(file)
    if file and hasattr(file, "tags"):
        default = id3.TRCK(text="0")
        return int(file.tags.get("TRCK", default)[0])


def get_year(file):
    """Get file by year for sort"""
    file = open_multimedia_file(file)
    if file and hasattr(file, "tags"):
        default = id3.TDOR(text="0")
        return file.tags.get("TDOR", default)[0]


def get_length(file):
    """Get file by length for sort"""
    file = open_multimedia_file(file)
    if file and hasattr(file, "info"):
        return file.info.length if hasattr(file.info, "length") else 0.0


def find_pattern(pattern, path):
    """Find patter in a file and tags"""
    global AUDIO_FORMAT

    # Create compiled pattern
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern)
    # Check pattern into filename
    if pattern.findall(path):
        return True
    # Check type of file
    ext = os.path.splitext(path)[1].replace(".", "").lower()
    if ext in AUDIO_FORMAT:
        file = open_multimedia_file(path)
        # Check supports of ID3 tags add compiled pattern
        if file and hasattr(file, "ID3"):
            # Check pattern into title
            if file.tags.get("TIT2"):
                if pattern.findall(file.tags.get("TIT2")[0]):
                    return True
            # Check pattern into album
            if file.tags.get("TALB"):
                if pattern.findall(file.tags.get("TALB")[0]):
                    return True


def vprint(verbose, *messages):
    """Verbose print"""
    if verbose:
        print("debug:", *messages)


def unix_to_dos(path, viceversa=False):
    """Substitute folder separator with windows separator

    :param path: path to substitute folder separator
    :param viceversa: dos to unix
    """
    if viceversa:
        old_sep = r"\\"
        new_sep = "/"
    else:
        old_sep = "/"
        new_sep = r"\\"
    return sub(old_sep, new_sep, path)


def write_playlist(
    playlist,
    open_mode,
    files,
    encoding,
    enabled_extensions=False,
    image=None,
    ext_part=None,
    max_tracks=None,
    verbose=False,
):
    """Write playlist into file"""
    if playlist:
        with open(
            playlist,
            mode=open_mode,
            encoding="UTF-8" if encoding == "UNICODE" else encoding,
            errors="ignore",
        ) as pl:
            if image and enabled_extensions:
                vprint(verbose, f"set image {image}")
                joined_string = f"\n#EXTIMG: {image}\n"
            else:
                joined_string = "\n"
            end_file_string = "\n"
            # Write extensions if exists
            if ext_part:
                pl.write("\n".join(files[:ext_part]) + joined_string)
            # Write all multimedia files
            vprint(verbose, f"write playlist {pl.name}")
            pl.write(joined_string.join(files[ext_part:max_tracks]) + end_file_string)


def make_playlist(
    directory,
    file_formats,
    pattern=None,
    exclude_pattern=None,
    sortby_name=False,
    sortby_date=False,
    sortby_track=False,
    sortby_year=False,
    sortby_size=False,
    sortby_length=False,
    recursive=False,
    exclude_dirs=None,
    unique=False,
    absolute=False,
    min_size=1,
    min_length=1,
    windows=False,
    interactive=False,
    verbose=False,
):
    """Make playlist list"""
    filelist = list()
    # Check if directory exists
    if not exists(directory):
        print(f"warning: {directory} does not exists")
        return filelist
    # Check if is a directory
    if not isdir(directory):
        print(f"warning: {directory} is not a directory")
        return filelist
    # Build a Path object
    path = Path(directory)
    root = path.parent
    vprint(verbose, f"current directory={path}, root={root}")
    for fmt in file_formats:
        # Check recursive
        folder = "**/*" if recursive else "*"
        files = path.glob(folder + f".{fmt}")
        # Process found files
        for file in files:
            # Get size of file
            size = file.stat().st_size
            # Check absolute file names
            file = str(file.resolve()) if absolute else str(file)
            # Check file match pattern
            if pattern:
                # Check re pattern
                compiled_pattern = re.compile(pattern)
                if not find_pattern(compiled_pattern, file):
                    continue
            if exclude_pattern:
                # Check re pattern
                compiled_pattern = re.compile(exclude_pattern)
                if find_pattern(compiled_pattern, file):
                    continue
            # Check if in exclude dirs
            if any([e_path in file for e_path in exclude_dirs]):
                continue
            # Check if file is in playlist
            if unique:
                if file_in_playlist(
                    filelist, file, root=root if not absolute else None
                ):
                    continue
            # Check file size
            if size <= min_size:
                continue
            # Check length
            if get_length(file) <= min_length:
                continue
            if interactive:
                if not confirm(file):
                    continue
            vprint(verbose, f"add multimedia file {file}")
            filelist.append(unix_to_dos(file) if windows else file)
    # Check sort
    if sortby_name:
        filelist = sorted(filelist)
    elif sortby_date:
        filelist = sorted(filelist, key=getctime)
    elif sortby_track:
        filelist = sorted(filelist, key=get_track)
    elif sortby_year:
        filelist = sorted(filelist, key=get_year)
    elif sortby_size:
        filelist = sorted(filelist, key=os.path.getsize)
    elif sortby_length:
        filelist = sorted(filelist, key=get_length)
    return filelist


def add_extension(filelist, cli_args, verbose=False):
    """Add extension to playlist list"""
    if not isinstance(filelist, list):
        raise ValueError(f"{filelist} is not a list object")

    # Check if playlist is an extended M3U
    cli_args.ext_part = 0
    if cli_args.title or cli_args.encoding or cli_args.image:
        if not cli_args.enabled_extensions:
            filelist.insert(0, "#EXTM3U")
            vprint(verbose, "enable extension flag")
            cli_args.enabled_extensions = True
            cli_args.ext_part += 1
            if cli_args.max_tracks:
                cli_args.max_tracks += 1

        # Set title
        if cli_args.title:
            if not cli_args.enabled_title:
                title = capwords(cli_args.title)
                filelist.insert(1, f"#PLAYLIST: {title}")
                vprint(verbose, f"set title {title}")
                cli_args.ext_part += 1
                if cli_args.max_tracks:
                    cli_args.max_tracks += 1
            else:
                print("warning: title is already configured")

        # Set encoding
        if cli_args.encoding:
            if not cli_args.enabled_encoding:
                filelist.insert(1, f"#EXTENC: {cli_args.encoding}")
                vprint(verbose, f"set encoding {cli_args.encoding}")
                cli_args.ext_part += 1
                if cli_args.max_tracks:
                    cli_args.max_tracks += 1
            else:
                print("warning: encoding is already configured")


def _process_playlist(files, cli_args, other_playlist=None):
    """Private function cli only for process arguments and make playlist"""

    # Join other playlist files
    if cli_args.join:
        join_playlist(files, *cli_args.join)

    # Add link
    files.extend(cli_args.link)

    # Add other files
    files.extend(cli_args.file)

    # Build a playlist
    if files:
        # Check shuffle
        if cli_args.shuffle:
            shuffle(files)

        # Add extension to playlist
        add_extension(files, cli_args, verbose=cli_args.verbose)

        # Write playlist to file
        write_playlist(
            other_playlist if other_playlist else cli_args.playlist,
            cli_args.open_mode,
            files,
            encoding=cli_args.encoding,
            enabled_extensions=cli_args.enabled_extensions,
            image=cli_args.image,
            ext_part=cli_args.ext_part,
            max_tracks=cli_args.max_tracks,
            verbose=cli_args.verbose,
        )
    else:
        print(
            "warning: no multimedia "
            f"files are found here: {','.join(cli_args.directories)}"
        )


def main():
    """Make a playlist file"""

    try:
        args = get_args()
        multimedia_files = list()
        vprint(
            args.verbose,
            f"formats={FILE_FORMAT}, recursive={args.recursive}, "
            f"pattern={args.pattern}, split={args.split}",
        )

        # Define cache
        if args.cache:
            cache = TempCache("mkpl", max_age=args.cache)
            vprint(args.verbose, f"use cache {cache.path}")
            # Clean the cache
            cache.clear_items()
        else:
            cache = None

        # Make multimedia list
        for directory in args.directories:
            if args.cache:
                directory_files = cache.cache_result(
                    make_playlist,
                    directory,
                    FILE_FORMAT,
                    args.pattern,
                    args.exclude_pattern,
                    sortby_name=args.orderby_name,
                    sortby_date=args.orderby_date,
                    sortby_track=args.orderby_track,
                    sortby_year=args.orderby_year,
                    sortby_size=args.orderby_size,
                    sortby_length=args.orderby_length,
                    recursive=args.recursive,
                    exclude_dirs=args.exclude_dirs,
                    unique=args.unique,
                    absolute=args.absolute,
                    min_size=args.size,
                    min_length=args.length,
                    windows=args.windows,
                    interactive=args.interactive,
                    verbose=args.verbose,
                )
            else:
                directory_files = make_playlist(
                    directory,
                    FILE_FORMAT,
                    args.pattern,
                    args.exclude_pattern,
                    sortby_name=args.orderby_name,
                    sortby_date=args.orderby_date,
                    sortby_track=args.orderby_track,
                    sortby_year=args.orderby_year,
                    sortby_size=args.orderby_size,
                    sortby_length=args.orderby_length,
                    recursive=args.recursive,
                    exclude_dirs=args.exclude_dirs,
                    unique=args.unique,
                    absolute=args.absolute,
                    min_size=args.size,
                    min_length=args.length,
                    windows=args.windows,
                    interactive=args.interactive,
                    verbose=args.verbose,
                )

            multimedia_files.extend(directory_files)

            # Check if you must split into directory playlist
            if args.split:
                # Substitute chars with URL encoding
                if args.url_chars:
                    multimedia_files = url_chars(directory_files)
                playlist_name = basename(normpath(directory))
                playlist_ext = ".m3u8" if args.encoding == "UNICODE" else ".m3u"
                playlist_path = join(
                    dirname(args.playlist), playlist_name + playlist_ext
                )
                _process_playlist(directory_files, args, playlist_path)
                args.enabled_extensions = False

        # Substitute chars with URL encoding
        if args.url_chars:
            multimedia_files = url_chars(multimedia_files)

        _process_playlist(multimedia_files, args)

        # Count files into playlist
        if args.count:
            print(len([file for file in multimedia_files if not file.startswith("#")]))

    except Exception as err:
        report_issue(err)


# endregion

# region main
if __name__ == "__main__":
    main()

# endregion
