#!/usr/bin/env python
"""
Goal: Implement the entry point for generating OneFlorda IDs

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

import time
import argparse
from datetime import timedelta
from onefl import logutils
from onefl.config import Config
from onefl.link_generator import LinkGenerator
from onefl.version import __version__

logger = logutils.get_a_logger(__file__)

# The config file is looked up relative to this "root" folder
ROOT_PATH = '.'
DEFAULT_SETTINGS_FILE = 'config/settings_linker.py'


def main():
    """
    Configure the logger object and read the command line arguments
    for invoking the generator.

    .. seealso::

        :meth:`LinkGenerator.generate`

    """
    LinkGenerator.configure_logger(logger)
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
        default='.',
        help='input directory name')
    parser.add_argument(
        '-o', '--outputdir',
        default='.',
        help='output directory name')

    parser.add_argument(
        '-p', '--partner',
        required=True,
        help='output directory name')

    parser.add_argument(
        '-a', '--ask', action='store_true', default=False,
        help='ask for confirmation to proceed')

    args = parser.parse_args()

    if args.version:
        import sys
        print("deduper, version {}".format(__version__))
        sys.exit()

    config = Config(root_path=ROOT_PATH, defaults={})
    config.from_pyfile(args.config)
    start = time.monotonic()
    success = LinkGenerator.generate(config=config,
                                     inputdir=args.inputdir,
                                     outputdir=args.outputdir,
                                     partner=args.partner,
                                     ask=args.ask,
                                     create_tables=False
                                     )
    success = True
    end = time.monotonic()
    elapsed = (end - start)

    if success:
        logger.info("Done. Process duration: {}"
                    .format(str(timedelta(seconds=elapsed))))
    else:
        logger.error("Failed!")

if __name__ == '__main__':
    main()
