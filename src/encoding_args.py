from dataclasses import dataclass
from pathlib import Path

@dataclass
class EncodingArgs:
    file_location: Path
    shrink: float
    preset: int
    audio: str
    output_file: Path
    min_bitrate: int
    max_bitrate: int
    skip_bitrate: int
    backup_folder: Path | None

    def __init__(
        self,
        file_location: Path,
        shrink: float,
        preset: int,
        audio: str,
        output_file: Path,
        min_bitrate: int,
        max_bitrate: int,
        skip_bitrate: int,
        backup_folder: Path | None,
    ):
        self.file_location = file_location
        self.shrink = shrink
        self.preset = preset
        self.audio = audio
        self.output_file = output_file
        self.min_bitrate = min_bitrate
        self.max_bitrate = max_bitrate
        self.skip_bitrate = skip_bitrate
        self.backup_folder = backup_folder
