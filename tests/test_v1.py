import platform

import pynetsnmp

from .fixtures import sess_v1


def test_pynetsnmp_v1_get():
    var = pynetsnmp.Varbind('.1.3.6.1.2.1.1.1', '0')
    res = pynetsnmp.snmp_get(
        var, version=1, hostname='localhost', community='public'
    )

    assert len(res) == 1

    assert platform.version() in res[0]
    assert platform.version() in var.val
    assert var.tag == 'sysDescr'
    assert var.iid == '0'
    assert var.type == 'OCTETSTR'


def test_pynetsnmp_v1_get_next():
    var = pynetsnmp.Varbind('.1.3.6.1.2.1.1.1', '0')
    res = pynetsnmp.snmp_get_next(
        var, version=1, hostname='localhost', community='public'
    )

    assert len(res) == 1

    assert var.tag == 'sysObjectID'
    assert var.iid == '0'
    assert var.val == '.1.3.6.1.4.1.8072.3.2.10'
    assert res[0] == '.1.3.6.1.4.1.8072.3.2.10'
    assert var.type == 'OBJECTID'


def test_pynetsnmp_v1_set():
    var = pynetsnmp.Varbind('sysLocation', '0')
    res = pynetsnmp.snmp_get(
        var, version=1, hostname='localhost', community='public'
    )

    assert len(res) == 1

    assert res[0] != 'my new location'

    var = pynetsnmp.Varbind('sysLocation', '0', 'my new location')
    res = pynetsnmp.snmp_set(
        var, version=1, hostname='localhost', community='public'
    )

    assert res == 1

    var = pynetsnmp.Varbind('sysLocation', '0')
    res = pynetsnmp.snmp_get(
        var, version=1, hostname='localhost', community='public'
    )

    assert len(res) == 1

    assert res[0] == 'my new location'


# TODO: This test needs completion but it seems to break SNMPD in Ubuntu 14.04
# def test_pynetsnmp_v1_set_restart_agent():
#     var = pynetsnmp.Varbind('sysUpTime', '0')
#     res = pynetsnmp.snmp_get(
#         var, version=1, hostname='localhost', community='public'
#     )

#     print "uptime = ", res[0]

#     var = pynetsnmp.Varbind('versionRestartAgent','0', 1)
#     res = pynetsnmp.snmp_set(
#         var, version=1, hostname='localhost', community='public'
#     )

#     var = pynetsnmp.Varbind('sysUpTime','0')
#     res = pynetsnmp.snmp_get(
#         var, version=1, hostname='localhost', community='public'
#     )

#     print "uptime = ", res[0]


def test_pynetsnmp_v1_set_via_varbind():
    var = pynetsnmp.Varbind('nsCacheEntry')
    res = pynetsnmp.snmp_get_next(
        var, version=1, hostname='localhost', community='public'
    )

    assert len(res) == 1

    assert var.tag == 'nsCacheTimeout'
    assert var.iid == '1.3.6.1.2.1.2.2'
    assert int(var.val) > 0
    assert int(res[0]) > 0
    assert var.type == 'INTEGER'

    var.val = 65
    res = pynetsnmp.snmp_set(
        var, version=1, hostname='localhost', community='public'
    )

    res = pynetsnmp.snmp_get(
        var, version=1, hostname='localhost', community='public'
    )

    assert len(res) == 1

    assert var.tag == 'nsCacheTimeout'
    assert var.iid == '1.3.6.1.2.1.2.2'
    assert var.val == '65'
    assert res[0] == '65'
    assert var.type == 'INTEGER'


def test_pynetsnmp_v1_set_multiple(sess_v1):
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind(
            '.1.3.6.1.6.3.12.1.2.1.2.116.101.115.116', '', '.1.3.6.1.6.1.1'
        ),
        pynetsnmp.Varbind(
            '.1.3.6.1.6.3.12.1.2.1.3.116.101.115.116', '', '1234'
        ),
        pynetsnmp.Varbind(
            '.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116', '',  4
        )
    )

    res = sess_v1.set(varlist)

    assert res == 1

    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('snmpTargetAddrTDomain'),
        pynetsnmp.Varbind('snmpTargetAddrTAddress'),
        pynetsnmp.Varbind('snmpTargetAddrRowStatus')
    )
    res = sess_v1.get_next(varlist)

    assert len(varlist) == 3
    assert len(res) == 3

    assert varlist[0].tag == 'snmpTargetAddrTDomain'
    assert varlist[0].iid == '116.101.115.116'
    assert varlist[0].val == '.1.3.6.1.6.1.1'
    assert res[0] == '.1.3.6.1.6.1.1'
    assert varlist[0].type == 'OBJECTID'

    assert varlist[1].tag == 'snmpTargetAddrTAddress'
    assert varlist[1].iid == '116.101.115.116'
    assert varlist[1].val == '1234'
    assert res[1] == '1234'
    assert varlist[1].type == 'OCTETSTR'

    assert varlist[2].tag == 'snmpTargetAddrRowStatus'
    assert varlist[2].iid == '116.101.115.116'
    assert varlist[2].val == '3'
    assert res[2] == '3'
    assert varlist[2].type == 'INTEGER'


def test_pynetsnmp_v1_set_clear(sess_v1):
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116', '', 6)
    )

    res = sess_v1.set(varlist)

    assert res == 1

    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('snmpTargetAddrTDomain'),
        pynetsnmp.Varbind('snmpTargetAddrTAddress'),
        pynetsnmp.Varbind('snmpTargetAddrRowStatus')
    )
    res = sess_v1.get_next(varlist)

    assert len(varlist) == 3
    assert len(res) == 3

    assert varlist[0].tag == 'snmpUnavailableContexts'
    assert varlist[0].iid == '0'
    assert varlist[0].val == '0'
    assert res[0] == '0'
    assert varlist[0].type == 'COUNTER'

    assert varlist[1].tag == 'snmpUnavailableContexts'
    assert varlist[1].iid == '0'
    assert varlist[1].val == '0'
    assert res[1] == '0'
    assert varlist[1].type == 'COUNTER'

    assert varlist[2].tag == 'snmpUnavailableContexts'
    assert varlist[2].iid == '0'
    assert varlist[2].val == '0'
    assert res[2] == '0'
    assert varlist[2].type == 'COUNTER'


def test_pynetsnmp_v1_walk():
    var = pynetsnmp.Varbind('system')

    res = pynetsnmp.snmp_walk(
        var, version=1, hostname='localhost', community='public'
    )

    assert len(res) >= 7

    assert platform.version() in res[0]
    assert res[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[4] == platform.node()
    assert res[5] == 'my new location'


def test_pynetsnmp_v1_walk_varlist():
    varlist = pynetsnmp.VarList(pynetsnmp.Varbind('system'))
    assert len(varlist) == 1
    assert varlist[0].tag == 'system'
    assert varlist[0].iid == ''
    assert varlist[0].val is None
    assert varlist[0].type is None

    res = pynetsnmp.snmp_walk(
        varlist, version=1, hostname='localhost', community='public'
    )

    assert len(res) >= 7
    assert len(varlist) >= 7

    assert varlist[0].tag == 'sysDescr'
    assert varlist[0].iid == '0'
    assert platform.version() in varlist[0].val
    assert varlist[0].type == 'OCTETSTR'

    assert varlist[3].tag == 'sysContact'
    assert varlist[3].iid == '0'
    assert varlist[3].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert varlist[3].type == 'OCTETSTR'

    assert varlist[4].tag == 'sysName'
    assert varlist[4].iid == '0'
    assert varlist[4].val == platform.node()
    assert varlist[4].type == 'OCTETSTR'

    assert varlist[5].tag == 'sysLocation'
    assert varlist[5].iid == '0'
    assert varlist[5].val == 'my new location'
    assert varlist[5].type == 'OCTETSTR'


def test_pynetsnmp_v1_session_get(sess_v1):
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('sysUpTime', 0),
        pynetsnmp.Varbind('sysContact', 0),
        pynetsnmp.Varbind('sysLocation', 0)
    )

    vals = sess_v1.get(varlist)

    assert len(vals) == 3
    assert len(varlist) == 3

    assert varlist[0].tag == 'sysUpTimeInstance'
    assert varlist[0].iid == ''
    assert int(varlist[0].val) > 0
    assert int(vals[0]) > 0
    assert varlist[0].type == 'TICKS'

    assert varlist[1].tag == 'sysContact'
    assert varlist[1].iid == '0'
    assert varlist[1].val == 'G. S. Marzot <gmarzot@marzot.net>'
    assert vals[1] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert varlist[1].type == 'OCTETSTR'

    assert varlist[2].tag == 'sysLocation'
    assert varlist[2].iid == '0'
    assert varlist[2].val == 'my new location'
    assert vals[2] == 'my new location'
    assert varlist[2].type == 'OCTETSTR'


def test_pynetsnmp_v1_session_get_next(sess_v1):
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('sysUpTime', 0),
        pynetsnmp.Varbind('sysContact', 0),
        pynetsnmp.Varbind('sysLocation', 0)
    )

    vals = sess_v1.get_next(varlist)

    assert len(vals) == 3
    assert len(varlist) == 3

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
    assert int(varlist[2].val) >= 0
    assert int(vals[2]) >= 0
    assert varlist[2].type == 'TICKS'


def test_pynetsnmp_v1_session_get_bulk_unspported(sess_v1):
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('sysUpTime'),
        pynetsnmp.Varbind('sysORLastChange'),
        pynetsnmp.Varbind('sysORID'),
        pynetsnmp.Varbind('sysORDescr'),
        pynetsnmp.Varbind('sysORUpTime')
    )

    vals = sess_v1.get_bulk(2, 8, varlist)

    assert vals is None

    assert len(varlist) == 5

    for index, tag in enumerate([
        'sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr', 'sysORUpTime'
    ]):
        assert varlist[index].tag == tag
        assert varlist[index].iid == ''
        assert varlist[index].val is None
        assert varlist[index].type is None


def test_pynetsnmp_v1_session_set(sess_v1):
    varlist = pynetsnmp.VarList(
        pynetsnmp.Varbind('sysLocation', '0', 'my newer location'))

    res = sess_v1.set(varlist)

    assert res == 1

    var = pynetsnmp.Varbind('sysLocation', '0')
    res = pynetsnmp.snmp_get(
        var, version=1, hostname='localhost', community='public'
    )

    assert len(res) == 1
    assert res[0] == 'my newer location'


def test_pynetsnmp_v1_session_walk(sess_v1):
    varlist = pynetsnmp.VarList(pynetsnmp.Varbind('system'))

    vals = sess_v1.walk(varlist)

    assert len(vals) >= 7
    assert len(varlist) >= 7

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

    assert varlist[4].tag == 'sysName'
    assert varlist[4].iid == '0'
    assert varlist[4].val == platform.node()
    assert vals[4] == platform.node()
    assert varlist[4].type == 'OCTETSTR'

    assert varlist[5].tag == 'sysLocation'
    assert varlist[5].iid == '0'
    assert varlist[5].val == 'my newer location'
    assert vals[5] >= 'my newer location'
    assert varlist[5].type == 'OCTETSTR'
