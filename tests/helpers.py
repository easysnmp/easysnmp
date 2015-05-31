import os
import subprocess


class SNMPSetCLIError(Exception):
    """An exception raised when an SNMP SET fails via the CLI"""


def snmp_set_via_cli(oid, value, type):
    """Sets an SNMP variable using the snmpset command

    :param oid: the OID to update
    :param value: the new value to set the OID to
    :param type: a single character type as required by the snmpset command
                 (i: INTEGER, u: unsigned INTEGER, t: TIMETICKS, a: IPADDRESS
                  o: OBJID, s: STRING, x: HEX STRING, d: DECIMAL STRING,
                  b: BITS U: unsigned int64, I: signed int64, F: float,
                  D: double)
    """
    dev_null = open(os.devnull)
    process = subprocess.Popen([
        'snmpset', '-v2c', '-c', 'public', 'localhost', oid, type, value
    ], stdout=dev_null, stderr=dev_null)
    process.communicate()
    if process.returncode != 0:
        raise SNMPSetCLIError(
            'failed to set {0} to {1} (type {2})'.format(oid, value, type)
        )
