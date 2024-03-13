import shutil
import subprocess
from pathlib import Path

from encoding_args import EncodingArgs


class Ffmpeg:
    encoding_args: EncodingArgs

    def __init__(self, encoding_args: EncodingArgs):
        self.args = encoding_args

    def encode(self):
        out_bitrate = self._get_output_bitrate()
        if not out_bitrate:
            return

        if self.args.backup_folder:
            copied_file = self._create_backup_file(
                self.args.file_location, self.args.backup_folder
            )
            assert copied_file is not None, "Backup failed"

        cmd = self._create_run_command(out_bitrate)
        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd)
        assert self.args.output_file.exists(), "Encoding failed"

        final_output = self._cleanup_and_rename()
        print(f"Created: {final_output}")

    @classmethod
    def _get_bitrate(cls, file: Path) -> int:
        cmd = (
            f"ffprobe -v error -select_streams v -show_entries format=bit_rate "
            f'-of default=noprint_wrappers=1:nokey=1 "{file}"'
        )
        fout = subprocess.run(
            cmd, stdout=subprocess.PIPE, shell=True
        ).stdout.decode("utf-8")
        try:
            return int(fout)
        except ValueError:
            pass
        cmd = (
            f"ffprobe -v quiet -select_streams v:0 -show_entries "
            f'stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "{file}"'
        )
        fout = subprocess.run(
            cmd, stdout=subprocess.PIPE, shell=True
        ).stdout.decode("utf-8")
        try:
            return int(fout)
        except ValueError:
            raise ValueError(f"Could not get bitrate from {file}")

    def _get_output_bitrate(self):
        bitrate = self._get_bitrate(self.args.file_location)
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
        self.args.file_location.unlink()
        mp4_path = self.args.file_location.with_suffix(".mp4")
        output_file = self.args.output_file.rename(str(mp4_path))
        assert (
            output_file.exists()
        ), f"Expected output file {output_file} not found"
        return output_file

    def _create_run_command(self, out_bitrate: int) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-i",
            str(self.args.file_location),
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
    def _create_backup_file(
        cls, file_location: Path, backup_folder: Path
    ) -> Path:
        backup_location = backup_folder / file_location.name
        shutil.copy2(file_location, backup_location)
        return backup_location
