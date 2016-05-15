from __future__ import unicode_literals

from .session import Session


def snmp_get(oids, **session_kargs):
    """
    Perform an SNMP GET operation to retrieve a particular piece of
    information.

    :param oids: you may pass in a list of OIDs or single item; each item
                 may be a string representing the entire OID
                 (e.g. 'sysDescr.0') or may be a tuple containing the
                 name as its first item and index as its second
                 (e.g. ('sysDescr', 0))
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    """

    session = Session(**session_kargs)
    return session.get(oids)


def snmp_set(oid, value, type=None, **session_kargs):
    """
    Perform an SNMP SET operation to update a particular piece of
    information.

    :param oid: the OID that you wish to set which may be a string
                representing the entire OID (e.g. 'sysDescr.0') or may
                be a tuple containing the name as its first item and
                index as its second (e.g. ('sysDescr', 0))
    :param value: the value to set the OID to
    :param snmp_type: if a numeric OID is used and the object is not in
                      the parsed MIB, a type must be explicitly supplied
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    """

    session = Session(**session_kargs)
    return session.set(oid, value, type)


def snmp_set_multiple(oid_values, **session_kargs):
    """
    Perform multiple SNMP SET operations to update various pieces of
    information at the same time.

    :param oid_values: a list of tuples whereby each tuple contains a
                       (oid, value) or an (oid, value, snmp_type)
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    """

    session = Session(**session_kargs)
    return session.set_multiple(oid_values)


def snmp_get_next(oids, **session_kargs):
    """
    Uses an SNMP GETNEXT operation to retrieve the next variable after
    the chosen item.

    :param oids: you may pass in a list of OIDs or single item; each item
                 may be a string representing the entire OID
                 (e.g. 'sysDescr.0') or may be a tuple containing the
                 name as its first item and index as its second
                 (e.g. ('sysDescr', 0))
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    """

    session = Session(**session_kargs)
    return session.get_next(oids)


def snmp_get_bulk(oids, non_repeaters=0, max_repetitions=10, **session_kargs):
    """
    Performs a bulk SNMP GET operation to retrieve multiple pieces of
    information in a single packet.

    :param oids: you may pass in a list of OIDs or single item; each item
                 may be a string representing the entire OID
                 (e.g. 'sysDescr.0') or may be a tuple containing the
                 name as its first item and index as its second
                 (e.g. ('sysDescr', 0))
    :param non_repeaters: the number of objects that are only expected to
                          return a single GETNEXT instance, not multiple
                          instances
    :param max_repetitions: the number of objects that should be returned
                            for all the repeating OIDs
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    """

    session = Session(**session_kargs)
    return session.get_bulk(oids, non_repeaters, max_repetitions)


def snmp_walk(oids='.1.3.6.1.2.1', **session_kargs):
    """
    Uses SNMP GETNEXT operation to automatically retrieve multiple
    pieces of information in an OID for you.

    :param oids: you may pass in a single item (multiple values currently
                 experimental) which may be a string representing the
                 entire OID (e.g. 'sysDescr.0') or may be a tuple
                 containing the name as its first item and index as its
                 second (e.g. ('sysDescr', 0))
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    """

    session = Session(**session_kargs)
    return session.walk(oids)


def snmp_bulkwalk(
    oids='.1.3.6.1.2.1', non_repeaters=0, max_repetitions=10,
    **session_kargs
):
    """
    Uses SNMP GETBULK operation using the prepared session to
    automatically retrieve multiple pieces of information in an OID

    :param oids: you may pass in a single item
                 * string representing the
                 entire OID (e.g. 'sysDescr.0')
                 * tuple (name, index) (e.g. ('sysDescr', 0))
                 * list of OIDs
    :param non_repeaters: the number of objects that are only expected to
                          return a single GETNEXT instance, not multiple
                          instances
    :param max_repetitions: the number of objects that should be returned
                            for all the repeating OIDs
    :return: a list of SNMPVariable objects containing the values that
             were retrieved via SNMP
    """

    session = Session(**session_kargs)
    return session.bulkwalk(oids, non_repeaters, max_repetitions)
