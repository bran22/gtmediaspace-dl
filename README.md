## Description

`gtmediaspace-dl` is a simple tool to download lecture videos from `mediaspace.gatech.edu`.  It leverages the Kaltura extractor in `youtube-dl` to download playlists.

## Installation

```python
pip install gtmediaspace-dl
```

## Usage

Playlist links should be in the format: `https://mediaspace.gatech.edu/playlist/details/*`

```
gtmediaspace-dl *your playlist link here*
```

## Optional Arguments

```
--embed-subs        Embed subtitle track in downloaded video files (requires ffmpeg)
```