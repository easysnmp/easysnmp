from __future__ import unicode_literals

from easysnmp.helpers import normalize_oid


def test_normalize_oid_regular():
    oid, oid_index = normalize_oid("sysContact.0")
    assert oid == "sysContact"
    assert oid_index == "0"


def test_normalize_oid_numeric():
    oid, oid_index = normalize_oid(".1.3.6.1.2.1.1.1.0")
    assert oid == ".1.3.6.1.2.1.1.1.0"
    assert oid_index == ""


def test_normalize_oid_full_qualified():
    oid, oid_index = normalize_oid(".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0")
    assert oid == ".iso.org.dod.internet.mgmt.mib-2.system.sysDescr"
    assert oid_index == "0"


def test_normalize_oid_with_index():
    oid, oid_index = normalize_oid("abc", "def")
    assert oid == "abc"
    assert oid_index == "def"
