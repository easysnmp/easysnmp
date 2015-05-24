import platform

import netsnmp

from .fixtures import sess_v3


def test_netsnmp_v3_session_get(sess_v3):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime', 0),
                           netsnmp.Varbind('sysContact', 0),
                           netsnmp.Varbind('sysLocation', 0))

    vals = sess_v3.get(vars)

    assert len(vals) == 3
    assert len(vars) == 3

    assert vars[0].tag == 'sysUpTimeInstance'
    assert vars[0].iid == ''
    assert ':' in vars[0].val
    assert ':' in vals[0]
    assert vars[0].type == 'TICKS'

    assert vars[1].tag == 'sysContact'
    assert vars[1].iid == '0'
    assert vars[1].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[1] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vars[1].type == 'OCTETSTR'

    assert vars[2].tag == 'sysLocation'
    assert vars[2].iid == '0'
    assert vars[2].val == 'my even newer location'
    assert vals[2] == 'my even newer location'
    assert vars[2].type == 'OCTETSTR'


def test_netsnmp_v3_session_getnext(sess_v3):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime', 0),
                           netsnmp.Varbind('sysContact', 0),
                           netsnmp.Varbind('sysLocation', 0))

    vals = sess_v3.getnext(vars)

    assert len(vars) == 3
    assert len(vals) == 3

    assert vars[0].tag == 'sysContact'
    assert vars[0].iid == '0'
    assert vars[0].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[0] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vars[0].type == 'OCTETSTR'

    assert vars[1].tag == 'sysName'
    assert vars[1].iid == '0'
    assert vars[1].val == platform.node()
    assert vals[1] == platform.node()
    assert vars[1].type == 'OCTETSTR'

    assert vars[2].tag == 'sysORLastChange'
    assert vars[2].iid == '0'
    assert ':' in vars[2].val
    assert ':' in vals[2]
    assert vars[2].type == 'TICKS'


def test_netsnmp_v3_session_getbulk(sess_v3):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime'),
                           netsnmp.Varbind('sysORLastChange'),
                           netsnmp.Varbind('sysORID'),
                           netsnmp.Varbind('sysORDescr'),
                           netsnmp.Varbind('sysORUpTime'))

    vals = sess_v3.getbulk(2, 8, vars)

    assert len(vals) == 26
    assert len(vars) == 26

    assert vars[0].tag == 'sysUpTimeInstance'
    assert vars[0].iid == ''
    assert ':' in vars[0].val
    assert vars[0].type == 'TICKS'

    assert vars[4].tag == 'sysORUpTime'
    assert vars[4].iid == '1'
    assert ':' in vars[4].val
    assert vars[4].type == 'TICKS'


def test_netsnmp_v3_session_set(sess_v3):
    vars = netsnmp.VarList(
        netsnmp.Varbind('sysLocation', '0', 'my final destination'))

    res = sess_v3.set(vars)

    assert res == 1

    var = netsnmp.Varbind('sysLocation', '0')
    res = netsnmp.snmpget(var,
                          Version=3,
                          DestHost='localhost',
                          SecLevel='authPriv',
                          SecName='initial',
                          PrivPass='priv_pass',
                          AuthPass='auth_pass')

    assert len(res) == 1
    assert res[0] == 'my final destination'


def test_netsnmp_v3_session_walk(sess_v3):
    vars = netsnmp.VarList(netsnmp.Varbind('system'))

    vals = sess_v3.walk(vars)

    assert len(vals) == 37
    assert len(vars) == 37

    assert vars[0].tag == 'sysDescr'
    assert vars[0].iid == '0'
    assert platform.version() in vars[0].val
    assert platform.version() in vals[0]
    assert vars[0].type == 'OCTETSTR'

    assert vars[3].tag == 'sysContact'
    assert vars[3].iid == '0'
    assert vars[3].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vars[3].type == 'OCTETSTR'

    assert vars[7].tag == 'sysORID'
    assert vars[7].iid == '1'
    assert vars[7].val == 'snmpMPDCompliance'
    assert vals[7] == 'snmpMPDCompliance'
    assert vars[7].type == 'OBJECTID'

    assert vars[17].tag == 'sysORDescr'
    assert vars[17].iid == '1'
    assert vars[17].val == 'The MIB for Message Processing and Dispatching.'
    assert vals[17] == 'The MIB for Message Processing and Dispatching.'
    assert vars[17].type == 'OCTETSTR'

    assert vars[27].tag == 'sysORUpTime'
    assert vars[27].iid == '1'
    assert ':' in vars[27].val
    assert ':' in vals[27]
    assert vars[27].type == 'TICKS'
