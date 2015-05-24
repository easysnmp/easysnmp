import platform

import netsnmp

from .fixtures import sess_v2


def test_netsnmp_v2_session_get(sess_v2):
    varlist = netsnmp.VarList(
        netsnmp.Varbind('sysUpTime', 0),
        netsnmp.Varbind('sysContact', 0),
        netsnmp.Varbind('sysLocation', 0)
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


def test_netsnmp_v2_session_get_next(sess_v2):
    varlist = netsnmp.VarList(
        netsnmp.Varbind('sysUpTime', 0),
        netsnmp.Varbind('sysContact', 0),
        netsnmp.Varbind('sysLocation', 0)
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


def test_netsnmp_v2_session_get_bulk(sess_v2):
    varlist = netsnmp.VarList(
        netsnmp.Varbind('sysUpTime'),
        netsnmp.Varbind('sysORLastChange'),
        netsnmp.Varbind('sysORID'),
        netsnmp.Varbind('sysORDescr'),
        netsnmp.Varbind('sysORUpTime')
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


def test_netsnmp_v2_session_set(sess_v2):
    varlist = netsnmp.VarList(
        netsnmp.Varbind('sysLocation', '0', 'my even newer location')
    )

    res = sess_v2.set(varlist)

    assert res == 1

    var = netsnmp.Varbind('sysLocation', '0')
    res = netsnmp.snmp_get(
        var, version=2, hostname='localhost', community='public'
    )

    assert len(res) == 1
    assert res[0] == 'my even newer location'


def test_netsnmp_v2_session_walk(sess_v2):
    varlist = netsnmp.VarList(netsnmp.Varbind('system'))

    vals = sess_v2.walk(varlist)

    assert len(vals) == 37
    assert len(varlist) == 37

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

    assert varlist[7].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORTable.sysOREntry'
        '.sysORID'
    )
    assert varlist[7].iid == '1'
    assert varlist[7].val == '.1.3.6.1.6.3.11.3.1.1'
    assert vals[7] == '.1.3.6.1.6.3.11.3.1.1'
    assert varlist[7].type == 'OBJECTID'

    assert varlist[17].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORTable.sysOREntry'
        '.sysORDescr'
    )
    assert varlist[17].iid == '1'
    assert varlist[17].val == 'The MIB for Message Processing and Dispatching.'
    assert vals[17] == 'The MIB for Message Processing and Dispatching.'
    assert varlist[17].type == 'OCTETSTR'

    assert varlist[27].tag == (
        '.iso.org.dod.internet.mgmt.mib-2.system.sysORTable.sysOREntry'
        '.sysORUpTime'
    )
    assert varlist[27].iid == '1'
    assert int(varlist[27].val) >= 0
    assert int(vals[27]) >= 0
    assert varlist[27].type == 'TICKS'
