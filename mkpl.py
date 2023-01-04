#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# mkpl -- mkpl
#
#     Copyright (C) 2022 Matteo Guadrini <matteo.guadrini@hotmail.it>
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
from os.path import join, exists, isdir, getsize
from pathlib import Path
from random import shuffle

# endregion

# region globals
FILE_FORMAT = {'mp1', 'mp2', 'mp3', 'mp4', 'aac', 'ogg', 'wav', 'wma',
               'avi', 'xvid', 'divx', 'mpeg', 'mpg', 'mov', 'wmv'}
__version__ = '1.4.0'


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
    parser.add_argument("-p", "--pattern", help="Regular expression inclusion pattern", default='.*')
    parser.add_argument("-f", "--format", help="Select only a file format", type=str, choices=FILE_FORMAT)
    parser.add_argument("-z", "--size", help="Start size in bytes", type=int, default=1, metavar='BYTES')
    parser.add_argument("-m", "--max-tracks", help="Maximum number of tracks", type=int, default=None, metavar='NUMBER')
    parser.add_argument("-t", "--title", help="Playlist title", default=None)
    parser.add_argument("-g", "--encoding", help="Text encoding", choices=('UTF-8', 'ASCII', 'UNICODE'), default=None)
    parser.add_argument("-I", "--image", help="Playlist image", default=None)
    parser.add_argument("-l", "--link", help="Add remote file links", nargs=argparse.ONE_OR_MORE, default=[])
    parser.add_argument("-r", "--recursive", help="Recursive search", action='store_true')
    parser.add_argument("-a", "--absolute", help="Absolute file name", action='store_true')
    parser.add_argument("-s", "--shuffle", help="Casual order", action='store_true')
    parser.add_argument("-u", "--unique", help="The same files are not placed in the playlist", action='store_true')
    parser.add_argument("-c", "--append", help="Continue playlist instead of override it", action='store_true')
    parser.add_argument("-w", "--windows", help="Windows style folder separator", action='store_true')

    args = parser.parse_args()

    # Check extension of playlist file
    if not args.playlist.endswith('.m3u'):
        if args.encoding == 'UNICODE':
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
        FILE_FORMAT.update(set(args.include))

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
        vprint(verbose, f"write playlist {pl.name}")
        if image and enabled_extensions:
            joined_string = f"\n#EXTIMG: {image}\n"
        else:
            joined_string = '\n'
        end_file_string = '\n'
        # Write extensions if exists
        if ext_part:
            pl.write('\n'.join(files[:ext_part]) + joined_string)
        # Write all multimedia files
        pl.write(joined_string.join(files[ext_part:max_tracks]) + end_file_string)


def make_playlist(directories,
                  pattern,
                  recursive=False,
                  exclude_dirs=None,
                  unique=False,
                  absolute=False,
                  min_size=1,
                  windows=False,
                  verbose=False):
    """Make playlist list"""
    filelist = list()
    # Walk to directories
    for directory in directories:
        # Build a Path object
        path = Path(directory)
        root = path.parent
        vprint(verbose, f"current directory={path}, root={root}")
        for fmt in FILE_FORMAT:
            # Check recursive
            folder = '**/*' if recursive else '*'
            for file in path.glob(folder + f'.{fmt}'):
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


def add_extension(filelist, cli_args):
    """Add extension to playlist list"""
    if not isinstance(filelist, list):
        raise ValueError(f'{filelist} is not a list object')

    # Check if playlist is an extended M3U
    cli_args.ext_part = 0
    if cli_args.title or cli_args.encoding or cli_args.image:
        if not cli_args.enabled_extensions:
            filelist.insert(0, '#EXTM3U')
            cli_args.enabled_extensions = True
            cli_args.ext_part += 1
            if cli_args.max_tracks:
                cli_args.max_tracks += 1

        # Set title
        if cli_args.title:
            if not cli_args.enabled_title:
                filelist.insert(1, f'#PLAYLIST: {capwords(cli_args.title)}')
                cli_args.ext_part += 1
                if cli_args.max_tracks:
                    cli_args.max_tracks += 1
            else:
                print("warning: title is already configured")

        # Set encoding
        if cli_args.encoding:
            if not cli_args.enabled_encoding:
                filelist.insert(1, f'#EXTENC: {cli_args.encoding}')
                cli_args.ext_part += 1
                if cli_args.max_tracks:
                    cli_args.max_tracks += 1
            else:
                print("warning: encoding is already configured")


def main():
    """Make a playlist file"""

    args = get_args()
    vprint(args.verbose, f"formats={FILE_FORMAT}, recursive={args.recursive}, pattern={args.pattern}")

    # Make multimedia list
    multimedia_files = make_playlist(args.directories,
                                     args.pattern,
                                     recursive=args.recursive,
                                     exclude_dirs=args.exclude_dirs,
                                     unique=args.unique,
                                     absolute=args.absolute,
                                     min_size=args.size,
                                     windows=args.windows,
                                     verbose=args.verbose)

    # Add link
    multimedia_files.extend(args.link)

    # Build a playlist
    if multimedia_files:

        # Check shuffle
        if args.shuffle:
            shuffle(multimedia_files)

        # Add extension to playlist
        add_extension(multimedia_files, args)

        # Write playlist to file
        write_playlist(args.opened_playlist,
                       args.open_mode,
                       multimedia_files,
                       enabled_extensions=args.enabled_extensions,
                       image=args.image,
                       ext_part=args.ext_part,
                       max_tracks=args.max_tracks,
                       verbose=args.verbose)
    else:
        print(f'warning: no multimedia files are found here: {",".join(args.directories)}')


# endregion

# region main
if __name__ == "__main__":
    main()

# endregion
