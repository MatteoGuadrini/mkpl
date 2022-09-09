#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# setup -- mkpl
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

import __info__
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='make_playlist',
    version=__info__.__version__,
    url=__info__.__homepage__,
    project_urls={
        'Documentation': __info__.__homepage__,
        'GitHub Project': __info__.__homepage__,
        'Issue Tracker': __info__.__homepage__ + '/issues'
    },
    license='GNU General Public License v3.0',
    author=__info__.__author__,
    author_email=__info__.__email__,
    maintainer=__info__.__author__,
    maintainer_email=__info__.__email__,
    description='Make M3U format playlist from command line',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"
        ],
    entry_points={
        'console_scripts': [
            'mkpl = mkpl:main',
            'make_playlist = mkpl:main',
        ]
    },
    python_requires='>=3.5'
)
