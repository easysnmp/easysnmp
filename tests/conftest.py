from __future__ import unicode_literals

import logging
import pytest
from sys import version_info

if version_info[0] >= 3:
    from subprocess import Popen, DEVNULL
else:
    from subprocess import Popen
    from os import devnull

import easysnmp


class SNMPSetCLIError(Exception):
    """An exception raised when an SNMP SET fails via the CLI."""

    pass


if version_info[0] >= 3:  # Required to avoid UnboundLocalError in Python 3

    def snmp_set_via_cli(oid, value, type):
        """
        Sets an SNMP variable using the snmpset command.

        :param oid: the OID to update
        :param value: the new value to set the OID to
        :param type: a single character type as required by the snmpset command
                     (i: INTEGER, u: unsigned INTEGER, t: TIMETICKS,
                      a: IPADDRESS o: OBJID, s: STRING, x: HEX STRING,
                      d: DECIMAL STRING, b: BITS U: unsigned int64,
                      I: signed int64, F: float, D: double)
        """
        process = Popen(
            "snmpset -v2c -c public localhost:11161 {} {} {}".format(
                oid, type, '"{}"'.format(value) if type == "s" else value
            ),
            stdout=DEVNULL,
            stderr=DEVNULL,
            shell=True,
        )
        process.communicate()
        if process.returncode != 0:
            raise SNMPSetCLIError(
                "failed to set {0} to {1} (type {2})".format(oid, value, type)
            )

else:

    def snmp_set_via_cli(oid, value, type):
        """
        Sets an SNMP variable using the snmpset command.

        :param oid: the OID to update
        :param value: the new value to set the OID to
        :param type: a single character type as required by the snmpset command
                     (i: INTEGER, u: unsigned INTEGER, t: TIMETICKS,
                      a: IPADDRESS o: OBJID, s: STRING, x: HEX STRING,
                      d: DECIMAL STRING, b: BITS U: unsigned int64,
                      I: signed int64, F: float, D: double)
        """
        DEVNULL = open(devnull, "w")
        process = Popen(
            "snmpset -v2c -c public localhost:11161 {} {} {}".format(
                oid, type, '"{}"'.format(value) if type == "s" else value
            ),
            stdout=DEVNULL,
            stderr=DEVNULL,
            shell=True,
        )
        process.communicate()
        if process.returncode != 0:
            raise SNMPSetCLIError(
                "failed to set {0} to {1} (type {2})".format(oid, value, type)
            )
        DEVNULL.close()


# Disable logging for the C interface
snmp_logger = logging.getLogger("easysnmp.interface")
snmp_logger.disabled = True


SESS_V1_ARGS = {
    "version": 1,
    "hostname": "localhost",
    "remote_port": 11161,
    "community": "public",
}

SESS_V2_ARGS = {
    "version": 2,
    "hostname": "localhost",
    "remote_port": 11161,
    "community": "public",
}

SESS_V3_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "security_level": "authPriv",
    "security_username": "initial",
    "privacy_password": "priv_pass",
    "auth_password": "auth_pass",
}


@pytest.fixture(params=[SESS_V1_ARGS, SESS_V2_ARGS, SESS_V3_ARGS])
def sess_args(request):
    return request.param


@pytest.fixture
def sess(sess_args):
    return easysnmp.Session(**sess_args)


@pytest.fixture
def reset_values():
    yield None
    snmp_set_via_cli("sysLocation.0", "my original location", "s")
    snmp_set_via_cli("nsCacheTimeout.1.3.6.1.2.1.2.2", "0", "i")
