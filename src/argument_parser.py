import argparse


def create_arg_parser() -> argparse.ArgumentParser:
    SHRINK_DEFAULT = 30
    PRESET_DEFAULT = 8
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        help="Input files",
        required=True,
    )

    arg_parser.add_argument(
        "-s",
        "--shrink",
        help=(
            f"Shrink bitrate by default=0.{SHRINK_DEFAULT}. "
            f"i.e {SHRINK_DEFAULT} percent"
        ),
        default=SHRINK_DEFAULT / 100,
        type=float,
    ),

    arg_parser.add_argument(
        "-p",
        "--preset",
        help=f"Preset. 0-13. Higher = Faster default={PRESET_DEFAULT}",
        default=PRESET_DEFAULT,
        type=int,
    )

    arg_parser.add_argument(
        "-a",
        "--audio",
        help=(
            "Audio codec setting. "
            "You can write any ffmpeg settings here "
            "and they will be inserted into the final command. default=-c:a copy"
        ),
        default="-c:a copy",
    )

    arg_parser.add_argument(
        "-b",
        "--backup",
        help=(
            "Backup original files. "
            "If this is set, a backup folder will be created "
            "and the original files will be copied there. "
        ),
        default=False,
    )

    try:
        validate_args(arg_parser.parse_args())
    except ValueError as e:
        arg_parser.error(str(e))

    return arg_parser


def validate_args(args: argparse.Namespace) -> None:
    if args.shrink < 0 or args.shrink > 1:
        raise ValueError("Shrink must be between 0 and 1")
    if args.preset < 0 or args.preset > 13:
        raise ValueError("Preset must be between 0 and 13")
