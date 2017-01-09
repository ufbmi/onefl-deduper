"""
Goal: store utility functions not specific to a module

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import pandas as pd
# import os
import sys
import unicodedata
# import sqlalchemy as db
# import hashlib
# import uuid
from hashlib import sha256

from csv import QUOTE_NONE, QUOTE_ALL  # noqa
# from urllib import parse
# from datetime import timedelta
# from datetime import datetime
# from base64 import b64decode, b64encode
from onefl import logutils
logger = logutils.get_a_logger(__file__)


# import locale
# locale.setlocale(locale.LC_ALL, 'en_US')
ESCAPECHAR = '\\'


# table of punctuation characters + space
CHARS_TO_DELETE = dict.fromkeys(
    i for i in range(sys.maxunicode)
    if unicodedata.category(chr(i)).startswith('P') or
    not chr(i).isalnum())


def prepare_for_hashing(text):
    """
    Given a string with punctuation characters
    """
    if not text:
        return ''
    return text.translate(CHARS_TO_DELETE).lower()


def apply_sha256(val):
    """ Compute sha256 sum
    :param val: the input string
    :rtype string: the sha256 hexdigest
    """
    m = sha256()
    m.update(val.encode('utf-8'))
    return m.hexdigest()


def frame_from_file(file_name,
                    delimiter,
                    dtype=object,
                    quoting=QUOTE_NONE,
                    engine=None,
                    converters=None,
                    usecols=None,
                    index_col=None,
                    nrows=None,
                    error_bad_lines=False):
    """
    Load data frame from file.
    @see frame_to_file()

    API note: "error_bad_lines": boolean, default True
    Lines with too many fields (e.g. a csv line with too many commas)
    will by default cause an exception to be raised, and no DataFrame
    will be returned. If False, then these 'bad lines' will dropped
    from the DataFrame that is returned. (Only valid with C parser)

    """
    df = pd.read_csv(file_name,
                     sep=delimiter,
                     escapechar=ESCAPECHAR,
                     quoting=quoting,
                     dtype=dtype,
                     engine=engine,
                     converters=converters,
                     usecols=usecols,
                     index_col=index_col,
                     nrows=nrows,
                     error_bad_lines=error_bad_lines,
                     skipinitialspace=True,
                     skip_blank_lines=True,
                     low_memory=True,
                     )

    df.fillna('', inplace=True)
    df = df.applymap(str.strip)
    return df


def frame_to_file(df, file_name, delimiter="|"):
    """
    Store the dataframe to a file
    """
    if "|" == delimiter:
        logger.warning("Writing frame {} using the default (|) delimiter"
                       .format(file_name))

    try:
        df.to_csv(file_name,
                  sep=delimiter,
                  escapechar=ESCAPECHAR,
                  index=False,
                  quoting=QUOTE_NONE,
                  encoding='utf-8')
    except Exception as exc:
        logger.error("Unable to write frame due: {}".format(exc))

    return True
