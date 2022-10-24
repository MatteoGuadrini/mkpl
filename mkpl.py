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
from re import findall, sub
from filecmp import cmp
from os.path import join
from pathlib import Path
from random import shuffle

# endregion

# region globals
FILE_FORMAT = {'mp1', 'mp2', 'mp3', 'mp4', 'aac', 'ogg', 'wav', 'wma',
               'avi', 'xvid', 'divx', 'mpeg', 'mpg', 'mov', 'wmv'}
__version__ = '1.3.0'


# endregion

# region functions
def get_args():
    """Get command-line arguments"""

    global FILE_FORMAT

    parser = argparse.ArgumentParser(
        description="Make music playlist",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='Playlist file is M3U format'
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
        print('DEBUG:', *messages)


def main():
    """Make a playlist"""

    args = get_args()
    multimedia_files = list()

    # Add link
    multimedia_files.extend(args.link)

    vprint(args.verbose, f"formats={FILE_FORMAT}, recursive={args.recursive}, pattern={args.pattern}")

    # Walk to directories
    for directory in args.directories:
        # Build a Path object
        path = Path(directory)
        root = path.parent
        vprint(args.verbose, f"current directory={path}, root={root}")
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
                        vprint(args.verbose, f"add multimedia file {file}")
                        multimedia_files.append(
                            sub('/', r"\\", file) if args.windows else file
                        )

    # Build a playlist
    if multimedia_files:
        ext_part = 0
        # Check shuffle
        if args.shuffle:
            shuffle(multimedia_files)

        # Check if playlist is an extended M3U
        if args.title or args.encoding or args.image:
            multimedia_files.insert(0, '#EXTM3U')
            ext_part += 1
            if args.max_tracks:
                args.max_tracks += 1

            # Set title
            if args.title:
                multimedia_files.insert(1, f'#PLAYLIST: {args.title.capitalize()}')
                ext_part += 1
                if args.max_tracks:
                    args.max_tracks += 1

            # Set encoding
            if args.encoding:
                multimedia_files.insert(1, f'#EXTENC: {args.encoding}')
                ext_part += 1
                if args.max_tracks:
                    args.max_tracks += 1

        with args.playlist as playlist:
            joined_string = f'\n#EXTIMG: {args.image}\n' if args.image else '\n'
            # Write extensions if exists
            if ext_part:
                playlist.write('\n'.join(multimedia_files[:ext_part]) + joined_string)
            # Write all multimedia files
            playlist.write(joined_string.join(multimedia_files[ext_part:args.max_tracks]) + '\n')
    else:
        print(f'WARNING: No multimedia files are found here: {",".join(args.directories)}')


# endregion

# region main
if __name__ == "__main__":
    main()

# endregion
