class SNMPBaseIntegerType(int):
    """The base type for all SNMP integer data types"""
    snmp_type = None

    def __new__(cls, value, snmp_oid=None, snmp_oid_index=None):
        obj = int.__new__(cls, value)
        obj.snmp_oid = snmp_oid
        obj.snmp_oid_index = snmp_oid_index
        return obj


class SNMPBaseStringType(str):
    """The base type for all SNMP string data types"""
    snmp_type = None

    def __new__(cls, value, snmp_oid=None, snmp_oid_index=None):
        obj = str.__new__(cls, value)
        obj.snmp_oid = snmp_oid
        obj.snmp_oid_index = snmp_oid_index
        return obj


class SNMPTimeTicks(SNMPBaseIntegerType):
    """The SNMP data type specifying the elapsed time between two events"""
    snmp_type = 'TICKS'


class SNMPOctetString(SNMPBaseStringType):
    """The SNMP data type used to specify octets of binary or textual
    information"""
    snmp_type = 'OCTETSTR'


class SNMPObjectIdentifier(SNMPBaseStringType):
    """The SNMP data type used to identify a type that has an assigned object
    identifier value"""
    snmp_type = 'OBJECTID'
