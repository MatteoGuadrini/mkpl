# Release notes

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