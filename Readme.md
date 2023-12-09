# HeicConverter

## Introduction

A very simple command line tool to convert *.heic files to jpg. Since the available programs for windows are either paid
or not working for me, I decided to make a simple python script to help convert these files.

## Features

- Convert all HEIC files to jpg in a folder and sub-folders recursively
- Skips already existing conversions
- Keep Metadata of the original file

## Usage

1. Copy the prepared exe to the folder with heic files for convert and double click it.
2. Use Command line and append the path of interest:

~~~~
./heicConverter.exe path/to/pictures
~~~~

3. Use command line, navigate to the path of interest and start the exe located somewhere on your machine.

## Installation

### Windows

Download the latest release from the [Release Page](https://github.com/saschiwy/HeicConverter/releases) and extract it
somewhere on your machine.

### Linux / Mac

Download the repo, install the dependencies and run the script.

## Development Dependencies

Install the python package dependencies with:

~~~~
pip install -r requirements.txt
~~~~

## Create your own executable

Install pyinstaller with:

~~~~
pip install pyinstaller
~~~~

Install the dependencies, navigate with a console to the source dir and run the following commands:

~~~~
python -m PyInstaller --onefile --console heicConverter.py
~~~~

## Remarks

This software was mainly created by people at StackOverflow:
https://stackoverflow.com/questions/54395735/how-to-work-with-heic-image-file-types-in-python

## Example

![Example](doc/example.png)

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=JBK73YUVW7MGW&source=url)