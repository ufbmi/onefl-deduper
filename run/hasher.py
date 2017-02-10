#!/usr/bin/env python
"""
Goal: Implement the entry point for the hash generator

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

import time
import argparse
from datetime import timedelta
from onefl import logutils
from onefl.config import Config
from onefl.hash_generator import HashGenerator
from onefl.normalized_patient import NormalizedPatient
from onefl.version import __version__

logger = logutils.get_a_logger(__file__)

# The config file is looked up relative to this "root" folder
ROOT_PATH = '.'
DEFAULT_SETTINGS_FILE = 'config/settings_hasher.py'


def main():
    """
    Configure the logger object and read the command line arguments
    for invoking the generator.

    .. seealso::

        :meth:`HashGenerator.generate`

    """
    HashGenerator.configure_logger(logger)
    NormalizedPatient.configure_logger(logger)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version",
                        default=False,
                        action='store_true',
                        help="Show the version number")

    parser.add_argument("-c", "--config",
                        default=DEFAULT_SETTINGS_FILE,
                        help="Application config file")
    parser.add_argument(
        '-i', '--inputdir',
        # required=True,
        default='.',
        help='input directory name')
    parser.add_argument(
        '-o', '--outputdir',
        # required=True,
        default='.',
        help='output directory name')

    args = parser.parse_args()

    if args.version:
        import sys
        print("deduper, version {}".format(__version__))
        sys.exit()

    config = Config(root_path=ROOT_PATH, defaults={})
    config.from_pyfile(args.config)
    start = time.monotonic()
    success = HashGenerator.generate(config, args.inputdir, args.outputdir)
    end = time.monotonic()
    elapsed = (end - start)

    if success:
        logger.info("Done. Process duration: {}"
                    .format(str(timedelta(seconds=elapsed))))
    else:
        logger.error("Failed!")

if __name__ == '__main__':
    main()
