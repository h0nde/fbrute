from config import *
import itertools
import os
import ctypes
import argparse
import string
import random

if os.name == "nt":
    update_stats = ctypes.windll.kernel32.SetConsoleTitleW
else:
    update_stats = lambda x: print(x)

class FilenameIterator:
    def __init__(self, charset, length, extensions):
        self.charset = charset
        self.length = length
        self.extensions = extensions
        self.position = 0
        self._fname_iter = itertools.product(
            self.charset,
            repeat=self.length
        )
        self._gen = self._make_gen()

    def _make_gen(self):
        while 1:
            fname = "".join(next(self._fname_iter))
            for ext in self.extensions:
                self.position += 1
                yield fname + ext

    def __next__(self):
        return next(self._gen)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--url",
        help="Base url",
        type=str
    )
    parser.add_argument(
        "-e",
        "--ext",
        help="File extensions (including dot at start)",
        type=str,
        nargs="+",
        default=DEFAULT_EXT
    )
    parser.add_argument(
        "-c",
        "--charset",
        help="Characters to be used within filenames",
        type=list,
        nargs="*",
        default=DEFAULT_CHARSET
    )
    parser.add_argument(
        "-l",
        "--length",
        help="Length of filenames",
        type=int,
        default=DEFAULT_LENGTH
    )
    parser.add_argument(
        "-p",
        "--proxyfile",
        help="Proxy file",
        type=argparse.FileType("r"),
        default=None
    )
    parser.add_argument(
        "-o",
        "--outputfile",
        help="Output file for links",
        type=argparse.FileType("a"),
        default=None
    )
    parser.add_argument(
        "-t",
        "--threads",
        help="Number of threads to be used",
        type=int,
        default=DEFAULT_THREADS
    )
    parser.add_argument(
        "--head",
        help="Use HEAD method for requests",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "-s",
        "--skip",
        help="Skip ahead (amount or filename)",
        default=None
    )
    parser.add_argument(
        "--debug",
        help="Debug mode",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "-d",
        "--download",
        help="Enables download mode & sets directory",
        type=str,
        default=None
    )
    parser.add_argument(
        "-x",
        "--success",
        help="Success status codes",
        type=int,
        nargs="*",
        default=DEFAULT_SUCCESS_CODES
    )
    parser.add_argument(
        "-i",
        "--ignore",
        help="Ignored status codes",
        type=int,
        nargs="*",
        default=DEFAULT_FAILED_STATUS_CODES
    )
    parser.add_argument(
        "--shuffle",
        help="Shuffle order of charset",
        action="store_true",
        default=False
    )

    args = parser.parse_args()

    args.charset = list(args.charset)
    if args.shuffle:
        random.shuffle(args.charset)

    if args.download:
        if not os.path.exists(args.download):
            os.mkdir(args.download)

    if args.proxyfile:
        with args.proxyfile as f:
            args.proxies = itertools.cycle(f.read().splitlines())
    else:
        args.proxies = None
    
    return args