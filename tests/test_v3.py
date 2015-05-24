import platform

import netsnmp

from .fixtures import sess_v3


def test_netsnmp_v3_session_get(sess_v3):
    varlist = netsnmp.VarList(
        netsnmp.Varbind('sysUpTime', 0),
        netsnmp.Varbind('sysContact', 0),
        netsnmp.Varbind('sysLocation', 0)
    )

    vals = sess_v3.get(varlist)

    assert len(vals) == 3
    assert len(varlist) == 3

    assert varlist[0].tag == 'sysUpTimeInstance'
    assert varlist[0].iid == ''
    assert ':' in varlist[0].val
    assert ':' in vals[0]
    assert varlist[0].type == 'TICKS'

    assert varlist[1].tag == 'sysContact'
    assert varlist[1].iid == '0'
    assert varlist[1].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[1] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert varlist[1].type == 'OCTETSTR'

    assert varlist[2].tag == 'sysLocation'
    assert varlist[2].iid == '0'
    assert varlist[2].val == 'my even newer location'
    assert vals[2] == 'my even newer location'
    assert varlist[2].type == 'OCTETSTR'


def test_netsnmp_v3_session_get_next(sess_v3):
    varlist = netsnmp.VarList(
        netsnmp.Varbind('sysUpTime', 0),
        netsnmp.Varbind('sysContact', 0),
        netsnmp.Varbind('sysLocation', 0)
    )

    vals = sess_v3.get_next(varlist)

    assert len(varlist) == 3
    assert len(vals) == 3

    assert varlist[0].tag == 'sysContact'
    assert varlist[0].iid == '0'
    assert varlist[0].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[0] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert varlist[0].type == 'OCTETSTR'

    assert varlist[1].tag == 'sysName'
    assert varlist[1].iid == '0'
    assert varlist[1].val == platform.node()
    assert vals[1] == platform.node()
    assert varlist[1].type == 'OCTETSTR'

    assert varlist[2].tag == 'sysORLastChange'
    assert varlist[2].iid == '0'
    assert ':' in varlist[2].val
    assert ':' in vals[2]
    assert varlist[2].type == 'TICKS'


def test_netsnmp_v3_session_get_bulk(sess_v3):
    varlist = netsnmp.VarList(
        netsnmp.Varbind('sysUpTime'),
        netsnmp.Varbind('sysORLastChange'),
        netsnmp.Varbind('sysORID'),
        netsnmp.Varbind('sysORDescr'),
        netsnmp.Varbind('sysORUpTime')
    )

    vals = sess_v3.get_bulk(2, 8, varlist)

    assert len(vals) == 26
    assert len(varlist) == 26

    assert varlist[0].tag == 'sysUpTimeInstance'
    assert varlist[0].iid == ''
    assert ':' in varlist[0].val
    assert varlist[0].type == 'TICKS'

    assert varlist[4].tag == 'sysORUpTime'
    assert varlist[4].iid == '1'
    assert ':' in varlist[4].val
    assert varlist[4].type == 'TICKS'


def test_netsnmp_v3_session_set(sess_v3):
    varlist = netsnmp.VarList(
        netsnmp.Varbind('sysLocation', '0', 'my final destination'))

    res = sess_v3.set(varlist)

    assert res == 1

    var = netsnmp.Varbind('sysLocation', '0')
    res = netsnmp.snmp_get(
        var, version=3, hostname='localhost',
        security_level='authPriv', security_username='initial',
        privacy_password='priv_pass', auth_password='auth_pass'
    )

    assert len(res) == 1
    assert res[0] == 'my final destination'


def test_netsnmp_v3_session_walk(sess_v3):
    varlist = netsnmp.VarList(netsnmp.Varbind('system'))

    vals = sess_v3.walk(varlist)

    assert len(vals) == 37
    assert len(varlist) == 37

    assert varlist[0].tag == 'sysDescr'
    assert varlist[0].iid == '0'
    assert platform.version() in varlist[0].val
    assert platform.version() in vals[0]
    assert varlist[0].type == 'OCTETSTR'

    assert varlist[3].tag == 'sysContact'
    assert varlist[3].iid == '0'
    assert varlist[3].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert varlist[3].type == 'OCTETSTR'

    assert varlist[7].tag == 'sysORID'
    assert varlist[7].iid == '1'
    assert varlist[7].val == 'snmpMPDCompliance'
    assert vals[7] == 'snmpMPDCompliance'
    assert varlist[7].type == 'OBJECTID'

    assert varlist[17].tag == 'sysORDescr'
    assert varlist[17].iid == '1'
    assert varlist[17].val == 'The MIB for Message Processing and Dispatching.'
    assert vals[17] == 'The MIB for Message Processing and Dispatching.'
    assert varlist[17].type == 'OCTETSTR'

    assert varlist[27].tag == 'sysORUpTime'
    assert varlist[27].iid == '1'
    assert ':' in varlist[27].val
    assert ':' in vals[27]
    assert varlist[27].type == 'TICKS'
