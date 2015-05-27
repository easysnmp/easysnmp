from curses.ascii import isprint


class SNMPBaseIntegerType(int):
    """The base type for all SNMP integer data types"""
    snmp_type = None

    def __new__(cls, value, snmp_oid=None, snmp_oid_index=None):
        obj = int.__new__(cls, value)
        obj.snmp_oid = snmp_oid
        if snmp_oid_index is None:
            obj.snmp_oid_index = None
        else:
            obj.snmp_oid_index = int(snmp_oid_index)
        return obj

    def __repr__(self):
        return (
            "<{} value={} (snmp_oid='{}', snmp_oid_index={})>".format(
                self.__class__.__name__, self, self.snmp_oid,
                self.snmp_oid_index
            )
        )


class SNMPBaseStringType(str):
    """The base type for all SNMP string data types"""
    snmp_type = None

    def __new__(cls, value, snmp_oid=None, snmp_oid_index=None):
        obj = str.__new__(cls, value)
        obj.snmp_oid = snmp_oid
        if snmp_oid_index is None:
            obj.snmp_oid_index = None
        else:
            obj.snmp_oid_index = int(snmp_oid_index)
        return obj

    def __repr__(self):
        # Filter all non-printable characters
        printable = filter(isprint, self)
        if printable != self:
            if printable:
                printable += ' '
            printable += '(contains binary)'

        return (
            "<{} value='{}' (snmp_oid='{}', snmp_oid_index={})>".format(
                self.__class__.__name__, printable, self.snmp_oid,
                self.snmp_oid_index
            )
        )


class SNMPObjectIdentifier(SNMPBaseStringType):
    """The SNMP data type used to identify a type that has an assigned object
    identifier value"""
    snmp_type = 'OBJECTID'


class SNMPOctetString(SNMPBaseStringType):
    """The SNMP data type used to specify octets of binary or textual
    information"""
    snmp_type = 'OCTETSTR'


class SNMPInteger(SNMPBaseIntegerType):
    """The SNMP data type representing a signed 32-bit integer"""
    snmp_type = 'INTEGER'


class SNMPNetworkAddress(SNMPBaseStringType):
    """The SNMP data type used to specify a network address of any type to
    be specified"""
    snmp_type = 'NETADDR'


class SNMPIPAddress(SNMPBaseStringType):
    """The SNMP data type used to specify an IPv4 address as a string of
    4 octets"""
    snmp_type = 'IPADDR'


class SNMPCounter(SNMPBaseIntegerType):
    """The SNMP data type representing a non-negative integer which
    monotonically increases until it reaches a maximum value"""
    snmp_type = 'COUNTER'


class SNMPGauge(SNMPBaseIntegerType):
    """The SNMP data type representing an unsigned integer, which may
    increase or decrease, but shall never exceed a maximum value"""
    snmp_type = 'GAUGE'


class SNMPTimeTicks(SNMPBaseIntegerType):
    """The SNMP data type specifying the elapsed time between two events"""
    snmp_type = 'TICKS'


class SNMPCounter64(SNMPBaseIntegerType):
    """The SNMP data type similar to counter but of 64-bit precision"""
    snmp_type = 'COUNTER64'


class SNMPUnsigned32(SNMPBaseIntegerType):
    """The SNMP data type representing an unsigned 32-bit integer"""
    snmp_type = 'UNSIGNED32'


class SNMPInteger32(SNMPBaseIntegerType):
    """The SNMP data type identical to an integer"""
    snmp_type = 'INTEGER32'


# Below we define a type mapping dictionary from type to its related class
TYPE_MAPPING = {
    'OTHER': None,
    'OBJECTID': SNMPObjectIdentifier,
    'OCTETSTR': SNMPOctetString,
    'INTEGER': SNMPInteger,
    'NETADDR': SNMPNetworkAddress,
    'IPADDR': SNMPIPAddress,
    'COUNTER': SNMPCounter,
    'GAUGE': SNMPGauge,
    'TICKS': SNMPTimeTicks,
    'OPAQUE': None,
    'NULL': None,
    'COUNTER64': SNMPCounter64,
    'BITSTRING': None,
    'NSAPADDRESS': None,
    'UINTEGER': None,
    'UNSIGNED32': SNMPUnsigned32,
    'INTEGER32': SNMPInteger32,
}
