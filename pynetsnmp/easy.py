from .session import Session


def snmp_get(oids, *args, **kargs):
    """Perform an SNMP GET operation to retrieve a particular piece of
    information
    """
    session = Session(*args, **kargs)
    return session.get(oids)


def snmp_set(oid, value, *args, **kargs):
    """Perform an SNMP SET operation to update a particular piece of
    information
    """
    session = Session(*args, **kargs)
    return session.set(oid, value)


def snmp_set_multiple(oid_values, *args, **kargs):
    """Perform multiple SNMP SET operations to update various pieces of
    information at the same time
    """
    session = Session(*args, **kargs)
    return session.set_multiple(oid_values)


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


def snmp_walk(oids='.1.3.6.1.2.1', *args, **kargs):
    """Uses SNMP GETNEXT operation to automatically retrieve multiple
    pieces of information in an OID for you
    """
    session = Session(*args, **kargs)
    return session.walk(oids)
