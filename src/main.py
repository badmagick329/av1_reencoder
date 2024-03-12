#!/usr/bin/env python3
from pathlib import Path

import ffmpeg
from argument_parser import create_arg_parser

SKIP_FILES_BELOW_BITRATE = 500_000


def main():
    initial_setup()


def initial_setup():
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()

    paths = parsed_args.input
    assert len(paths) > 0, "No input files"
    shrink = parsed_args.shrink
    folder_location = Path(paths[0]).parent
    preset = parsed_args.preset
    backup = parsed_args.backup
    audio = parsed_args.audio
    max_bitrate = (
        parsed_args.max_video_bitrate
        if parsed_args.max_video_bitrate < 100
        else 100
    )
    min_bitrate = (
        parsed_args.min_video_bitrate
        if parsed_args.min_video_bitrate >= 1
        else 1
    )
    max_bitrate *= 1_000_000
    min_bitrate *= 1_000_000
    backup_folder = None
    if backup:
        backup_folder = create_backup_folder(folder_location)
    video_exts = [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".webm",
        ".flv",
        ".wmv",
        ".ts",
        ".m4v",
        ".m2ts",
        ".mpg",
        ".mpeg",
    ]
    aggregated_files = list()
    for file in paths:
        if Path(file).is_dir():
            aggregated_files.extend(
                [f for f in Path(file).glob("*") if f.suffix in video_exts]
            )
            continue
        file = Path(file)
        if file.suffix in video_exts:
            aggregated_files.append(file)

    for file in aggregated_files:
        print(f"Processing {file}")
        process_file(
            file=file,
            shrink=shrink,
            preset=preset,
            backup_folder=backup_folder,
            audio=audio,
            max_bitrate=max_bitrate,
            min_bitrate=min_bitrate,
        )


def create_backup_folder(path: Path) -> Path:
    backup_folder = path / "backup"
    backup_folder.mkdir(exist_ok=True)
    return backup_folder


def process_file(
    file: Path,
    shrink: float,
    preset: int,
    backup_folder: Path | None,
    audio: str,
    max_bitrate: int,
    min_bitrate: int,
):
    assert file.exists(), f"File {file} does not exist"
    ffmpeg.encode_file(
        file,
        shrink,
        preset,
        audio,
        file,
        min_bitrate=min_bitrate,
        max_bitrate=max_bitrate,
        skip_bitrate=SKIP_FILES_BELOW_BITRATE,
        backup_folder=backup_folder,
    )


if __name__ == "__main__":
    main()
