#!/usr/bin/env python3
from pathlib import Path

import ffmpeg
from argument_parser import create_arg_parser


def main():
    initial_setup()


def initial_setup():
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()

    filenames = parsed_args.input
    assert len(filenames) > 0, "No input files"
    shrink = parsed_args.shrink
    folder_location = Path(filenames[0]).parent
    preset = parsed_args.preset
    backup = parsed_args.backup
    audio = parsed_args.audio
    backup_folder = None
    if backup:
        backup_folder = create_backup_folder(folder_location)
    print("Start")
    print(f"Files: {filenames}")
    print(f"Shrink: {shrink}")
    print(f"Backup folder: {backup_folder}")
    print("End")
    for filename in filenames:
        print(f"Processing {filename}")
        process_file(
            filename=filename,
            shrink=shrink,
            preset=preset,
            backup_folder=backup_folder,
            audio=audio,
        )


def create_backup_folder(path: Path) -> Path:
    backup_folder = path / "backup"
    backup_folder.mkdir(exist_ok=True)
    return backup_folder


def process_file(
    filename: str,
    shrink: float,
    preset: int,
    backup_folder: Path | None,
    audio: str,
):
    file_location = Path(filename)
    output_file = file_location
    assert file_location.exists(), f"File {filename} does not exist"
    ffmpeg.encode_file(
        file_location,
        shrink,
        preset,
        audio,
        output_file,
        min_bitrate=5_000_000,
        backup_folder=backup_folder,
    )


if __name__ == "__main__":
    main()
