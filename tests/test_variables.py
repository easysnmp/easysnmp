import easysnmp


def test_easysnmp_variable():
    var = easysnmp.SNMPVariable('sysDescr', '0')
    assert var.tag == 'sysDescr'
    assert var.iid == '0'


def test_easysnmp_variable_extract_iid():
    var = easysnmp.SNMPVariable('sysDescr.0')
    assert var.tag == 'sysDescr'
    assert var.iid == '0'
    assert var.val is None
    assert var.type is None


def test_easysnmp_long_variable():
    var = easysnmp.SNMPVariable(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr', '0'
    )
    assert var.tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert var.iid == '0'
    assert var.val is None
    assert var.type is None


def test_easysnmp_variable_doesnt_extract_iid():
    var = easysnmp.SNMPVariable(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0'
    )
    assert var.tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert var.iid is '0'
    assert var.val is None
    assert var.type is None


def test_easysnmp_numeric_variable():
    var = easysnmp.SNMPVariable('.1.3.6.1.2.1.1.1.0')
    assert var.tag == '.1.3.6.1.2.1.1.1.0'
    assert var.iid == ''
    assert var.val is None
    assert var.type is None
