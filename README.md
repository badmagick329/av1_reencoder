# Description

Re-encode video files to AV1 with ffmpeg. The primary use case for this
script is to re-encode video files with a very high bitrate to a more
compact format. The default settings will reduce the bitrate by 30%

# Examples

### Re-encode all videos in a dir

Note: The original files will be removed unless -b is specified

```sh
python src/main.py -i ./videos
```

### Re-encode multiple videos and copy originals to a backup dir

```sh
python src/main.py -b -i ./videos/video1.webm ./videos/video2.webm
```

### Reduce bitrate by 50%, backup original, do not go below 2M bitrate

```sh
python src/main.py -i /tmp/input.webm -s 0.5 -b -mn 2
```

# Flags

```
-i INPUT [INPUT ...], --input INPUT [INPUT ...]
    Input files or directories. Directories will not be searched recursively. Only video
    files with known extensions will be processed.
```

```
-s SHRINK, --shrink SHRINK
    Shrink bitrate by default=0.30. i.e 30 percent
```

```
-p PRESET, --preset PRESET
    Preset. 0-13. Higher = Faster default=8
```

```
-a AUDIO, --audio AUDIO
    Audio codec setting. You can write any ffmpeg flags here and they will be inserted into
    the final command. default=-c:a copy
```

```
-b, --backup, --no-backup
    Backup original files. If this is set, a backup folder will be created and the original
    files will be copied there. (default: No backup)
```

```
-mx MAX_VIDEO_BITRATE, --max_video_bitrate MAX_VIDEO_BITRATE
    Max video bitrate in Mbps. default=45. 100 is the max
```

```
-mn MIN_VIDEO_BITRATE, --min_video_bitrate MIN_VIDEO_BITRATE
    Min video bitrate in Mbps. default=1
```
