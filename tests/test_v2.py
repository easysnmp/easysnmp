import platform

import netsnmp

from .fixtures import sess_v2


def test_netsnmp_v2_session_get(sess_v2):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime', 0),
                           netsnmp.Varbind('sysContact', 0),
                           netsnmp.Varbind('sysLocation', 0))
    vals = sess_v2.get(vars)

    assert len(vals) == 3
    assert len(vars) == 3

    assert vars[0].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysUpTime.sysUpTimeInstance')
    assert vars[0].iid == ''
    assert int(vars[0].val) > 0
    assert int(vals[0]) > 0
    assert vars[0].type == 'TICKS'

    assert vars[1].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysContact'
    assert vars[1].iid == '0'
    assert vars[1].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[1] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vars[1].type == 'OCTETSTR'

    assert vars[2].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysLocation'
    assert vars[2].iid == '0'
    assert vars[2].val == 'my newer location'
    assert vals[2] == 'my newer location'
    assert vars[2].type == 'OCTETSTR'


def test_netsnmp_v2_session_get_next(sess_v2):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime', 0),
                           netsnmp.Varbind('sysContact', 0),
                           netsnmp.Varbind('sysLocation', 0))

    vals = sess_v2.get_next(vars)

    assert len(vals) == 3
    assert len(vars) == 3

    assert vars[0].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysContact'
    assert vars[0].iid == '0'
    assert vars[0].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[0] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vars[0].type == 'OCTETSTR'

    assert vars[1].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysName'
    assert vars[1].iid == '0'
    assert vars[1].val == platform.node()
    assert vals[1] == platform.node()
    assert vars[1].type == 'OCTETSTR'

    assert vars[2].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORLastChange')
    assert vars[2].iid == '0'
    assert int(vars[2].val) >= 0
    assert int(vals[2]) >= 0
    assert vars[2].type == 'TICKS'


def test_netsnmp_v2_session_get_bulk(sess_v2):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime'),
                           netsnmp.Varbind('sysORLastChange'),
                           netsnmp.Varbind('sysORID'),
                           netsnmp.Varbind('sysORDescr'),
                           netsnmp.Varbind('sysORUpTime'))

    vals = sess_v2.get_bulk(2, 8, vars)

    assert len(vals) == 26
    assert len(vars) == 26

    assert vars[0].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysUpTime.sysUpTimeInstance')
    assert vars[0].iid == ''
    assert int(vars[0].val) > 0
    assert vars[0].type == 'TICKS'

    assert vars[4].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORTable'
        '.sysOREntry.sysORUpTime')
    assert vars[4].iid == '1'
    assert int(vars[4].val) >= 0
    assert vars[4].type == 'TICKS'


def test_netsnmp_v2_session_set(sess_v2):
    vars = netsnmp.VarList(
        netsnmp.Varbind('sysLocation', '0', 'my even newer location'))

    res = sess_v2.set(vars)

    assert res == 1

    var = netsnmp.Varbind('sysLocation', '0')
    res = netsnmp.snmp_get(var,
                           version=2,
                           hostname='localhost',
                           community='public')

    assert len(res) == 1
    assert res[0] == 'my even newer location'


def test_netsnmp_v2_session_walk(sess_v2):
    vars = netsnmp.VarList(netsnmp.Varbind('system'))

    vals = sess_v2.walk(vars)

    assert len(vals) == 37
    assert len(vars) == 37

    assert vars[0].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
    assert vars[0].iid == '0'
    assert platform.version() in vars[0].val
    assert platform.version() in vals[0]
    assert vars[0].type == 'OCTETSTR'

    assert vars[3].tag == '.iso.org.dod.internet.mgmt.mib-2.system.sysContact'
    assert vars[3].iid == '0'
    assert vars[3].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vars[3].type == 'OCTETSTR'

    assert vars[7].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORTable.sysOREntry'
        '.sysORID')
    assert vars[7].iid == '1'
    assert vars[7].val == '.1.3.6.1.6.3.11.3.1.1'
    assert vals[7] == '.1.3.6.1.6.3.11.3.1.1'
    assert vars[7].type == 'OBJECTID'

    assert vars[17].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORTable.sysOREntry'
        '.sysORDescr')
    assert vars[17].iid == '1'
    assert vars[17].val == 'The MIB for Message Processing and Dispatching.'
    assert vals[17] == 'The MIB for Message Processing and Dispatching.'
    assert vars[17].type == 'OCTETSTR'

    assert vars[27].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORTable.sysOREntry'
        '.sysORUpTime')
    assert vars[27].iid == '1'
    assert int(vars[27].val) >= 0
    assert int(vals[27]) >= 0
    assert vars[27].type == 'TICKS'
