"""
Goal: store utility functions not specific to a module

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import binascii
import dill
import pandas as pd
import os
import sys
import unicodedata
# import hashlib
import uuid

from hashlib import sha256
from csv import QUOTE_NONE, QUOTE_ALL  # noqa
from datetime import datetime
from datetime import date

from onefl import logutils
log = logutils.get_a_logger(__file__)

# Uncomment to enable degug info
# dill.detect.trace(True)

FORMAT_DATABASE_DATE = "%Y-%m-%d"
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


def hexlify(val):
    """
    This function is used to display binary data in a friendly format.

        .. seealso::
            :meth:`LinkageEntity:friendly_hash`

    Note:
        - Without the decode() the builtin `hexlify` return the bytes for
            hexadecimal representation of the binary data.
        - The returned string is twice as long as the length of data.

    :param val: binary
    :rtype: string
    """
    return binascii.hexlify(val).decode()


def get_uuid_bin():
    """
    Note: the returned value needs to be hexlified to be human readable
    """
    uuid_text = uuid.uuid1()
    return binascii.unhexlify(str(uuid_text).replace('-', '').lower().encode())


def get_uuid():
    """ Generate a PK-friendly uuid"""
    val = str(uuid.uuid1())
    return sort_uuid(val)


def sort_uuid(val):
    return val[14:18] + val[9:13] + val[0:8] + val[19:23] + val[24:]


def apply_sha256(val):
    """ Compute sha256 sum
    :param val: the input string
    :rtype string: the sha256 hexdigest
    """
    m = sha256()
    m.update(val.encode('utf-8'))
    return m.hexdigest()


def format_date_as_string(val, fmt='%m-%d-%Y'):
    """
    :rtype str:
    :return the input value formatted as '%Y-%m-%d'

    :param val: datetime or string
    :param fmt: the input format for the date
    """
    if isinstance(val, date):
        return val.strftime(fmt)

    da = format_date(val, fmt)

    if not da:
        return ''

    return da.strftime(FORMAT_DATABASE_DATE)


def format_date(val, fmt='%m-%d-%Y'):
    """
    Transform the input string to a datetime object

    :param val: the input string for date
    :param fmt: the input format for the date
    """
    date_obj = None

    try:
        date_obj = datetime.strptime(val, fmt)
    except Exception as exc:
        log.warning("Problem formatting date: {} - {} due: {}"
                    .format(val, fmt, exc))

    return date_obj


def get_db_friendly_date_time():
    """
    :rtype: string
    :return current time in format: "2014-06-24 01:23:24"
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_file_size(file_name):
    """
    :rtype numeric: the number of bytes in a file
    """
    bytes = os.path.getsize(file_name)
    return humanize_bytes(bytes)


def humanize_bytes(bytes, precision=1):
    """Return a humanized string representation of a number of bytes."""
    # This was stollen from http://code.activestate.com/recipes/577081/
    abbrevs = (
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'bytes')
    )
    if bytes == 1:
        return '1 byte'

    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return '%.*f %s' % (precision, bytes / factor, suffix)


def frame_from_file(file_name,
                    delimiter,
                    dtype=object,
                    quoting=QUOTE_ALL,
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
        log.warning("Writing frame {} using the default (|) delimiter"
                    .format(file_name))

    try:
        df.to_csv(file_name,
                  sep=delimiter,
                  escapechar=ESCAPECHAR,
                  index=False,
                  quoting=QUOTE_NONE,
                  encoding='utf-8')
    except Exception as exc:
        log.error("Unable to write frame due: {}".format(exc))

    return True


def run_dill_encoded(what):
    fun, args = dill.loads(what)
    return fun(*args)


def apply_async(pool, fun, args, run_dill_encoded=run_dill_encoded):
    return pool.apply_async(run_dill_encoded, (dill.dumps((fun, args)),))


def ask_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return the answer
    as a boolean.

    :param question: the question displayed to the user
    :param default: the default answer if the user hits <Enter>

    """
    valid = {"y": True, "n": False}

    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()[0]

        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
