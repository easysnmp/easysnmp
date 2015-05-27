class EasySNMPError(Exception):
    """The base Easy SNMP exception which covers all exceptions raised"""
    pass


class EasySNMPNoSuchObjectError(EasySNMPError):
    """The error raised when a NOSUCHOBJECT type is returned from Net-SNMP"""
    pass
