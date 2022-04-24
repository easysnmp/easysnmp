from __future__ import unicode_literals

from easysnmp.session import build_varlist


def test_build_varlist():
    varlist, is_list = build_varlist("sysContact.0")
    assert len(varlist) == 1
    assert varlist[0].oid == "sysContact"
    assert varlist[0].oid_index == "0"
    assert varlist[0].value is None
    assert varlist[0].snmp_type is None
    assert not is_list


def test_build_varlist_list():
    varlist, is_list = build_varlist(["sysContact.0", ("sysDescr", "0")])
    assert len(varlist) == 2
    assert varlist[0].oid == "sysContact"
    assert varlist[0].oid_index == "0"
    assert varlist[0].value is None
    assert varlist[0].snmp_type is None
    assert varlist[1].oid == "sysDescr"
    assert varlist[1].oid_index == "0"
    assert varlist[1].value is None
    assert varlist[1].snmp_type is None
    assert is_list
