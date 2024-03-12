import shutil
import subprocess
from pathlib import Path


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
    max_bitrate: int,
    skip_bitrate: int,
    backup_folder: Path | None,
):
    file_location = file_location.resolve().absolute()
    orig_output_file = output_file.resolve().absolute()
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
    if out_bitrate < skip_bitrate:
        print(
            f"Output bitrate {out_bitrate} is less than min bitrate threshold {skip_bitrate}. Skipping..."
        )
        return

    if out_bitrate > max_bitrate:
        out_bitrate = max_bitrate
    if out_bitrate < min_bitrate:
        out_bitrate = min_bitrate

    if backup_folder:
        copied_file = backup_file(file_location, backup_folder)
        assert copied_file is not None, "Backup failed"

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
    if not output_file.exists():
        return
    file_location.unlink()
    mp4_path = file_location.with_suffix(".mp4")
    output_file = output_file.rename(str(mp4_path))
    assert (
        output_file.exists()
    ), f"Expected output file {output_file} not found"
    print(f"Created: {output_file}")


def backup_file(file_location: Path, backup_folder: Path) -> Path:
    backup_location = backup_folder / file_location.name
    shutil.copy2(file_location, backup_location)
    return backup_location
