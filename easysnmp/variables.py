import string
import re

# This regular expression is used to extract the index from an OID
OID_INDEX_RE = re.compile(
    r'''(
            (?:\.\d+)+                   # numeric OID
            |                            # or
            (?:\w+(?:[-:]*\w+)+)         # regular OID
            |                            # or
            (?:\.iso(?:\.\w+[-:]*\w+)+)  # fully qualified OID
        )
        \.?(.*)                          # OID index
     ''',
    re.VERBOSE
)


def tostr(s):
    """Converts any variable to a string"""
    return None if s is None else str(s)


def normalize_oid(oid, oid_index):
    """Ensures that the index is set correctly given an OID definition"""

    # Determine the OID index from the OID if not specified
    if oid_index is None and oid is not None:
        # We attempt to extract the index from an OID (e.g. sysDescr.0
        # or .iso.org.dod.internet.mgmt.mib-2.system.sysContact.0)
        match = OID_INDEX_RE.match(oid)
        if match:
            oid, oid_index = match.group(1, 2)

    return oid, oid_index


class SNMPVariable(object):
    """An SNMP variable binding which is used to represent a piece of
    information being retreived via SNMP.

    :param oid: the OID being manipulated
    :param oid_index: the index of the OID
    :param value: the OID value
    :param snmp_type: the snmp_type of data contained in val (please see
                      http://www.net-snmp.org/wiki/index.php/TUT:snmpset#Data_Types
                      for further information)
    """

    def __init__(self, oid=None, oid_index=None, value=None, snmp_type=None):
        self.oid, self.oid_index = normalize_oid(oid, oid_index)
        self.value = value
        self.snmp_type = snmp_type

    def __repr__(self):
        # Filter all non-printable characters
        printable_value = filter(
            lambda c: c in string.printable, self.value
        )
        if printable_value != self.value:
            if printable_value:
                printable_value += ' '
            printable_value += '(contains binary)'

        return (
            "<{0} value='{1}' (oid='{2}', oid_index='{3}', "
            "snmp_type='{4}')>".format(
                self.__class__.__name__, printable_value, self.oid,
                self.oid_index, self.snmp_type
            )
        )

    def __setattr__(self, name, value):
        self.__dict__[name] = tostr(value)


class SNMPVariableList(list):
    """An slight variation of a list which is used internally by the
    Net-SNMP C interface."""
    @property
    def varbinds(self):
        return self
