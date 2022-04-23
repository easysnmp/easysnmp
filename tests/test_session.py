from __future__ import unicode_literals

import platform
import re

import pytest
from easysnmp.exceptions import (
    EasySNMPError,
    EasySNMPConnectionError,
    EasySNMPTimeoutError,
    EasySNMPNoSuchObjectError,
    EasySNMPNoSuchInstanceError,
    EasySNMPNoSuchNameError,
)

from easysnmp.session import Session


def test_session_invalid_snmp_version():
    with pytest.raises(ValueError):
        Session(version=4)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_session_invalid_hostname(version):
    with pytest.raises(EasySNMPConnectionError):
        session = Session(hostname="invalid", version=version)
        session.get("sysContact.0")


@pytest.mark.parametrize("version", [1, 2, 3])
def test_session_invalid_hostname_and_remote_port(version):
    with pytest.raises(ValueError):
        Session(hostname="localhost:162", remote_port=163, version=version)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_session_hostname_and_remote_port_split(version):
    session = Session(hostname="localhost:162", version=version)
    assert session.hostname == "localhost"
    assert session.remote_port == 162


@pytest.mark.parametrize("version", [1, 2, 3])
def test_session_invalid_port(version):
    with pytest.raises(EasySNMPTimeoutError):
        session = Session(remote_port=1234, version=version, timeout=0.2, retries=1)
        session.get("sysContact.0")


def test_session_set_multiple_next(sess, reset_values):
    # Destroy succeeds even if no row exists
    sess.set(".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", 6)
    success = sess.set_multiple(
        [
            (".1.3.6.1.6.3.12.1.2.1.2.116.101.115.116", ".1.3.6.1.6.1.1"),
            (".1.3.6.1.6.3.12.1.2.1.3.116.101.115.116", "1234"),
            (".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", 4),
        ]
    )
    assert success

    res = sess.get_next(
        ["snmpTargetAddrTDomain", "snmpTargetAddrTAddress", "snmpTargetAddrRowStatus"]
    )

    assert len(res) == 3

    assert res[0].oid == "snmpTargetAddrTDomain"
    assert res[0].oid_index == "116.101.115.116"
    assert res[0].value == ".1.3.6.1.6.1.1"
    assert res[0].snmp_type == "OBJECTID"

    assert res[1].oid == "snmpTargetAddrTAddress"
    assert res[1].oid_index == "116.101.115.116"
    assert res[1].value == "1234"
    assert res[1].snmp_type == "OCTETSTR"

    assert res[2].oid == "snmpTargetAddrRowStatus"
    assert res[2].oid_index == "116.101.115.116"
    assert res[2].value == "3"
    assert res[2].snmp_type == "INTEGER"


def test_session_set_clear(sess):
    res = sess.set(".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", 6)
    assert res == 1

    res = sess.get_next(
        ["snmpTargetAddrTDomain", "snmpTargetAddrTAddress", "snmpTargetAddrRowStatus"]
    )

    assert len(res) == 3

    assert res[0].oid == "snmpUnavailableContexts"
    assert res[0].oid_index == "0"
    assert res[0].value == "0"
    assert res[0].snmp_type == "COUNTER"

    assert res[1].oid == "snmpUnavailableContexts"
    assert res[1].oid_index == "0"
    assert res[1].value == "0"
    assert res[1].snmp_type == "COUNTER"

    assert res[2].oid == "snmpUnavailableContexts"
    assert res[2].oid_index == "0"
    assert res[2].value == "0"
    assert res[2].snmp_type == "COUNTER"


def test_session_get(sess):
    res = sess.get([("sysUpTime", "0"), ("sysContact", "0"), ("sysLocation", "0")])

    assert len(res) == 3

    assert res[0].oid == "sysUpTimeInstance"
    assert res[0].oid_index == ""
    assert int(res[0].value) > 0
    assert res[0].snmp_type == "TICKS"

    assert res[1].oid == "sysContact"
    assert res[1].oid_index == "0"
    assert res[1].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[1].snmp_type == "OCTETSTR"

    assert res[2].oid == "sysLocation"
    assert res[2].oid_index == "0"
    assert res[2].value == "my original location"
    assert res[2].snmp_type == "OCTETSTR"


def test_session_get_use_numeric(sess):
    sess.use_numeric = True
    res = sess.get("sysContact.0")

    assert res.oid == ".1.3.6.1.2.1.1.4"
    assert res.oid_index == "0"
    assert res.value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res.snmp_type == "OCTETSTR"


def test_session_get_use_sprint_value(sess):
    sess.use_sprint_value = True
    res = sess.get("sysUpTimeInstance")

    assert res.oid == "sysUpTimeInstance"
    assert res.oid_index == ""
    assert re.match(r"^\d+:\d+:\d+:\d+\.\d+$", res.value)
    assert res.snmp_type == "TICKS"


def test_session_get_use_enums(sess):
    sess.use_enums = True
    res = sess.get("ifAdminStatus.1")

    assert res.oid == "ifAdminStatus"
    assert res.oid_index == "1"
    assert res.value == "up"
    assert res.snmp_type == "INTEGER"


def test_session_get_next(sess):
    res = sess.get_next([("sysUpTime", "0"), ("sysContact", "0"), ("sysLocation", "0")])

    assert len(res) == 3

    assert res[0].oid == "sysContact"
    assert res[0].oid_index == "0"
    assert res[0].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[0].snmp_type == "OCTETSTR"

    assert res[1].oid == "sysName"
    assert res[1].oid_index == "0"
    assert res[1].value == platform.node()
    assert res[1].snmp_type == "OCTETSTR"

    assert res[2].oid == "sysORLastChange"
    assert res[2].oid_index == "0"
    assert int(res[2].value) >= 0
    assert res[2].snmp_type == "TICKS"


def test_session_set(sess, reset_values):
    res = sess.get(("sysLocation", "0"))
    assert res.value != "my newer location"

    success = sess.set(("sysLocation", "0"), "my newer location")
    assert success

    res = sess.get(("sysLocation", "0"))
    assert res.value == "my newer location"


def test_session_set_multiple(sess, reset_values):
    res = sess.get(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"])
    assert res[0].value != "my newer location"
    assert res[1].value != "160"

    success = sess.set_multiple(
        [
            ("sysLocation.0", "my newer location"),
            (("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 160),
        ]
    )
    assert success

    res = sess.get(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"])
    assert res[0].value == "my newer location"
    assert res[1].value == "160"


def test_session_get_bulk(sess):  # noqa
    if sess.version == 1:
        with pytest.raises(EasySNMPError):
            sess.get_bulk(
                [
                    "sysUpTime",
                    "sysORLastChange",
                    "sysORID",
                    "sysORDescr",
                    "sysORUpTime",
                ],
                2,
                8,
            )
    else:
        res = sess.get_bulk(
            ["sysUpTime", "sysORLastChange", "sysORID", "sysORDescr", "sysORUpTime"],
            2,
            8,
        )

        assert len(res) == 26

        assert res[0].oid == "sysUpTimeInstance"
        assert res[0].oid_index == ""
        assert int(res[0].value) > 0
        assert res[0].snmp_type == "TICKS"

        assert res[4].oid == "sysORUpTime"
        assert res[4].oid_index == "1"
        assert int(res[4].value) >= 0
        assert res[4].snmp_type == "TICKS"


def test_session_get_invalid_instance(sess):
    # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    if sess.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess.get("sysDescr.100")
    else:
        res = sess.get("sysDescr.100")
        assert res.snmp_type == "NOSUCHINSTANCE"


def test_session_get_invalid_instance_with_abort_enabled(sess):
    # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    sess.abort_on_nonexistent = True
    if sess.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess.get("sysDescr.100")
    else:
        with pytest.raises(EasySNMPNoSuchInstanceError):
            sess.get("sysDescr.100")


def test_session_get_invalid_object(sess):
    if sess.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess.get("iso")
    else:
        res = sess.get("iso")
        assert res.snmp_type == "NOSUCHOBJECT"


def test_session_get_invalid_object_with_abort_enabled(sess):
    sess.abort_on_nonexistent = True
    if sess.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess.get("iso")
    else:
        with pytest.raises(EasySNMPNoSuchObjectError):
            sess.get("iso")


def test_session_walk(sess):
    res = sess.walk("system")

    assert len(res) >= 7

    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert platform.version() in res[0].value
    assert res[0].snmp_type == "OCTETSTR"

    assert res[3].oid == "sysContact"
    assert res[3].oid_index == "0"
    assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[3].snmp_type == "OCTETSTR"

    assert res[4].oid == "sysName"
    assert res[4].oid_index == "0"
    assert res[4].value == platform.node()
    assert res[4].snmp_type == "OCTETSTR"

    assert res[5].oid == "sysLocation"
    assert res[5].oid_index == "0"
    assert res[5].value == "my original location"
    assert res[5].snmp_type == "OCTETSTR"


def test_session_bulkwalk(sess):
    if sess.version == 1:
        with pytest.raises(EasySNMPError):
            sess.bulkwalk("system")
    else:
        res = sess.walk("system")

        assert len(res) >= 7

        assert res[0].oid == "sysDescr"
        assert res[0].oid_index == "0"
        assert platform.version() in res[0].value
        assert res[0].snmp_type == "OCTETSTR"

        assert res[3].oid == "sysContact"
        assert res[3].oid_index == "0"
        assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
        assert res[3].snmp_type == "OCTETSTR"

        assert res[4].oid == "sysName"
        assert res[4].oid_index == "0"
        assert res[4].value == platform.node()
        assert res[4].snmp_type == "OCTETSTR"

        assert res[5].oid == "sysLocation"
        assert res[5].oid_index == "0"
        assert res[5].value == "my original location"
        assert res[5].snmp_type == "OCTETSTR"


def test_session_walk_all(sess):
    # OID 1.3.6.1.6.3.16.1.5.2.1.6.6.95.110.111.110.101.95.1.2
    # or SNMP-VIEW-BASED-ACM-MIB::vacmViewTreeFamilyStatus."_none_".1.2
    # appears to return a noSuchName error when using v1, but not with v2c.
    # This may be a Net-SNMP snmpd bug.
    if sess.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess.walk(".")
    else:
        res = sess.walk(".")

        assert len(res) > 0

        assert res[0].oid == "sysDescr"
        assert res[0].oid_index == "0"
        assert platform.version() in res[0].value
        assert res[0].snmp_type == "OCTETSTR"

        assert res[3].oid == "sysContact"
        assert res[3].oid_index == "0"
        assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
        assert res[3].snmp_type == "OCTETSTR"

        assert res[4].oid == "sysName"
        assert res[4].oid_index == "0"
        assert res[4].value == platform.node()
        assert res[4].snmp_type == "OCTETSTR"

        assert res[5].oid == "sysLocation"
        assert res[5].oid_index == "0"
        assert res[5].value == "my original location"
        assert res[5].snmp_type == "OCTETSTR"


def test_session_update():
    s = Session(version=3)
    ptr = s.sess_ptr
    s.version = 1
    s.update_session()
    assert ptr != s.sess_ptr
    s.tunneled = True
    ptr = s.sess_ptr
    with pytest.raises(ValueError):
        s.update_session()
    assert ptr == s.sess_ptr
    s.update_session(tunneled=False, version=2)
    assert s.version == 2
    assert s.tunneled is False
