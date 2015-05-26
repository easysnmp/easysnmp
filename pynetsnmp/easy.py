from .variables import Varbind, VarList
from .session import Session


def snmp_get(oids, *args, **kargs):
    """Perform an SNMP GET operation to retrieve a particular piece of
    information
    """
    session = Session(*args, **kargs)
    return session.get(oids)


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


def snmp_get_next(oids, *args, **kargs):
    """Uses an SNMP GETNEXT operation to retrieve the next variable after
    the chosen item
    """

    session = Session(*args, **kargs)
    return session.get_next(oids)


def snmp_get_bulk(oids, non_repeaters, max_repetitions, *args, **kargs):
    """Performs a bulk SNMP GET operation to retrieve multiple pieces of
    information in a single packet
    """

    session = Session(*args, **kargs)
    return session.get_bulk(oids, non_repeaters, max_repetitions)


def snmp_walk(oids, *args, **kargs):
    """Uses SNMP GETNEXT operation to automatically retrieve multiple
    pieces of information in an OID for you
    """

    session = Session(*args, **kargs)
    return session.walk(oids)
