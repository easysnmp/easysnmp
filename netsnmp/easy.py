from .variables import Varbind, VarList
from .session import Session


def snmp_get(*args, **kargs):
    """Perform an SNMP GET operation to retrieve a particular piece of
    information
    """

    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))

    session = Session(**kargs)
    return session.get(var_list)


def snmp_set(*args, **kargs):
    """Perform an SNMP SET operation to retrieve a particular piece of
    information
    """

    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))

    session = Session(**kargs)
    return session.set(var_list)


def snmp_get_next(*args, **kargs):
    """Uses an SNMP GETNEXT operation to retrieve the next variable after
    the chosen item
    """

    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))

    session = Session(**kargs)
    return session.get_next(var_list)


def snmp_get_bulk(non_repeaters, max_repetitions, *args, **kargs):
    """Performs a bulk SNMP GET operation to retrieve multiple pieces of
    information in a single packet
    """

    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))

    session = Session(**kargs)
    return session.get_bulk(non_repeaters, max_repetitions, var_list)


def snmp_walk(*args, **kargs):
    """Uses SNMP GETNEXT operation to automatically retrieve multiple
    pieces of information in an OID for you
    """

    if isinstance(args[0], VarList):
        var_list = args[0]
    else:
        var_list = VarList()
        for arg in args:
            if isinstance(arg, Varbind):
                var_list.append(arg)
            else:
                var_list.append(Varbind(arg))

    session = Session(**kargs)
    return session.walk(var_list)
