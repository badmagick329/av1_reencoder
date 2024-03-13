import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from encoding_args import EncodingArgs


@dataclass
class Config:
    input_files: list[Path]
    shrink: float
    preset: int
    audio: str
    backup: bool
    max_video_bitrate: int
    min_video_bitrate: int
    parsed_args: Namespace

    SKIP_FILES_BELOW_BITRATE = 500_000
    VIDEO_EXTS = [
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

    def __init__(self, arg_parser: ArgumentParser) -> None:
        self._arg_parser = arg_parser
        self.parsed_args = arg_parser.parse_args()
        self.input_files = self._init_input_files()
        self.shrink = self.parsed_args.shrink
        self.preset = self.parsed_args.preset
        self.backup = self.parsed_args.backup
        self.audio = self.parsed_args.audio
        self.max_video_bitrate = self._init_max_video_bitrate()
        self.min_video_bitrate = self._init_min_video_bitrate()

    def _init_input_files(self):
        aggregated_files = list()
        valid_paths = [
            Path(p).resolve()
            for p in self.parsed_args.input
            if Path(p).exists()
        ]

        for path in valid_paths:
            aggregated_files.extend(self._get_videos_in(path))

        if not aggregated_files:
            print("No video files found at given input")
            sys.exit(1)

        return aggregated_files

    def _init_max_video_bitrate(self) -> int:
        max_bitrate = (
            self.parsed_args.max_video_bitrate
            if self.parsed_args.max_video_bitrate < 100
            else 100
        )
        return max_bitrate * 1_000_000

    def _init_min_video_bitrate(self) -> int:
        min_bitrate = (
            self.parsed_args.min_video_bitrate
            if self.parsed_args.min_video_bitrate >= 1
            else 1
        )
        return min_bitrate * 1_000_000

    def _get_videos_in(self, path: Path) -> list[Path]:
        assert path.exists()

        if path.is_dir():
            return [
                f.resolve()
                for f in path.glob("*")
                if f.suffix in self.VIDEO_EXTS
            ]

        if path.suffix in self.VIDEO_EXTS:
            return [path]

        return []

    def _create_backup_folder(self, path: Path) -> Path:
        backup_folder = path.parent / "backup"
        backup_folder.mkdir(exist_ok=True)
        assert (
            backup_folder.exists()
        ), f"Failed to create backup folder at {backup_folder}"
        return backup_folder

    def get_encoding_args(self) -> Iterator[EncodingArgs]:
        for file in self.input_files:
            yield EncodingArgs(
                input_file=file,
                shrink=self.shrink,
                preset=self.preset,
                audio=self.audio,
                output_file=self._get_output_file(file).with_suffix(".mp4"),
                min_bitrate=self.min_video_bitrate,
                max_bitrate=self.max_video_bitrate,
                skip_bitrate=self.SKIP_FILES_BELOW_BITRATE,
                backup_folder=(
                    self._create_backup_folder(file) if self.backup else None
                ),
            )

    def _get_output_file(self, file: Path) -> Path:
        orig_output_file, output_file = file, file
        ext = self.parsed_args.extension
        if ext.startswith("."):
            ext = ext[1:]
        i = 0
        while output_file.exists():
            output_file = (
                output_file.parent / f"{orig_output_file.stem}_{i}.{ext}"
            )
            i += 1
        return output_file.resolve()
