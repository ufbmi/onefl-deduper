#!/usr/bin/env python
"""
Goal: Implement the entry point for the hash generator

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

import os
import sys

# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen

import time
import argparse
from datetime import timedelta
from multiprocessing import freeze_support

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
    success = HashGenerator.generate(config,
                                     args.inputdir,
                                     args.outputdir,
                                     args.ask)
    end = time.monotonic()
    elapsed = (end - start)

    if success:
        logger.info("Done. Process duration: {}"
                    .format(str(timedelta(seconds=elapsed))))
    else:
        logger.error("Failed!")

if __name__ == '__main__':
    freeze_support()
    main()
