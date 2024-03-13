#!/usr/bin/env python3
from argument_parser import create_arg_parser
from config import Config
from ffmpeg import Ffmpeg


def main():
    arg_parser = create_arg_parser()
    config = Config(arg_parser)

    for args in config.get_encoding_args():
        Ffmpeg(args).encode()


if __name__ == "__main__":
    main()
