from __future__ import unicode_literals

def normalize_oid(oid, oid_index=None):
    """
    Ensures that the index is set correctly given an OID definition.

    :param oid: the OID to normalize
    :param oid_index: the OID index to normalize
    """

    # Determine the OID index from the OID if not specified
    if oid_index is None and oid is not None:
        # We attempt to extract the index from an OID (e.g. sysDescr.0
        # or .iso.org.dod.internet.mgmt.mib-2.system.sysContact.0)
        subidentifiers = oid.split('.')
        if subidentifiers:
            oid_index = subidentifiers.pop()
            oid = '.'.join(subidentifiers)

    return oid, oid_index
