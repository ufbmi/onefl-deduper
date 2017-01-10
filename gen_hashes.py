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
from onefl.hash_generator import HashGenerator
from onefl.normalized_patient import NormalizedPatient
logger = logutils.get_a_logger(__file__)


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
    parser.add_argument(
        '-i', '--inputdir',
        required=True,
        help='input directory name')
    parser.add_argument(
        '-o', '--outputdir',
        required=True,
        help='output directory name')

    args = parser.parse_args()
    start = time.monotonic()
    success = HashGenerator.generate(args.inputdir, args.outputdir)
    end = time.monotonic()
    elapsed = (end - start)

    if success:
        logger.info("Done. Process duration: {}"
                    .format(str(timedelta(seconds=elapsed))))
    else:
        logger.error("Failed!")

if __name__ == '__main__':
    main()
