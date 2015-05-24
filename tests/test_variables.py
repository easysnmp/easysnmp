import pynetsnmp


def test_pynetsnmp_variable():
    var = pynetsnmp.Varbind('sysDescr', '0')
    assert var.tag == 'sysDescr'
    assert var.iid == '0'


def test_pynetsnmp_variable_extract_iid():
    var = pynetsnmp.Varbind('sysDescr.0')
    assert var.tag == 'sysDescr'
    assert var.iid == '0'
    assert var.val is None
    assert var.type is None


def test_pynetsnmp_long_variable():
    var = pynetsnmp.Varbind(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr', '0'
    )
    assert var.tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert var.iid == '0'
    assert var.val is None
    assert var.type is None


def test_pynetsnmp_variable_doesnt_extract_iid():
    var = pynetsnmp.Varbind(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0'
    )
    assert var.tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0'
    assert var.iid is None
    assert var.val is None
    assert var.type is None


def test_pynetsnmp_numeric_variable():
    var = pynetsnmp.Varbind('.1.3.6.1.2.1.1.1.0')
    assert var.tag == '.1.3.6.1.2.1.1.1.0'
    assert var.iid == ''
    assert var.val is None
    assert var.type is None
