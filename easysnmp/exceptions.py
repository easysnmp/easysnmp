class EasySNMPError(Exception):
    """The base Easy SNMP exception which covers all exceptions raised"""


class EasySNMPConnectionError(EasySNMPError):
    """Indicates a problem connecting to the remote host"""


class EasySNMPTimeoutError(EasySNMPConnectionError):
    """The error raised when an SNMP request times out"""


class EasySNMPUnknownObjectIDError(EasySNMPError):
    """The error raised when an inexisted OID is requested"""


class EasySNMPNoSuchObjectError(EasySNMPError):
    """The error raised when a NOSUCHOBJECT type is returned from Net-SNMP"""


class EasySNMPNoSuchInstanceError(EasySNMPError):
    """
    The error raised when a NOSUCHINSTANCE value is returned from Net-SNMP
    when a particular OID index doesn't exist
    """
