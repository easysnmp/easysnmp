from __future__ import unicode_literals

import string

from .compat import ub, text_type


def strip_non_printable(value):
    """
    Removes any non-printable characters and adds an indicator to the string
    when binary characters are fonud.

    :param value: the value that you wish to strip
    """
    if value is None:
        return None

    # Filter all non-printable characters
    # (note that we must use join to account for the fact that Python 3
    # returns a generator)
    printable_value = ''.join(filter(lambda c: c in string.printable, value))

    if printable_value != value:
        if printable_value:
            printable_value += ' '
        printable_value += '(contains binary)'

    return printable_value


def tostr(value):
    """
    Converts any variable to a string or returns None if the variable
    contained None to begin with; this function currently supports None,
    unicode strings, byte strings and numbers.

    :param value: the value you wish to convert to a string
    """

    if value is None:
        return None
    elif isinstance(value, text_type):
        return value
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return ub(value)
