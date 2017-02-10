"""
Goal: store utility functions for user interaction

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import os
import sys


def check_file_exists(ask, file_name):
    """
    If ask = `True` prompt the user to continue or stop,
    otherwise pretend that the file exists.
    """
    exists = False

    if not os.path.isfile(file_name):
        if ask:
            opt = ask_yes_no("The file {} does not exist. "
                             "Continue anyway?".format(file_name))
            if not opt:
                sys.exit('Got it.')
    else:
        exists = True
    return exists


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
