class EasySNMPError(Exception):
    """The base Easy SNMP exception which covers all exceptions raised"""


class EasySNMPTimeoutError(EasySNMPError):
    """The error raised when an SNMP request times out"""


class EasySNMPNoSuchObjectError(EasySNMPError):
    """The error raised when a NOSUCHOBJECT type is returned from Net-SNMP"""


class EasySNMPNoSuchInstanceError(EasySNMPError):
    """
    The error raised when a NOSUCHINSTANCE value is returned from Net-SNMP
    when a particular OID index doesn't exist
    """
