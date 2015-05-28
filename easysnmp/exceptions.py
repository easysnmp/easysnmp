class EasySNMPError(Exception):
    """The base Easy SNMP exception which covers all exceptions raised"""
    pass


class EasySNMPNoSuchObjectError(EasySNMPError):
    """The error raised when a NOSUCHOBJECT type is returned from Net-SNMP"""
    pass


class EasySNMPNoSuchInstanceError(EasySNMPError):
    """The error raised when a NOSUCHINSTANCE value is returned from
    Net-SNMP when a particular OID index doesn't exist"""
    pass
