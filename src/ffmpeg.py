import json
import shutil
import subprocess
from pathlib import Path

from encoding_args import EncodingArgs


class Ffmpeg:
    encoding_args: EncodingArgs

    def __init__(self, encoding_args: EncodingArgs):
        self.args = encoding_args

    def encode(self):
        input_codec = self._get_codec(self.args.input_file)
        if input_codec == "av1":
            print(f"{self.args.input_file} is already av1 encoded")
            return

        out_bitrate = self._get_output_bitrate()
        if not out_bitrate:
            return

        if self.args.backup_folder:
            copied_file = self._create_backup_file(
                self.args.input_file, self.args.backup_folder
            )
            assert copied_file is not None, "Backup failed"

        cmd = self._create_run_command(out_bitrate)
        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd)
        assert self.args.output_file.exists(), "Encoding failed"

        final_output = self._cleanup_and_rename()
        print(f"Created: {final_output}")

    @classmethod
    def _get_codec(cls, file: Path) -> str:
        ffmpeg_cmd = (
            "ffprobe -v quiet -select_streams v:0 -show_entries "
            "stream=codec_name -of default=noprint_wrappers=1:nokey=1 "
            f"{cls._escape_and_quote(file)}"
        )
        fout = subprocess.run(
            ffmpeg_cmd, stdout=subprocess.PIPE, shell=True
        ).stdout.decode("utf-8")
        return fout.lower().strip()

    @classmethod
    def _escape_and_quote(cls, file: Path) -> str:
        name = str(file).replace('"', '\\"')
        return f'"{name}"'

    @classmethod
    def _get_bitrate(cls, file: Path) -> int:
        cmd = (
            "ffprobe -v error -select_streams v -show_entries format=bit_rate "
            "-of default=noprint_wrappers=1:nokey=1 "
            f"{cls._escape_and_quote(file)}"
        )
        fout = subprocess.run(
            cmd, stdout=subprocess.PIPE, shell=True
        ).stdout.decode("utf-8")
        try:
            return int(fout)
        except ValueError:
            pass
        cmd = (
            "ffprobe -v quiet -select_streams v:0 -show_entries "
            "stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "
            f"{cls._escape_and_quote(file)}"
        )
        fout = subprocess.run(
            cmd, stdout=subprocess.PIPE, shell=True
        ).stdout.decode("utf-8")
        try:
            return int(fout)
        except ValueError:
            raise ValueError(f"Could not get bitrate from {file}")

    def _get_output_bitrate(self):
        bitrate = self._get_bitrate(self.args.input_file)
        out_bitrate = int(bitrate - bitrate * self.args.shrink)
        if out_bitrate < self.args.skip_bitrate:
            print(
                f"Output bitrate {out_bitrate} is less "
                f"than min bitrate threshold {self.args.skip_bitrate}. Skipping..."
            )
            return None

        if out_bitrate > self.args.max_bitrate:
            return self.args.max_bitrate
        if out_bitrate < self.args.min_bitrate:
            return self.args.min_bitrate
        return out_bitrate

    def _cleanup_and_rename(self) -> Path:
        self.args.input_file.unlink()
        output_suffix = self.args.output_file.suffix
        overwrite_path = self.args.input_file.with_suffix(output_suffix)
        output_file = self.args.output_file.rename(str(overwrite_path))
        assert (
            output_file.exists()
        ), f"Expected output file {output_file} not found"
        return output_file

    def _create_run_command(self, out_bitrate: int) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-i",
            str(self.args.input_file),
            "-c:v",
            "libsvtav1",
            "-b:v",
            str(out_bitrate),
            "-preset",
            str(self.args.preset),
            *self.args.audio.split(" "),
            "-fps_mode",
            "vfr",
            str(self.args.output_file),
        ]

    @classmethod
    def _create_backup_file(cls, file: Path, backup_folder: Path) -> Path:
        backup_location = backup_folder / file.name
        shutil.copy2(file, backup_location)
        return backup_location
