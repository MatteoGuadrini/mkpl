# Release notes

## 1.15.0
Jun 13, 2025

- Add default for `playlist` positional argument with current directory name, refs# 16
- Fix issue #17

## 1.14.0
May 16, 2025

- Add `max-length` cli argument
- Add `max-size` cli argument

## 1.13.0
May 03, 2025

- Add `explain-error` cli argument
- Add _mp4_ tag support

## 1.12.0
Mar 31, 2025

- Add `length` cli argument

## 1.11.0
Nov 22, 2024

- Add `exclude-pattern` cli argument
- Add `file` cli argument
- Add **human_size_to_byte** function
- Fix `link` argument if it is a valid http link

## 1.10.0
Jul 25, 2024

- Add `url-chars` cli argument
- Add `cache` cli argument, refs #10
- Add **url_chars** function, refs #12
- Fix _mkv_ extension, refs #13
- Fix **orderby-track** return function, refs #14

## 1.9.0
May 09, 2024

- Add `orderby-size` cli argument
- Add `orderby-length` cli argument
- Add `interactive` cli argument
- Add `count` cli argument
- Add **confirm** function for _interactive_ mode

## 1.8.0
Aug 03, 2023

- Refactor _make_playlist_ function for better performance
- Add standard path on unique argument
- Add _open_multimedia_file_ function
- Add `orderby-year` cli argument
- Add `join` cli argument
- Add mkpl logo
- Migrate to pyproject.toml installation
- Fix absolute name into _make_playlist_ function, refs #8
- Fix check if playlist is not empty before writes it to file
- Fix check extension of file before open tags

## 1.7.0
Jun 12, 2023

- Add _find_pattern_ function
- Add find pattern for _ID3 tags_
- Add `orderby-track` cli argument: see issue #6
- Add _encoding_ and _ignore error handling_ to `write_playlist` function: see issue #7
- Fix reset _enabled_extensions_ with split argument

## 1.6.0
Mar 07, 2023

- Add `-o` or `--orderby-name` cli argument: see issue #4
- Add `-O` or `--orderby-date` cli argument: see issue #4
- Add support for _'opus'_ file format: see issue #5
- Fix check playlist extension for _m3u8_ format
- Fix asterisk and dot char into include argument

## 1.5.0
Jan 13, 2023

- _Refactor module_; all business logic into functions: **make_playlist**, **write_playlist** and **add_extension**
- Add `-S` or `--split` cli argument: see issue #2
- Fix check image and append mode
- Fix _enabled_encoding_ when is just enabled

## 1.4.0
Nov 10, 2022

- Add _capwords_ function for title of playlist
- Add checks for extension attribute in append mode
- Add warnings for extensions enabled
- Add checks for image file

## 1.3.0
Oct 24, 2022

- Add _verbose_ argument
- Add _vprint_ function
- Fix shuffle and extension issue #1
- Fix new line in the append mode
- Fix epilog message
- Fix join with extension tags

## 1.2.0
Sep 28, 2022

- Add _windows_ argument
- Fix file extension with UNICODE encode

## 1.1.0
Sep 19, 2022

- Add _title_ argument
- Add _encoding_ argument
- Add _image_ argument
- Add _link_ argument

## 1.0.1
Sep 9, 2022

- Add _file_ formats
- Add _get_args_ function
- Add _file_in_playlist_ function
- Add _main_ function
- Add _playlist_ maker