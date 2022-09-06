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
from re import findall
from filecmp import cmp
from os.path import join
from pathlib import Path
from random import shuffle

# endregion

# region globals
FILE_FORMAT = {'mp1', 'mp2', 'mp3', 'mp4', 'aac', 'ogg', 'wav', 'wma',
               'avi', 'xvid', 'divx', 'mpeg', 'mpg', 'mov', 'wmv'}
__version__ = '1.0.0'


# endregion

# region functions
def get_args():
    """Get command-line arguments"""

    global FILE_FORMAT

    parser = argparse.ArgumentParser(
        description="Make music playlist",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='Playlist format is m3u'
    )

    parser.add_argument("playlist", help="Playlist file", type=str)
    parser.add_argument("-v", "--version", help="Print version", action='version', version=__version__)
    parser.add_argument("-d", "--directories", help="Directories that contains multimedia file",
                        nargs=argparse.ONE_OR_MORE, default=['.'])
    parser.add_argument("-e", "--exclude-dirs", help="Exclude directory paths", nargs=argparse.ONE_OR_MORE, default=[])
    parser.add_argument("-i", "--include", help="Include other file format", nargs=argparse.ONE_OR_MORE,
                        metavar='FORMAT')
    parser.add_argument("-p", "--pattern", help="Regular expression inclusion pattern", default='.*')
    parser.add_argument("-f", "--format", help="Select only a file format", type=str, choices=FILE_FORMAT)
    parser.add_argument("-z", "--size", help="Start size in bytes", type=int, default=1, metavar='BYTES')
    parser.add_argument("-m", "--max-tracks", help="Maximum number of tracks", type=int, default=None, metavar='NUMBER')
    parser.add_argument("-r", "--recursive", help="Recursive search", action='store_true')
    parser.add_argument("-a", "--absolute", help="Absolute file name", action='store_true')
    parser.add_argument("-s", "--shuffle", help="Casual order", action='store_true')
    parser.add_argument("-u", "--unique", help="The same files are not placed in the playlist", action='store_true')
    parser.add_argument("-c", "--append", help="Continue playlist instead of override it", action='store_true')

    args = parser.parse_args()

    # Check extension of playlist file
    if not args.playlist.endswith('.m3u'):
        args.playlist += '.m3u'

    # Open playlist file
    mode = 'at' if args.append else 'wt'
    args.playlist = open(args.playlist, mode=mode)

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
        # Check if absolute path in playlist
        if root:
            f = join(root, f)
        # Compare two files
        if cmp(f, file):
            return True


def main():
    """Make a playlist"""

    args = get_args()
    multimedia_files = list()

    # Walk to directories
    for directory in args.directories:
        # Build a Path object
        path = Path(directory)
        root = path.parent
        for fmt in FILE_FORMAT:
            # Check recursive
            folder = '**/*' if args.recursive else '*'
            for file in path.glob(folder + f'.{fmt}'):
                # Check if in exclude dirs
                if any([e_path in str(file) for e_path in args.exclude_dirs]):
                    continue
                # Check if file is in playlist
                if args.unique:
                    if file_in_playlist(multimedia_files,
                                        str(file),
                                        root=root if not args.absolute else None):
                        continue
                # Check absolute file names
                size = file.stat().st_size
                file = str(file) if args.absolute else str(file.relative_to(path.parent))
                # Check re pattern
                if findall(args.pattern, file):
                    # Check file size
                    if size >= args.size:
                        multimedia_files.append(file)

    # Build a playlist
    if multimedia_files:
        # Check shuffle
        if args.shuffle:
            shuffle(multimedia_files)
        with args.playlist as playlist:
            playlist.writelines('\n'.join(multimedia_files[:args.max_tracks]))
    else:
        print(f'warning: No multimedia files found here: {",".join(args.directories)}')


# endregion

# region main
if __name__ == "__main__":
    main()

# endregion
