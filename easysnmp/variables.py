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


def normalize_oid(tag, iid):
    """Ensures that the index is set correctly given an OID definition"""

    # Determine the OID ID from the tag if not specified
    if iid is None and tag is not None:
        # We attempt to extract the index from an OID (e.g. sysDescr.0
        # or .iso.org.dod.internet.mgmt.mib-2.system.sysContact.0)
        match = OID_INDEX_RE.match(tag)
        if match:
            tag, iid = match.group(1, 2)

    return tag, iid


class SNMPVariable(object):
    """An SNMP variable binding which is used to represent a piece of
    information being retreived via SNMP.

    :param tag: the OID being manipulated
    :param iid: the index of the OID
    :param val: the OID value
    :param type: the type of data contained in val (please see
                 http://www.net-snmp.org/wiki/index.php/TUT:snmpset#Data_Types
                 for further information)
    """

    def __init__(self, tag=None, iid=None, val=None, type=None):
        self.tag, self.iid = normalize_oid(tag, iid)
        self.val = val
        self.type = type

    def __setattr__(self, name, value):
        self.__dict__[name] = tostr(value)


class SNMPVariableList(list):
    """An slight variation of a list which is used internally by the
    Net-SNMP C interface."""
    @property
    def varbinds(self):
        return self
