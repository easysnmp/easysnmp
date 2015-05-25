import platform

import pynetsnmp

from .fixtures import sess_v2  # noqa


def test_pynetsnmp_v2_session_get(sess_v2):  # noqa
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('sysUpTime', 0),
        pynetsnmp.Varbind('sysContact', 0),
        pynetsnmp.Varbind('sysLocation', 0)
    )
    vals = sess_v2.get(varlist)

    assert len(vals) == 3
    assert len(varlist) == 3

    assert varlist[0].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysUpTime.sysUpTimeInstance'
    )
    assert varlist[0].iid == ''
    assert int(varlist[0].val) > 0
    assert int(vals[0]) > 0
    assert varlist[0].type == 'TICKS'

    assert varlist[1].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysContact'
    )
    assert varlist[1].iid == '0'
    assert varlist[1].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[1] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert varlist[1].type == 'OCTETSTR'

    assert varlist[2].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysLocation'
    )
    assert varlist[2].iid == '0'
    assert varlist[2].val == 'my newer location'
    assert vals[2] == 'my newer location'
    assert varlist[2].type == 'OCTETSTR'


def test_pynetsnmp_v2_session_get_next(sess_v2):  # noqa
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('sysUpTime', 0),
        pynetsnmp.Varbind('sysContact', 0),
        pynetsnmp.Varbind('sysLocation', 0)
    )

    vals = sess_v2.get_next(varlist)

    assert len(vals) == 3
    assert len(varlist) == 3

    assert varlist[0].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysContact'
    )
    assert varlist[0].iid == '0'
    assert varlist[0].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[0] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert varlist[0].type == 'OCTETSTR'

    assert varlist[1].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysName'
    assert varlist[1].iid == '0'
    assert varlist[1].val == platform.node()
    assert vals[1] == platform.node()
    assert varlist[1].type == 'OCTETSTR'

    assert varlist[2].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORLastChange')
    assert varlist[2].iid == '0'
    assert int(varlist[2].val) >= 0
    assert int(vals[2]) >= 0
    assert varlist[2].type == 'TICKS'


def test_pynetsnmp_v2_session_get_bulk(sess_v2):  # noqa
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('sysUpTime'),
        pynetsnmp.Varbind('sysORLastChange'),
        pynetsnmp.Varbind('sysORID'),
        pynetsnmp.Varbind('sysORDescr'),
        pynetsnmp.Varbind('sysORUpTime')
    )

    vals = sess_v2.get_bulk(2, 8, varlist)

    assert len(vals) == 26
    assert len(varlist) == 26

    assert varlist[0].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysUpTime.sysUpTimeInstance'
    )
    assert varlist[0].iid == ''
    assert int(varlist[0].val) > 0
    assert varlist[0].type == 'TICKS'

    assert varlist[4].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORTable'
        '.sysOREntry.sysORUpTime')
    assert varlist[4].iid == '1'
    assert int(varlist[4].val) >= 0
    assert varlist[4].type == 'TICKS'


def test_pynetsnmp_v2_session_set(sess_v2):  # noqa
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('sysLocation', '0', 'my even newer location')
    )

    res = sess_v2.set(varlist)

    assert res == 1

    var = pynetsnmp.Varbind('sysLocation', '0')
    res = pynetsnmp.snmp_get(
        var, version=2, hostname='localhost', community='public'
    )

    assert len(res) == 1
    assert res[0] == 'my even newer location'


def test_pynetsnmp_v2_session_walk(sess_v2):  # noqa
    varlist = pynetsnmp.VarList(pynetsnmp.Varbind('system'))

    vals = sess_v2.walk(varlist)

    assert len(vals) >= 7
    assert len(varlist) >= 7

    assert varlist[0].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert varlist[0].iid == '0'
    assert platform.version() in varlist[0].val
    assert platform.version() in vals[0]
    assert varlist[0].type == 'OCTETSTR'

    assert varlist[3].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysContact'
    )
    assert varlist[3].iid == '0'
    assert varlist[3].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert varlist[3].type == 'OCTETSTR'

    assert varlist[4].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysName'
    assert varlist[4].iid == '0'
    assert varlist[4].val == platform.node()
    assert vals[4] == platform.node()
    assert varlist[4].type == 'OCTETSTR'

    assert varlist[5].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysLocation'
    )
    assert varlist[5].iid == '0'
    assert varlist[5].val == 'my even newer location'
    assert vals[5] >= 'my even newer location'
    assert varlist[5].type == 'OCTETSTR'
