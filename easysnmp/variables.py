from .helpers import normalize_oid
from .utils import strip_non_printable, tostr


class SNMPVariable(object):
    """
    An SNMP variable binding which is used to represent a piece of
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
        printable_value = strip_non_printable(self.value)
        repr_value = (
            '(none)' if printable_value is None
            else "'{0}'".format(printable_value)
        )
        repr_oid = '(none)' if self.oid is None else "'{0}'".format(self.oid)
        repr_oid_index = (
            '(none)' if self.oid_index is None
            else "'{0}'".format(self.oid_index)
        )
        repr_snmp_type = (
            '(none)' if self.snmp_type is None
            else "'{0}'".format(self.snmp_type)
        )
        return (
            "<{0} value={1} (oid={2}, oid_index={3}, snmp_type={4})>".format(
                self.__class__.__name__,
                repr_value, repr_oid, repr_oid_index, repr_snmp_type
            )
        )

    def __setattr__(self, name, value):
        self.__dict__[name] = tostr(value)


class SNMPVariableList(list):
    """
    An slight variation of a list which is used internally by the
    Net-SNMP C interface.
    """

    @property
    def varbinds(self):
        return self
