import string


class SNMPBaseIntegerType(object):
    """The base type for all SNMP integer data types"""
    snmp_type = None

    def __init__(self, value, oid=None, oid_index=None):
        self.value = int(value)
        self.oid = oid
        self.oid_index = oid_index

    def __repr__(self):
        return (
            "<{} value={} (oid='{}', oid_index={})>".format(
                self.__class__.__name__, self.value, self.oid, self.oid_index
            )
        )


class SNMPBaseStringType(object):
    """The base type for all SNMP string data types"""
    snmp_type = None

    def __init__(self, value, oid=None, oid_index=None):
        self.value = value
        self.oid = oid
        self.oid_index = oid_index

    def __repr__(self):
        # Filter all non-printable characters
        printable = filter(lambda c: c in string.printable, self)
        if printable != self:
            if printable:
                printable += ' '
            printable += '(contains binary)'

        return (
            "<{} value='{}' (oid='{}', oid_index={})>".format(
                self.__class__.__name__, printable, self.oid, self.oid_index
            )
        )


class SNMPBits(SNMPBaseStringType):
    """The SNMP data type used to specifies a collection of labelled bits"""
    snmp_type = 'BITS'


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


class SNMPOpaque(SNMPBaseStringType):
    """The SNMP data type used sometimes to wrap objects of other types"""
    snmp_type = 'OPAQUE'


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
    'BITS': SNMPBits,
    'OBJECTID': SNMPObjectIdentifier,
    'OCTETSTR': SNMPOctetString,
    'INTEGER': SNMPInteger,
    'NETADDR': SNMPNetworkAddress,
    'IPADDR': SNMPIPAddress,
    'COUNTER': SNMPCounter,
    'GAUGE': SNMPGauge,
    'TICKS': SNMPTimeTicks,
    'OPAQUE': SNMPOpaque,
    'COUNTER64': SNMPCounter64,
    'UNSIGNED32': SNMPUnsigned32,
    'INTEGER32': SNMPInteger32,
}
