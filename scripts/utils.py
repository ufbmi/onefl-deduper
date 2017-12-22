"""
Goal: Store helper functions

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
from urllib import parse
import sys


def get_db_url(db_host, db_name, db_user, db_pass):
    """
    Helper function for creating the "pyodbc" connection string.

    @see /etc/freetds.conf
    @see http://docs.sqlalchemy.org/en/latest/dialects/mssql.html
    @see https://code.google.com/p/pyodbc/wiki/ConnectionStrings
    """
    params = parse.quote(
        "Driver={{FreeTDS}};Server={};Port=1433;"
        "Database={};UID={};PWD={};"
        .format(db_host, db_name, db_user, db_pass))
    return 'mssql+pyodbc:///?odbc_connect={}'.format(params)


def ask_yes_no(question, default="yes"):
    """
    From: https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input  # noqa

    Ask a yes/no question via input() and return the answer as a boolean.

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
