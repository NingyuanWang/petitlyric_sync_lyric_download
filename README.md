# petitlyric_sync_lyric_download
Download sync lyric from petitlyric as lrc files

This applet downloads sync lyric from petitlyric(プチリリ), and store them locally as lrc files. 
The lyric searching is based on the METADATA of the audio files, namely the artist name, track title, and album title. 
Since the synced lyric is matched only on these data, it requires the input audio file to have accurate metadata, and is of same length as the commonly distributed version.

## Installation
Use the command
```
pip install -r requirements.txt
```
to setup the system, assuming python is already installed on the system.
## Basic usage
The script ```petitlyric_folder_gui.py``` gives a basic gui that allows the user to select a folder, and look for lyrics for all audio files inside the folder (recursively).
On a windows system, if .py files are correctly associated with python, then double-clicking the file should suffice.

The script ```petitlyrics.py``` allows more functionality, and can be used as a library for other programs.

## Disclaimer
This applet is not affiliated with petitlyric, comes with no warranty, and may not be actively taken care of.
