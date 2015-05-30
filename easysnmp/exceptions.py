class EasySNMPError(Exception):
    """The base Easy SNMP exception which covers all exceptions raised"""


class EasySNMPConnectionError(EasySNMPError):
    """Indicates a problem connecting to the remote host"""


class EasySNMPTimeoutError(EasySNMPConnectionError):
    """Raised when an SNMP request times out"""


class EasySNMPUnknownObjectIDError(EasySNMPError):
    """Raised when an inexisted OID is requested"""


class EasySNMPNoSuchObjectError(EasySNMPError):
    """Raised when a NOSUCHOBJECT type is returned from Net-SNMP"""


class EasySNMPNoSuchInstanceError(EasySNMPError):
    """
    Raised when a NOSUCHINSTANCE value is returned from Net-SNMP when a
    particular OID index doesn't exist
    """


class EasySNMPUndeterminedTypeError(EasySNMPError):
    """
    Raised when the type cannot be determine when setting the value of an OID
    """
