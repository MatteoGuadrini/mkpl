#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# mkpl -- mkpl
#
#     Copyright (C) 2023 Matteo Guadrini <matteo.guadrini@hotmail.it>
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
from string import capwords
from re import findall, sub
from filecmp import cmp
from pathlib import Path
from random import shuffle
from os.path import (join, exists, isdir, getsize, 
                     normpath, basename, dirname, getctime)

# endregion

# region globals
FILE_FORMAT = {'mp1', 'mp2', 'mp3', 'mp4', 'aac', 'ogg', 'wav', 'wma', 'm4a', 'aiff',
               'avi', 'xvid', 'divx', 'mpeg', 'mpg', 'mov', 'wmv', 'flac', 'alac', 'opus'}
__version__ = '1.6.0'


# endregion

# region functions
def get_args():
    """Get command-line arguments"""

    global FILE_FORMAT

    parser = argparse.ArgumentParser(
        description="Command line tool to create media playlists in M3U format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='See latest release from https://github.com/MatteoGuadrini/mkpl'
    )

    parser.add_argument("playlist", help="Playlist file", type=str)
    parser.add_argument("-v", "--verbose", help="Enable verbosity", action="store_true")
    parser.add_argument("-V", "--version", help="Print version", action='version', version=__version__)
    parser.add_argument("-d", "--directories", help="Directories that contains multimedia file",
                        nargs=argparse.ONE_OR_MORE, default=['.'])
    parser.add_argument("-e", "--exclude-dirs", help="Exclude directory paths", nargs=argparse.ONE_OR_MORE, default=[])
    parser.add_argument("-i", "--include", help="Include other file format", nargs=argparse.ONE_OR_MORE,
                        metavar='FORMAT')
    parser.add_argument("-p", "--pattern", 
                        help="Regular expression inclusion pattern", default='.*')
    parser.add_argument("-f", "--format", help="Select only a file format", type=str, choices=FILE_FORMAT)
    parser.add_argument("-z", "--size", help="Start size in bytes", type=int, 
                        default=1, metavar='BYTES')
    parser.add_argument("-m", "--max-tracks", help="Maximum number of tracks", 
                        type=int, default=None, metavar='NUMBER')
    parser.add_argument("-t", "--title", help="Playlist title", default=None)
    parser.add_argument("-g", "--encoding", help="Text encoding", choices=('UTF-8', 'ASCII', 'UNICODE'), default=None)
    parser.add_argument("-I", "--image", help="Playlist image", default=None)
    parser.add_argument("-l", "--link", help="Add remote file links", nargs=argparse.ONE_OR_MORE, default=[])
    parser.add_argument("-r", "--recursive", help="Recursive search", action='store_true')
    parser.add_argument("-a", "--absolute", help="Absolute file name", action='store_true')
    parser.add_argument("-s", "--shuffle", help="Casual order", action='store_true')
    parser.add_argument("-u", "--unique", help="The same files are not placed in the playlist", action='store_true')
    parser.add_argument("-c", "--append", help="Continue playlist instead of override it", action='store_true')
    parser.add_argument("-w", "--windows", help="Windows style folder separator", 
                        action='store_true')
    parser.add_argument("-S", "--split", help="Split playlist by directories", action='store_true')
    parser.add_argument("-o", "--orderby-name", help="Order playlist files by name", action='store_true')
    parser.add_argument("-O", "--orderby-date", help="Order playlist files by date", action='store_true')

    args = parser.parse_args()

    # Check extension of playlist file
    if not args.playlist.endswith('.m3u'):
        if args.encoding == 'UNICODE':
            if not args.playlist.endswith('.m3u8'):
                args.playlist += '.m3u8'
        else:
            args.playlist += '.m3u'

    # Check if playlist is not a directory
    if isdir(args.playlist):
        parser.error(f'{args.playlist} is a directory')

    # Open playlist file
    args.open_mode = 'at+' if args.append else 'wt'
    args.enabled_extensions = False
    args.enabled_title = False
    args.enabled_encoding = False
    # Verify extension attribute in append mode
    if args.append:
        with open(args.playlist, mode=args.open_mode) as opened_playlist:
            opened_playlist.seek(0)
            first_three_lines = opened_playlist.readlines(100)
            for line in first_three_lines:
                if '#EXTM3U' in line:
                    args.enabled_extensions = True
                if '#PLAYLIST' in line:
                    args.enabled_title = True
                if '#EXTENC' in line:
                    args.enabled_encoding = True
            # Check if extensions are disabled and image is specified
            if getsize(args.playlist) > 0:
                if not args.enabled_extensions and args.image:
                    print(f'warning: image {args.image} has not been set because the extension flag'
                          ' is not present in the playlist')
                    args.image = None

    # Check if image file exists
    if args.image:
        if not exists(args.image):
            parser.error(f'image file {args.image} does not exist')

    # Extend files format
    if args.include:
        FILE_FORMAT.update(set([fmt.strip('*').strip('.') for fmt in args.include]))

    # Select only one format
    if args.format:
        FILE_FORMAT = {args.format.strip('*').strip('.')}

    return args


def file_in_playlist(playlist, file, root=None):
    """Check if file is in the playlist"""
    for f in playlist:
        # Skip extended tags
        if f.startswith('#'):
            continue
        # Check if absolute path in playlist
        if root:
            f = join(root, f)
        # Compare two files
        if cmp(f, file):
            return True


def vprint(verbose, *messages):
    """Verbose print"""
    if verbose:
        print('debug:', *messages)


def write_playlist(playlist,
                   open_mode,
                   files,
                   enabled_extensions=False,
                   image=None,
                   ext_part=None,
                   max_tracks=None,
                   verbose=False):
    """Write playlist into file"""
    with open(playlist, mode=open_mode) as pl:
        if image and enabled_extensions:
            vprint(verbose, f"set image {image}")
            joined_string = f"\n#EXTIMG: {image}\n"
        else:
            joined_string = '\n'
        end_file_string = '\n'
        # Write extensions if exists
        if ext_part:
            pl.write('\n'.join(files[:ext_part]) + joined_string)
        # Write all multimedia files
        vprint(verbose, f"write playlist {pl.name}")
        pl.write(joined_string.join(files[ext_part:max_tracks]) + end_file_string)


def make_playlist(directory,
                  pattern,
                  file_formats,
                  sortby_name=False,
                  sortby_date=False,
                  recursive=False,
                  exclude_dirs=None,
                  unique=False,
                  absolute=False,
                  min_size=1,
                  windows=False,
                  verbose=False):
    """Make playlist list"""
    filelist = list()
    # Check if directory exists
    if not exists(directory):
        print(f'warning: {directory} does not exists')
        return filelist
    # Check if is a directory
    if not isdir(directory):
        print(f'warning: {directory} is not a directory')
        return filelist
    # Build a Path object
    path = Path(directory)
    root = path.parent
    vprint(verbose, f"current directory={path}, root={root}")
    for fmt in file_formats:
        # Check recursive
        folder = '**/*' if recursive else '*'
        files = path.glob(folder + f'.{fmt}')
        # Check sort
        if sortby_name:
            files = sorted(files)
        if sortby_date:
            files = sorted(files, key=getctime)
        for file in files:
            # Check if in exclude dirs
            if any([e_path in str(file) for e_path in exclude_dirs]):
                continue
            # Check if file is in playlist
            if unique:
                if file_in_playlist(filelist,
                                    str(file),
                                    root=root if not absolute else None):
                    continue
            # Check absolute file names
            size = file.stat().st_size
            file = str(file) if absolute else str(file.relative_to(path.parent))
            # Check re pattern
            if findall(pattern, file):
                # Check file size
                if size >= min_size:
                    vprint(verbose, f"add multimedia file {file}")
                    filelist.append(
                        sub('/', r"\\", file) if windows else file
                    )
    return filelist


def add_extension(filelist, cli_args, verbose=False):
    """Add extension to playlist list"""
    if not isinstance(filelist, list):
        raise ValueError(f'{filelist} is not a list object')

    # Check if playlist is an extended M3U
    cli_args.ext_part = 0
    if cli_args.title or cli_args.encoding or cli_args.image:
        if not cli_args.enabled_extensions:
            filelist.insert(0, '#EXTM3U')
            vprint(verbose, "enable extension flag")
            cli_args.enabled_extensions = True
            cli_args.ext_part += 1
            if cli_args.max_tracks:
                cli_args.max_tracks += 1

        # Set title
        if cli_args.title:
            if not cli_args.enabled_title:
                title = capwords(cli_args.title)
                filelist.insert(1, f'#PLAYLIST: {title}')
                vprint(verbose, f"set title {title}")
                cli_args.ext_part += 1
                if cli_args.max_tracks:
                    cli_args.max_tracks += 1
            else:
                print("warning: title is already configured")

        # Set encoding
        if cli_args.encoding:
            if not cli_args.enabled_encoding:
                filelist.insert(1, f'#EXTENC: {cli_args.encoding}')
                vprint(verbose, f"set encoding {cli_args.encoding}")
                cli_args.ext_part += 1
                if cli_args.max_tracks:
                    cli_args.max_tracks += 1
            else:
                print("warning: encoding is already configured")


def _process_playlist(files, cli_args, other_playlist=None):
    """Private function cli only for process arguments and make playlist"""

    # Add link
    files.extend(cli_args.link)

    # Build a playlist
    if files:

        # Check shuffle
        if cli_args.shuffle:
            shuffle(files)

        # Add extension to playlist
        add_extension(files, cli_args, verbose=cli_args.verbose)

        # Write playlist to file
        write_playlist(other_playlist if other_playlist else cli_args.playlist,
                       cli_args.open_mode,
                       files,
                       enabled_extensions=cli_args.enabled_extensions,
                       image=cli_args.image,
                       ext_part=cli_args.ext_part,
                       max_tracks=cli_args.max_tracks,
                       verbose=cli_args.verbose)
    else:
        print(f'warning: no multimedia files are found here: {",".join(cli_args.directories)}')


def main():
    """Make a playlist file"""

    args = get_args()
    multimedia_files = list()
    vprint(args.verbose, f"formats={FILE_FORMAT}, recursive={args.recursive}, "
                         f"pattern={args.pattern}, split={args.split}")

    # Make multimedia list
    for directory in args.directories:
        directory_files = make_playlist(directory,
                                        args.pattern,
                                        FILE_FORMAT,
                                        sortby_name=args.orderby_name,
                                        sortby_date=args.orderby_date,
                                        recursive=args.recursive,
                                        exclude_dirs=args.exclude_dirs,
                                        unique=args.unique,
                                        absolute=args.absolute,
                                        min_size=args.size,
                                        windows=args.windows,
                                        verbose=args.verbose)

        multimedia_files.extend(directory_files)

        # Check if you must split into directory playlist
        if args.split:
            playlist_name = basename(normpath(directory))
            playlist_ext = '.m3u8' if args.encoding == 'UNICODE' else '.m3u'
            playlist_path = join(dirname(args.playlist), playlist_name + playlist_ext)
            _process_playlist(directory_files, args, playlist_path)

    _process_playlist(multimedia_files, args)


# endregion

# region main
if __name__ == "__main__":
    main()

# endregion
