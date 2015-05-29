import easysnmp


def test_easysnmp_variable():
    var = easysnmp.SNMPVariable('sysDescr', '0')
    assert var.oid == 'sysDescr'
    assert var.oid_index == '0'


def test_easysnmp_variable_extract_oid_index():
    var = easysnmp.SNMPVariable('sysDescr.0')
    assert var.oid == 'sysDescr'
    assert var.oid_index == '0'
    assert var.value is None
    assert var.snmp_type is None


def test_easysnmp_long_variable():
    var = easysnmp.SNMPVariable(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr', '0'
    )
    assert var.oid == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert var.oid_index == '0'
    assert var.value is None
    assert var.snmp_type is None


def test_easysnmp_variable_doesnt_extract_oid_index():
    var = easysnmp.SNMPVariable(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0'
    )
    assert var.oid == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert var.oid_index is '0'
    assert var.value is None
    assert var.snmp_type is None


def test_easysnmp_numeric_variable():
    var = easysnmp.SNMPVariable('.1.3.6.1.2.1.1.1.0')
    assert var.oid == '.1.3.6.1.2.1.1.1.0'
    assert var.oid_index == ''
    assert var.value is None
    assert var.snmp_type is None
