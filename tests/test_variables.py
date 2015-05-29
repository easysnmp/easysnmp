import easysnmp


def test_snmp_variable():
    var = easysnmp.SNMPVariable('sysDescr', '0')
    assert var.oid == 'sysDescr'
    assert var.oid_index == '0'


def test_snmp_variable_value():
    var = easysnmp.SNMPVariable('sysDescr', '0', 'my thingo')
    assert var.value == 'my thingo'
    assert var.oid == 'sysDescr'
    assert var.oid_index == '0'


def test_snmp_variable_repr():
    var = easysnmp.SNMPVariable('sysDescr', '0', 'my thingo', 'OCTETSTR')
    assert var.__repr__() == (
        "<SNMPVariable value='my thingo' "
        "(oid='sysDescr', oid_index='0', snmp_type='OCTETSTR')>"
    )


def test_snmp_variable_repr_binary():
    var = easysnmp.SNMPVariable(
        'sysDescr', '0',
        chr(20) + 'my thingo' + chr(155),
        'OCTETSTR'
    )
    assert var.__repr__() == (
        "<SNMPVariable value='my thingo (contains binary)' "
        "(oid='sysDescr', oid_index='0', snmp_type='OCTETSTR')>"
    )


def test_snmp_variable_repr_binary_only():
    var = easysnmp.SNMPVariable(
        'sysDescr', '0',
        chr(20) + chr(155),
        'OCTETSTR'
    )
    assert var.__repr__() == (
        "<SNMPVariable value='(contains binary)' "
        "(oid='sysDescr', oid_index='0', snmp_type='OCTETSTR')>"
    )


def test_snmp_variable_extract_oid_index():
    var = easysnmp.SNMPVariable('sysDescr.0')
    assert var.oid == 'sysDescr'
    assert var.oid_index == '0'
    assert var.value is None
    assert var.snmp_type is None


def test_snmp_variable_long():
    var = easysnmp.SNMPVariable(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr', '0'
    )
    assert var.oid == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert var.oid_index == '0'
    assert var.value is None
    assert var.snmp_type is None


def test_snmp_variable_doesnt_extract_oid_index():
    var = easysnmp.SNMPVariable(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0'
    )
    assert var.oid == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert var.oid_index is '0'
    assert var.value is None
    assert var.snmp_type is None


def test_snmp_variable_numeric():
    var = easysnmp.SNMPVariable('.1.3.6.1.2.1.1.1.0')
    assert var.oid == '.1.3.6.1.2.1.1.1.0'
    assert var.oid_index == ''
    assert var.value is None
    assert var.snmp_type is None
