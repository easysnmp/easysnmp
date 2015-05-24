import platform

import netsnmp

from .fixtures import sess_v1


def test_netsnmp_v1_get():
    var = netsnmp.Varbind('.1.3.6.1.2.1.1.1', '0')
    res = netsnmp.snmpget(var,
                          Version=1,
                          DestHost='localhost',
                          Community='public')

    assert len(res) == 1

    assert platform.version() in res[0]
    assert platform.version() in var.val
    assert var.tag == 'sysDescr'
    assert var.iid == '0'
    assert var.type == 'OCTETSTR'


def test_netsnmp_v1_getnext():
    var = netsnmp.Varbind('.1.3.6.1.2.1.1.1', '0')
    res = netsnmp.snmpgetnext(var,
                              Version=1,
                              DestHost='localhost',
                              Community='public')

    assert len(res) == 1

    assert var.tag == 'sysObjectID'
    assert var.iid == '0'
    assert var.val == '.1.3.6.1.4.1.8072.3.2.10'
    assert res[0] == '.1.3.6.1.4.1.8072.3.2.10'
    assert var.type == 'OBJECTID'


def test_netsnmp_v1_set():
    var = netsnmp.Varbind('sysLocation', '0')
    res = netsnmp.snmpget(var,
                          Version=1,
                          DestHost='localhost',
                          Community='public')

    assert len(res) == 1

    assert res[0] != 'my new location'

    var = netsnmp.Varbind('sysLocation', '0', 'my new location')
    res = netsnmp.snmpset(var,
                          Version=1,
                          DestHost='localhost',
                          Community='public')

    assert res == 1

    var = netsnmp.Varbind('sysLocation', '0')
    res = netsnmp.snmpget(var,
                          Version=1,
                          DestHost='localhost',
                          Community='public')

    assert len(res) == 1

    assert res[0] == 'my new location'


# TODO: This test needs completion but it seems to break SNMPD in Ubuntu 14.04
# def test_netsnmp_v1_set_restart_agent():
#     var = netsnmp.Varbind('sysUpTime', '0')
#     res = netsnmp.snmpget(var,
#                           Version=1,
#                           DestHost='localhost',
#                           Community='public')
#
#     print "uptime = ", res[0]
#
#     var = netsnmp.Varbind('versionRestartAgent','0', 1)
#     res = netsnmp.snmpset(var,
#                           Version=1,
#                           DestHost='localhost',
#                           Community='public')
#
#     var = netsnmp.Varbind('sysUpTime','0')
#     res = netsnmp.snmpget(var,
#                           Version=1,
#                           DestHost='localhost',
#                           Community='public')
#
#     print "uptime = ", res[0]


def test_netsnmp_v1_set_via_varbind():
    var = netsnmp.Varbind('nsCacheEntry')
    res = netsnmp.snmpgetnext(var,
                              Version=1,
                              DestHost='localhost',
                              Community='public')

    assert len(res) == 1

    assert var.tag == 'nsCacheTimeout'
    assert var.iid == '1.3.6.1.2.1.2.2'
    assert int(var.val) > 0
    assert int(res[0]) > 0
    assert var.type == 'INTEGER'

    var.val = 65
    res = netsnmp.snmpset(var,
                          Version=1,
                          DestHost='localhost',
                          Community='public')

    res = netsnmp.snmpget(var,
                          Version=1,
                          DestHost='localhost',
                          Community='public')

    assert len(res) == 1

    assert var.tag == 'nsCacheTimeout'
    assert var.iid == '1.3.6.1.2.1.2.2'
    assert var.val == '65'
    assert res[0] == '65'
    assert var.type == 'INTEGER'


def test_netsnmp_v1_set_multiple(sess_v1):
    vars = netsnmp.VarList(
        netsnmp.Varbind(
            '.1.3.6.1.6.3.12.1.2.1.2.116.101.115.116', '', '.1.3.6.1.6.1.1'),
        netsnmp.Varbind(
            '.1.3.6.1.6.3.12.1.2.1.3.116.101.115.116', '', '1234'),
        netsnmp.Varbind(
            '.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116', '',  4))

    res = sess_v1.set(vars)

    assert res == 1

    vars = netsnmp.VarList(netsnmp.Varbind('snmpTargetAddrTDomain'),
                           netsnmp.Varbind('snmpTargetAddrTAddress'),
                           netsnmp.Varbind('snmpTargetAddrRowStatus'))
    res = sess_v1.getnext(vars)

    assert len(vars) == 3
    assert len(res) == 3

    assert vars[0].tag == 'snmpTargetAddrTDomain'
    assert vars[0].iid == '116.101.115.116'
    assert vars[0].val == '.1.3.6.1.6.1.1'
    assert res[0] == '.1.3.6.1.6.1.1'
    assert vars[0].type == 'OBJECTID'

    assert vars[1].tag == 'snmpTargetAddrTAddress'
    assert vars[1].iid == '116.101.115.116'
    assert vars[1].val == '1234'
    assert res[1] == '1234'
    assert vars[1].type == 'OCTETSTR'

    assert vars[2].tag == 'snmpTargetAddrRowStatus'
    assert vars[2].iid == '116.101.115.116'
    assert vars[2].val == '3'
    assert res[2] == '3'
    assert vars[2].type == 'INTEGER'


def test_netsnmp_v1_set_clear(sess_v1):
    vars = netsnmp.VarList(
        netsnmp.Varbind('.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116', '', 6))

    res = sess_v1.set(vars)

    assert res == 1

    vars = netsnmp.VarList(netsnmp.Varbind('snmpTargetAddrTDomain'),
                           netsnmp.Varbind('snmpTargetAddrTAddress'),
                           netsnmp.Varbind('snmpTargetAddrRowStatus'))
    res = sess_v1.getnext(vars)

    assert len(vars) == 3
    assert len(res) == 3

    assert vars[0].tag == 'snmpUnavailableContexts'
    assert vars[0].iid == '0'
    assert vars[0].val == '0'
    assert res[0] == '0'
    assert vars[0].type == 'COUNTER'

    assert vars[1].tag == 'snmpUnavailableContexts'
    assert vars[1].iid == '0'
    assert vars[1].val == '0'
    assert res[1] == '0'
    assert vars[1].type == 'COUNTER'

    assert vars[2].tag == 'snmpUnavailableContexts'
    assert vars[2].iid == '0'
    assert vars[2].val == '0'
    assert res[2] == '0'
    assert vars[2].type == 'COUNTER'


def test_netsnmp_v1_walk():
    var = netsnmp.Varbind('system')

    res = netsnmp.snmpwalk(var,
                           Version=1,
                           DestHost='localhost',
                           Community='public')

    assert len(res) == 37

    assert platform.version() in res[0]
    assert res[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[7] == '.1.3.6.1.6.3.11.3.1.1'
    assert res[17] == 'The MIB for Message Processing and Dispatching.'
    assert int(res[27]) >= 0


def test_netsnmp_v1_walk_varlist():
    vars = netsnmp.VarList(netsnmp.Varbind('system'))
    assert len(vars) == 1
    assert vars[0].tag == 'system'
    assert vars[0].iid == ''
    assert vars[0].val is None
    assert vars[0].type is None

    res = netsnmp.snmpwalk(vars,
                           Version=1,
                           DestHost='localhost',
                           Community='public')

    assert len(res) == 37
    assert len(vars) == 37

    assert vars[0].tag == 'sysDescr'
    assert vars[0].iid == '0'
    assert platform.version() in vars[0].val
    assert vars[0].type == 'OCTETSTR'

    assert vars[3].tag == 'sysContact'
    assert vars[3].iid == '0'
    assert vars[3].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vars[3].type == 'OCTETSTR'

    assert vars[7].tag == 'sysORID'
    assert vars[7].iid == '1'
    assert vars[7].val == '.1.3.6.1.6.3.11.3.1.1'
    assert vars[7].type == 'OBJECTID'

    assert vars[17].tag == 'sysORDescr'
    assert vars[17].iid == '1'
    assert vars[17].val == 'The MIB for Message Processing and Dispatching.'
    assert vars[17].type == 'OCTETSTR'

    assert vars[27].tag == 'sysORUpTime'
    assert vars[27].iid == '1'
    assert int(vars[27].val) >= 0
    assert vars[27].type == 'TICKS'


def test_netsnmp_v1_session_get(sess_v1):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime', 0),
                           netsnmp.Varbind('sysContact', 0),
                           netsnmp.Varbind('sysLocation', 0))

    vals = sess_v1.get(vars)

    assert len(vals) == 3
    assert len(vars) == 3

    assert vars[0].tag == 'sysUpTimeInstance'
    assert vars[0].iid == ''
    assert int(vars[0].val) > 0
    assert int(vals[0]) > 0
    assert vars[0].type == 'TICKS'

    assert vars[1].tag == 'sysContact'
    assert vars[1].iid == '0'
    assert vars[1].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[1] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vars[1].type == 'OCTETSTR'

    assert vars[2].tag == 'sysLocation'
    assert vars[2].iid == '0'
    assert vars[2].val == 'my new location'
    assert vals[2] == 'my new location'
    assert vars[2].type == 'OCTETSTR'


def test_netsnmp_v1_session_getnext(sess_v1):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime', 0),
                           netsnmp.Varbind('sysContact', 0),
                           netsnmp.Varbind('sysLocation', 0))

    vals = sess_v1.getnext(vars)

    assert len(vals) == 3
    assert len(vars) == 3

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
    assert int(vars[2].val) >= 0
    assert int(vals[2]) >= 0
    assert vars[2].type == 'TICKS'


def test_netsnmp_v1_session_getbulk_unspported(sess_v1):
    vars = netsnmp.VarList(netsnmp.Varbind('sysUpTime'),
                           netsnmp.Varbind('sysORLastChange'),
                           netsnmp.Varbind('sysORID'),
                           netsnmp.Varbind('sysORDescr'),
                           netsnmp.Varbind('sysORUpTime'))

    vals = sess_v1.getbulk(2, 8, vars)

    assert vals is None

    assert len(vars) == 5

    for index, tag in enumerate([
        'sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr', 'sysORUpTime'
    ]):
        assert vars[index].tag == tag
        assert vars[index].iid == ''
        assert vars[index].val is None
        assert vars[index].type is None


def test_netsnmp_v1_session_set(sess_v1):
    vars = netsnmp.VarList(
        netsnmp.Varbind('sysLocation', '0', 'my newer location'))

    res = sess_v1.set(vars)

    assert res == 1

    var = netsnmp.Varbind('sysLocation', '0')
    res = netsnmp.snmpget(var,
                          Version=1,
                          DestHost='localhost',
                          Community='public')

    assert len(res) == 1
    assert res[0] == 'my newer location'


def test_netsnmp_v1_session_walk(sess_v1):
    vars = netsnmp.VarList(netsnmp.Varbind('system'))

    vals = sess_v1.walk(vars)

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
    assert vars[7].val == '.1.3.6.1.6.3.11.3.1.1'
    assert vals[7] == '.1.3.6.1.6.3.11.3.1.1'
    assert vars[7].type == 'OBJECTID'

    assert vars[17].tag == 'sysORDescr'
    assert vars[17].iid == '1'
    assert vars[17].val == 'The MIB for Message Processing and Dispatching.'
    assert vals[17] == 'The MIB for Message Processing and Dispatching.'
    assert vars[17].type == 'OCTETSTR'

    assert vars[27].tag == 'sysORUpTime'
    assert vars[27].iid == '1'
    assert int(vars[27].val) >= 0
    assert int(vals[27]) >= 0
    assert vars[27].type == 'TICKS'
