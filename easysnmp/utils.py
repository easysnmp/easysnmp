import string


def strip_non_printable(value):
    """
    Removes any non-printable characters and adds an indicator to the string
    when binary characters are fonud

    :param value: the value that you wish to strip
    """
    # Filter all non-printable characters
    printable_value = filter(lambda c: c in string.printable, value)

    if printable_value != value:
        if printable_value:
            printable_value += ' '
        printable_value += '(contains binary)'

    return printable_value


def tostr(value):
    """
    Converts any variable to a string or returns None if the variable
    contained None to begin with

    :param value: the value you wish to convert to a string
    """

    return None if value is None else str(value)
