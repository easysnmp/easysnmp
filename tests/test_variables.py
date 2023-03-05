from __future__ import unicode_literals

from easysnmp.compat import ub
from easysnmp.variables import SNMPVariable, SNMPVariableList


def test_snmp_variable_regular():
    var = SNMPVariable("sysDescr", "0")
    assert var.oid == "sysDescr"
    assert var.oid_index == "0"


def test_snmp_variable_value():
    var = SNMPVariable("sysDescr", "0", "my thingo")
    assert var.value == "my thingo"
    assert var.oid == "sysDescr"
    assert var.oid_index == "0"


def test_snmp_variable_repr():
    var = SNMPVariable("sysDescr", "0", "my thingo", "OCTETSTR")
    assert var.__repr__() == (
        "<SNMPVariable value='my thingo' "
        "(oid='sysDescr', oid_index='0', snmp_type='OCTETSTR')>"
    )


def test_snmp_variable_repr_binary():
    var = SNMPVariable(
        "sysDescr", "0", ub(chr(20)) + "my thingo" + ub(chr(155)), "OCTETSTR"
    )
    assert var.__repr__() == (
        "<SNMPVariable value='my thingo (contains binary)' "
        "(oid='sysDescr', oid_index='0', snmp_type='OCTETSTR')>"
    )


def test_snmp_variable_repr_binary_only():
    var = SNMPVariable("sysDescr", "0", ub(chr(20)) + ub(chr(155)), "OCTETSTR")
    assert var.__repr__() == (
        "<SNMPVariable value='(contains binary)' "
        "(oid='sysDescr', oid_index='0', snmp_type='OCTETSTR')>"
    )


def test_snmp_variable_repr_none():
    var = SNMPVariable()
    assert var.__repr__() == (
        "<SNMPVariable value=None (oid=None, oid_index=None, snmp_type=None)>"
    )


def test_snmp_variable_eq_():
    var1 = SNMPVariable(
        "sysDescr", "0", ub(chr(20)) + "my thingo 1" + ub(chr(155)), "OCTETSTR"
    )

    var2 = SNMPVariable(
        "sysDescr", "0", ub(chr(20)) + "my thingo 1" + ub(chr(155)), "OCTETSTR"
    )

    assert var1 == var2


def test_snmp_variable_not_eq_():
    var1 = SNMPVariable(
        "sysDescr", "0", ub(chr(20)) + "my thingo 1" + ub(chr(155)), "OCTETSTR"
    )

    var2 = SNMPVariable(
        "sysDescr", "0", ub(chr(20)) + "my thingo 2" + ub(chr(155)), "OCTETSTR"
    )

    assert var1 != var2


def test_snmp_variable_extract_oid_index():
    var = SNMPVariable("sysDescr.0")
    assert var.oid == "sysDescr"
    assert var.oid_index == "0"
    assert var.value is None
    assert var.snmp_type is None


def test_snmp_variable_long():
    var = SNMPVariable(".iso.org.dod.internet.mgmt.mib-2.system.sysDescr", "0")
    assert var.oid == ".iso.org.dod.internet.mgmt.mib-2.system.sysDescr"
    assert var.oid_index == "0"
    assert var.value is None
    assert var.snmp_type is None


def test_snmp_variable_doesnt_extract_oid_index():
    var = SNMPVariable(".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0")
    assert var.oid == ".iso.org.dod.internet.mgmt.mib-2.system.sysDescr"
    assert var.oid_index == "0"
    assert var.value is None
    assert var.snmp_type is None


def test_snmp_variable_numeric():
    var = SNMPVariable(".1.3.6.1.2.1.1.1.0")
    assert var.oid == ".1.3.6.1.2.1.1.1.0"
    assert var.oid_index == ""
    assert var.value is None
    assert var.snmp_type is None


def test_snmp_variable_list():
    varlist = SNMPVariableList(["sysContact.0", "sysLocation.0", "sysDescr.0"])
    assert varlist.varbinds == ["sysContact.0", "sysLocation.0", "sysDescr.0"]
