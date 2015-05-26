class PyNetSNMPError(Exception):
    """The base PyNetSNMP exception which covers all exceptions raised"""
    pass


class PyNetSNMPNoSuchObjectError(PyNetSNMPError):
    """The error raised when a NOSUCHOBJECT type is returned from Net-SNMP"""
    pass
