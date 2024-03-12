import json
import subprocess
import sys
from pathlib import Path


def ffprobe_json(tar: str) -> dict:
    tar = tar.replace('"', '\\"')
    ffmpeg_cmd = f'ffprobe -v error -show_streams -print_format json "{tar}"'
    fout = subprocess.run(
        ffmpeg_cmd, stdout=subprocess.PIPE, shell=True
    ).stdout.decode("utf-8")
    return json.loads(fout)


def get_bitrate(file: Path) -> int:
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


def encode_file(
    file_location: Path,
    shrink: float,
    preset: int,
    audio: str,
    output_file: Path,
    min_bitrate: int,
    backup_folder: Path | None,
):
    file_location = file_location.resolve()
    orig_output_file = output_file.resolve()
    output_file = orig_output_file
    i = 0
    while output_file.exists():
        output_file = output_file.parent / f"{orig_output_file.stem}_{i}.mp4"
        i += 1
    assert (
        not output_file.exists()
    ), f"Output file {output_file} already exists"
    assert file_location.exists(), f"File {file_location} does not exist"
    print(f"Shrink: {shrink}")
    bitrate = get_bitrate(file_location)
    print(f"Bitrate: {bitrate}")
    out_bitrate = int(bitrate - bitrate * shrink)
    print(f"Original bitrate: {bitrate}. Output bitrate: {out_bitrate}")
    if out_bitrate < min_bitrate:
        print(
            f"Output bitrate {out_bitrate} is less than minimum bitrate {min_bitrate}. Skipping..."
        )
        return

    if backup_folder:
        file_location = backup_file(file_location, backup_folder)
        assert file_location is not None, "Backup failed"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(file_location),
        "-c:v",
        "libsvtav1",
        "-b:v",
        str(out_bitrate),
        "-preset",
        str(preset),
        *audio.split(" "),
        "-fps_mode",
        "vfr",
        str(output_file),
    ]
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)


def backup_file(file_location: Path, backup_folder: Path) -> Path:
    backup_location = backup_folder / file_location.name
    subprocess.run(["cp", file_location, backup_location])
    return backup_location
