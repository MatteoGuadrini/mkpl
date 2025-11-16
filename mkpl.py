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
import traceback
from collections import namedtuple
from filecmp import cmp
from itertools import islice
from os.path import abspath, basename, exists, getctime, getsize, isdir, join, normpath
from pathlib import Path
from random import shuffle
from re import sub
from string import capwords
from urllib import parse

from mutagen import File, MutagenError, id3, mp4
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
EXPLAIN_ERROR = False
CACHE = TempCache("mkpl", max_age=30)
__version__ = "1.18.1"

Playlist = namedtuple(
    "Playlist", ("files", "ext", "name", "encoding"), defaults=([], False, False, False)
)

PlaylistEntry = namedtuple(
    "PlaylistEntry", ("file", "image", "extinf"), defaults=(None, False, False)
)

# endregion


# region functions
def get_args():
    """Get command-line arguments"""

    global FILE_FORMAT, EXPLAIN_ERROR, CACHE

    parser = argparse.ArgumentParser(
        description="Command line tool to create playlist files in M3U format.",
        epilog="See latest release from https://github.com/MatteoGuadrini/mkpl",
    )
    orderby_group = parser.add_mutually_exclusive_group()
    separator_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "playlist",
        help="Playlist file",
        type=str,
        default=os.path.join(os.getcwd(), os.path.split(os.getcwd())[1]),
        nargs=argparse.OPTIONAL,
    )
    parser.add_argument("-v", "--verbose", help="Enable verbosity", action="store_true")
    parser.add_argument(
        "-V", "--version", help="Print version", action="version", version=__version__
    )
    parser.add_argument(
        "-d",
        "--directories",
        help="Directories that contains multimedia file",
        nargs=argparse.ONE_OR_MORE,
        default=[Path(".")],
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
        default="0",
        metavar="BYTES",
    )
    parser.add_argument(
        "-A",
        "--max-size",
        help="Maximum size (bytes, kb, mb, ...)",
        default="0",
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
        "-M", "--length", help="Minimum length", default=0, metavar="SECONDS", type=int
    )
    parser.add_argument(
        "-X",
        "--max-length",
        help="Maximum length",
        default=0,
        metavar="SECONDS",
        type=int,
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
    separator_group.add_argument(
        "-w", "--windows", help="Windows style folder separator", action="store_true"
    )
    separator_group.add_argument(
        "-x", "--unix", help="Unix style folder separator", action="store_true"
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
        "-N",
        "--add-info",
        help="Add file information to playlist. See EXTINF attribute",
        action="store_true",
    )
    parser.add_argument(
        "-C", "--count", help="Count elements into playlist", action="store_true"
    )
    parser.add_argument(
        "-E",
        "--explain-error",
        help="Explain error with traceback",
        action="store_true",
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

    arguments = parser.parse_args()

    # Check explain error
    if arguments.explain_error:
        EXPLAIN_ERROR = True

    # Check extension of playlist file
    if not arguments.playlist.endswith(".m3u"):
        if arguments.encoding == "UNICODE":
            if not arguments.playlist.endswith(".m3u8"):
                arguments.playlist += ".m3u8"
        else:
            arguments.playlist += ".m3u"

    # Check if playlist is not a directory
    if isdir(arguments.playlist):
        parser.error(f"{arguments.playlist} is a directory")

    # Open playlist file
    arguments.open_mode = "at+" if arguments.append else "wt"
    arguments.enabled_extensions = (
        True
        if any(
            (arguments.title, arguments.encoding, arguments.image, arguments.add_info)
        )
        else False
    )
    arguments.enabled_title = True if arguments.title else False
    arguments.enabled_encoding = True if arguments.encoding else False
    # Verify extension attribute in append mode
    if arguments.append:
        with open(arguments.playlist, mode=arguments.open_mode) as opened_playlist:
            opened_playlist.seek(0)
            first_three_lines = list(islice(opened_playlist, 3))
            for line in first_three_lines:
                if "#EXTM3U" in line:
                    arguments.enabled_extensions = True
                if "#PLAYLIST" in line:
                    arguments.enabled_title = True
                if "#EXTENC" in line:
                    arguments.enabled_encoding = True
            # Check if extensions are disabled and image is specified
            if getsize(arguments.playlist) > 0:
                if not arguments.enabled_extensions and arguments.image:
                    print(
                        f"warning: image {arguments.image} has not "
                        "been set because the extension flag"
                        " is not present in the playlist"
                    )
                    arguments.image = None

    # Check if image file exists
    if arguments.image:
        if not exists(arguments.image):
            parser.error(f"image file {arguments.image} does not exist")

    # Extend files format
    if arguments.include:
        FILE_FORMAT.update(
            set([fmt.strip("*").strip(".") for fmt in arguments.include])
        )

    # Select only one format
    if arguments.format:
        FILE_FORMAT = {arguments.format.strip("*").strip(".")}

    # Convert size string into number
    arguments.size = human_size_to_byte(arguments.size)
    arguments.max_size = human_size_to_byte(arguments.max_size)

    # Check link argument if it is a valid link
    if arguments.link:
        arguments.link = [
            link for link in arguments.link if re.match("https?://", link)
        ]

    # Check if other files exists
    if arguments.file:
        arguments.file = [f for f in arguments.file if os.path.exists(f)]

    # Check min-max length
    if arguments.length and arguments.length == arguments.max_length:
        parser.error("minimum and maximum length must not has the same values")
    elif arguments.max_length and arguments.length >= arguments.max_length:
        parser.error("minimum length is upper of maximum length")

    # Define cache
    if arguments.cache:
        CACHE = TempCache("mkpl", max_age=arguments.cache)
        vprint(arguments.verbose, f"use cache {CACHE.path}")
        # Clean the cache
        CACHE.clear_items()

    return arguments


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


def file_in_playlist(playlist: Playlist, file, root=None):
    """Check if file is in the playlist"""
    for f in playlist.files:
        # Get string path
        f = f.file
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
    return False


def join_playlist(playlist: Playlist, *others):
    """Join current playlist with others"""
    for file in others:
        try:
            # open playlist, remove extensions and extend current playlist file
            lines = open(file).readlines()
            playlist.files.extend(
                [
                    PlaylistEntry(line.rstrip())
                    for line in lines
                    if not line.startswith("#")
                ]
            )
        except FileNotFoundError:
            print(f"warning: {file} file not found")
        except OSError as error:
            print(f"warning: {file} generated error: {error}")


def url_chars(file):
    """URL encoding converts characters into a format that can be transmitted over the Internet."""
    return parse.quote(file, safe="/")


def report_issue(exc, tb=False):
    """Report issue"""
    print(
        "error: {0} on line {1}, with error {2}".format(
            type(exc).__name__, exc.__traceback__.tb_lineno, str(exc)
        )
    )
    if tb:
        traceback.print_exc()
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


def get_track(file: PlaylistEntry):
    """Get file by track for sort"""
    file = open_multimedia_file(file.file)
    if file and hasattr(file, "tags"):
        if isinstance(file.tags, id3.ID3Tags):
            default = id3.TRCK(text="0")
            ret = file.tags.get("TRCK", default)[0]
        elif isinstance(file.tags, mp4.MP4Tags):
            ret = file.tags.get("trkn", [(0, 0)])[0][0]
        if isinstance(ret, str) and ret.isdecimal():
            return int(ret)
    return 0


def get_year(file: PlaylistEntry):
    """Get file by year for sort"""
    file = open_multimedia_file(file.file)
    if file and hasattr(file, "tags"):
        if isinstance(file.tags, id3.ID3Tags):
            default = id3.TDOR(text=["0000"])
            tags = file.tags.get("TDOR", default)
            if isinstance(tags, str):
                return tags
            elif isinstance(tags, (tuple, list)):
                return tags[0]
        elif isinstance(file.tags, mp4.MP4Tags):
            tags = file.tags.get("\xa9day", ["0000"])
            if isinstance(tags, str):
                return tags
            elif isinstance(tags, (tuple, list)):
                return tags[0]
    return "0000"


def get_length(file):
    """Get file by length for sort"""
    if isinstance(file, PlaylistEntry):
        file = open_multimedia_file(file.file)
    else:
        file = open_multimedia_file(file)
    if file and hasattr(file, "info"):
        return file.info.length if hasattr(file.info, "length") else 0.1
    return 0.1


def get_ctime(file: PlaylistEntry):
    """Get file by creation time for sort"""
    return getctime(file.file)


def get_size(file: PlaylistEntry):
    """Get file by size for sort"""
    return os.path.getsize(file.file)


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
    return False


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


def escape_newlines(string: str):
    """Escape newline character"""
    return string.replace("\n", "\\n")


def make_extinf(file):
    """Compose EXTINF attribute"""
    global AUDIO_FORMAT

    # String format EXTINF attribute: %seconds%,"%artist% - %title%"
    extinf_str = "{},{} - {}"
    # Check type of file
    ext = os.path.splitext(file)[1].replace(".", "").lower()
    if ext in AUDIO_FORMAT:
        file = open_multimedia_file(file)
        length = int(file.info.length) if hasattr(file.info, "length") else -1
        if isinstance(file.tags, id3.ID3Tags):
            artist = file.tags.get("TPE1", "")
            title = file.tags.get("TIT2", "")
        elif isinstance(file.tags, mp4.MP4Tags):
            artist = file.tags.get("\xa9ART", [""])[0]
            title = file.tags.get("\xa9nam", [""])[0]
        return extinf_str.format(length, artist, title).replace("\n", " ")
    return "Unknown extra infos"


def write_playlist(
    playlist_file: str,
    open_mode: str,
    playlist: Playlist,
    max_tracks: int = None,
):
    """Write playlist into file"""
    encoding = playlist.encoding if playlist.encoding else None
    with open(
        playlist_file,
        mode=open_mode,
        encoding="UTF-8" if encoding == "UNICODE" else encoding,
        errors="ignore",
    ) as pl:
        # Enable playlist extension
        if playlist.ext:
            pl.write("#EXTM3U\n")
            if playlist.name:
                pl.write(f"#PLAYLIST:{capwords(playlist.name)}\n")
            if playlist.encoding:
                pl.write(f"#EXTENC:{playlist.encoding}\n")
        for file in playlist.files[:max_tracks]:
            if file.image:
                pl.write(f"#EXTIMG:{file.image}\n")
            if file.extinf:
                pl.write(f"#EXTINF:{file.extinf}\n")
            pl.write(file.file + "\n")


@CACHE
def make_playlist(
    directories,
    file_formats,
    extension=False,
    title=False,
    encoding=False,
    pattern=False,
    image=False,
    infos=False,
    exclude_pattern=None,
    sortby_name=False,
    sortby_date=False,
    sortby_track=False,
    sortby_year=False,
    sortby_size=False,
    sortby_length=False,
    sortby_shuffle=False,
    recursive=False,
    exclude_dirs=None,
    unique=False,
    absolute=False,
    min_size=0,
    max_size=0,
    min_length=0,
    max_length=0,
    url_char=False,
    windows=False,
    unix=False,
    interactive=False,
    links=None,
    other_files=None,
    verbose=False,
):
    """Make playlist list"""
    filelist = Playlist([], extension, title, encoding)
    exclude_dirs = [] if exclude_dirs is None else exclude_dirs
    for directory in directories:
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
                # Check minimum file size
                if min_size and size <= min_size:
                    continue
                # Check maximum file size
                if max_size and size >= max_size:
                    continue
                # Check minimum length
                if min_length and get_length(file) <= min_length:
                    continue
                # Check maximum length
                if max_length and get_length(file) >= max_length:
                    continue
                if interactive:
                    if not confirm(file):
                        continue
                vprint(verbose, f"add multimedia file {file}")
                # Substitute with Windows separator
                if windows:
                    file = unix_to_dos(file)
                # Substitute with Unix separator
                elif unix:
                    file = unix_to_dos(file, viceversa=True)
                # URL chars
                if url_char:
                    file = url_chars(file)
                # Normalize file path
                file = escape_newlines(file)
                # Append entry file into playlist
                entry = PlaylistEntry(
                    file,
                    image,
                    make_extinf(file) if infos else infos,
                )
                filelist.files.append(entry)
    # Add link
    if links:
        filelist.files.extend(
            [
                PlaylistEntry(
                    link,
                    image,
                    False,
                )
                for link in links
            ]
        )
    # Add other files
    if other_files:
        filelist.files.extend(
            [
                PlaylistEntry(
                    other_file,
                    image,
                    make_extinf(other_file) if infos else infos,
                )
                for other_file in other_files
            ]
        )
    # Check sort
    if sortby_name:
        filelist.files.sort()
    elif sortby_date:
        filelist.files.sort(key=get_ctime)
    elif sortby_track:
        filelist.files.sort(key=get_track)
    elif sortby_year:
        filelist.files.sort(key=get_year)
    elif sortby_size:
        filelist.files.sort(key=get_size)
    elif sortby_length:
        filelist.files.sort(key=get_length)
    elif sortby_shuffle:
        shuffle(filelist.files)
    return filelist


def main_cli():
    """Make a playlist file"""

    args = get_args()
    vprint(
        args.verbose,
        f"formats={FILE_FORMAT}, recursive={args.recursive}, "
        f"pattern={args.pattern}, split={args.split}",
    )
    if args.split:
        for directory in args.directories:
            playlist_name = basename(normpath(directory))
            # Make multimedia list
            playlist = make_playlist(
                [directory],
                FILE_FORMAT,
                pattern=args.pattern,
                exclude_pattern=args.exclude_pattern,
                extension=args.enabled_extensions,
                title=capwords(directory),
                encoding=args.encoding,
                image=args.image,
                infos=args.add_info,
                sortby_name=args.orderby_name,
                sortby_date=args.orderby_date,
                sortby_track=args.orderby_track,
                sortby_year=args.orderby_year,
                sortby_size=args.orderby_size,
                sortby_length=args.orderby_length,
                sortby_shuffle=args.shuffle,
                recursive=args.recursive,
                exclude_dirs=args.exclude_dirs,
                unique=args.unique,
                absolute=args.absolute,
                min_size=args.size,
                max_size=args.max_size,
                min_length=args.length,
                max_length=args.max_length,
                url_char=args.url_chars,
                windows=args.windows,
                unix=args.unix,
                interactive=args.interactive,
                links=args.link,
                other_files=args.file,
                verbose=args.verbose,
            )
            if playlist.files:
                vprint(args.verbose, f"write playlist {playlist_name}")
                # Write playlist to file
                extension = ".m3u" if args.encoding != "UNICODE" else ".m3u8"
                write_playlist(playlist_name + extension, args.open_mode, playlist)
    # Make multimedia list
    playlist = make_playlist(
        args.directories,
        FILE_FORMAT,
        pattern=args.pattern,
        exclude_pattern=args.exclude_pattern,
        extension=args.enabled_extensions,
        title=args.title,
        encoding=args.encoding,
        image=args.image,
        infos=args.add_info,
        sortby_name=args.orderby_name,
        sortby_date=args.orderby_date,
        sortby_track=args.orderby_track,
        sortby_year=args.orderby_year,
        sortby_size=args.orderby_size,
        sortby_length=args.orderby_length,
        sortby_shuffle=args.shuffle,
        recursive=args.recursive,
        exclude_dirs=args.exclude_dirs,
        unique=args.unique,
        absolute=args.absolute,
        min_size=args.size,
        max_size=args.max_size,
        min_length=args.length,
        max_length=args.max_length,
        url_char=args.url_chars,
        windows=args.windows,
        unix=args.unix,
        interactive=args.interactive,
        links=args.link,
        other_files=args.file,
        verbose=args.verbose,
    )

    # Join other playlist files
    if args.join:
        join_playlist(playlist, *args.join)

    if playlist.files:
        vprint(args.verbose, f"write playlist {args.playlist}")
        # Write playlist to file
        write_playlist(args.playlist, args.open_mode, playlist, args.max_tracks)
    else:
        print(
            f"warning: no multimedia files are found here: {','.join([abspath(dir) for dir in args.directories])}"
        )

    # Count files into playlist
    if args.count:
        print(len(playlist.files))


def main():
    """Main function of make playlist"""
    try:
        main_cli()
    except Exception as err:
        report_issue(err, tb=EXPLAIN_ERROR)


# endregion

# region main
if __name__ == "__main__":
    main()

# endregion
