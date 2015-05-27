import platform

import pytest
import easysnmp

from .fixtures import sess_v1  # noqa


def test_easysnmp_v1_get():
    res = easysnmp.snmp_get(
        ('.1.3.6.1.2.1.1.1', 0),
        version=1, hostname='localhost', community='public'
    )

    assert platform.version() in res
    assert res.snmp_oid == 'sysDescr'
    assert res.snmp_oid_index == 0
    assert res.snmp_type == 'OCTETSTR'


def test_easysnmp_v1_get_next():
    res = easysnmp.snmp_get_next(
        ('.1.3.6.1.2.1.1.1', 0),
        version=1, hostname='localhost', community='public'
    )

    assert res.snmp_oid == 'sysObjectID'
    assert res.snmp_oid_index == 0
    assert res == '.1.3.6.1.4.1.8072.3.2.10'
    assert res.snmp_type == 'OBJECTID'


def test_easysnmp_v1_set():
    res = easysnmp.snmp_get(
        ('sysLocation', 0),
        version=1, hostname='localhost', community='public'
    )
    assert res != 'my new location'

    success = easysnmp.snmp_set(
        ('sysLocation', 0), 'my new location',
        version=1, hostname='localhost', community='public'
    )
    assert success

    res = easysnmp.snmp_get(
        ('sysLocation', 0),
        version=1, hostname='localhost', community='public'
    )
    assert res == 'my new location'


# TODO: This test needs completion but it seems to break SNMPD in Ubuntu 14.04
# def test_easysnmp_v1_set_restart_agent():
#     var = easysnmp.Varbind('sysUpTime', '0')
#     res = easysnmp.snmp_get(
#         var, version=1, hostname='localhost', community='public'
#     )

#     print "uptime = ", res[0]

#     var = easysnmp.Varbind('versionRestartAgent','0', 1)
#     res = easysnmp.snmp_set(
#         var, version=1, hostname='localhost', community='public'
#     )

#     var = easysnmp.Varbind('sysUpTime','0')
#     res = easysnmp.snmp_get(
#         var, version=1, hostname='localhost', community='public'
#     )

#     print "uptime = ", res[0]


def test_easysnmp_v1_set_next():
    res = easysnmp.snmp_get_next(
        'nsCacheEntry', version=1, hostname='localhost', community='public'
    )

    assert res.snmp_oid == 'nsCacheTimeout'
    assert res.snmp_oid_index == '1.3.6.1.2.1.2.2'
    assert res > 0
    assert res.snmp_type == 'INTEGER'

    res = easysnmp.snmp_set(
        'nsCacheEntry', 65,
        version=1, hostname='localhost', community='public'
    )

    res = easysnmp.snmp_get(
        'nsCacheEntry', version=1, hostname='localhost', community='public'
    )

    assert res.snmp_oid == 'nsCacheTimeout'
    assert res.snmp_oid_index == '1.3.6.1.2.1.2.2'
    assert res == 65
    assert res.snmp_type == 'INTEGER'


def test_easysnmp_v1_set_multiple(sess_v1):  # noqa
    success = sess_v1.set_multiple({
        '.1.3.6.1.6.3.12.1.2.1.2.116.101.115.116': '.1.3.6.1.6.1.1',
        '.1.3.6.1.6.3.12.1.2.1.3.116.101.115.116': '1234',
        '.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116':  4
    })
    assert success

    res = sess_v1.get_next([
        'snmpTargetAddrTDomain', 'snmpTargetAddrTAddress',
        'snmpTargetAddrRowStatus'
    ])

    assert len(res) == 3

    assert res[0].snmp_oid == 'snmpTargetAddrTDomain'
    assert res[0].snmp_oid_index == '116.101.115.116'
    assert res[0] == '.1.3.6.1.6.1.1'
    assert res[0].snmp_type == 'OBJECTID'

    assert res[1].snmp_oid == 'snmpTargetAddrTAddress'
    assert res[1].snmp_oid_index == '116.101.115.116'
    assert res[1] == '1234'
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].snmp_oid == 'snmpTargetAddrRowStatus'
    assert res[2].snmp_oid_index == '116.101.115.116'
    assert res[2] == 3
    assert res[2].snmp_type == 'INTEGER'


def test_easysnmp_v1_set_clear(sess_v1):  # noqa
    res = sess_v1.set('.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116', 6)
    assert res == 1

    res = sess_v1.get_next([
        'snmpTargetAddrTDomain', 'snmpTargetAddrTAddress',
        'snmpTargetAddrRowStatus'
    ])

    assert len(res) == 3

    assert res[0].snmp_oid == 'snmpUnavailableContexts'
    assert res[0].snmp_oid_index == 0
    assert res[0] == 0
    assert res[0].snmp_type == 'COUNTER'

    assert res[1].snmp_oid == 'snmpUnavailableContexts'
    assert res[1].snmp_oid_index == 0
    assert res[1] == 0
    assert res[1].snmp_type == 'COUNTER'

    assert res[2].snmp_oid == 'snmpUnavailableContexts'
    assert res[2].snmp_oid_index == 0
    assert res[2] == 0
    assert res[2].snmp_type == 'COUNTER'


def test_easysnmp_v1_walk():
    res = easysnmp.snmp_walk(
        'system', version=1, hostname='localhost', community='public'
    )
    assert len(res) >= 7

    assert platform.version() in res[0]
    assert res[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[4] == platform.node()
    assert res[5] == 'my new location'


def test_easysnmp_v1_walk_res():
    res = easysnmp.snmp_walk(
        'system', version=1, hostname='localhost', community='public'
    )

    assert len(res) >= 7

    assert res[0].snmp_oid == 'sysDescr'
    assert res[0].snmp_oid_index == 0
    assert platform.version() in res[0]
    assert res[0].snmp_type == 'OCTETSTR'

    assert res[3].snmp_oid == 'sysContact'
    assert res[3].snmp_oid_index == 0
    assert res[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[3].snmp_type == 'OCTETSTR'

    assert res[4].snmp_oid == 'sysName'
    assert res[4].snmp_oid_index == 0
    assert res[4] == platform.node()
    assert res[4].snmp_type == 'OCTETSTR'

    assert res[5].snmp_oid == 'sysLocation'
    assert res[5].snmp_oid_index == 0
    assert res[5] == 'my new location'
    assert res[5].snmp_type == 'OCTETSTR'


def test_easysnmp_v1_session_get(sess_v1):  # noqa
    res = sess_v1.get([
        ('sysUpTime', 0),
        ('sysContact', 0),
        ('sysLocation', 0)
    ])

    assert len(res) == 3

    assert res[0].snmp_oid == 'sysUpTimeInstance'
    assert res[0].snmp_oid_index is None
    assert res[0] > 0
    assert res[0].snmp_type == 'TICKS'

    assert res[1].snmp_oid == 'sysContact'
    assert res[1].snmp_oid_index == 0
    assert res[1] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].snmp_oid == 'sysLocation'
    assert res[2].snmp_oid_index == 0
    assert res[2] == 'my new location'
    assert res[2].snmp_type == 'OCTETSTR'


def test_easysnmp_v1_session_get_next(sess_v1):  # noqa
    res = sess_v1.get_next([
        ('sysUpTime', 0),
        ('sysContact', 0),
        ('sysLocation', 0)
    ])

    assert len(res) == 3

    assert res[0].snmp_oid == 'sysContact'
    assert res[0].snmp_oid_index == 0
    assert res[0] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[0].snmp_type == 'OCTETSTR'

    assert res[1].snmp_oid == 'sysName'
    assert res[1].snmp_oid_index == 0
    assert res[1] == platform.node()
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].snmp_oid == 'sysORLastChange'
    assert res[2].snmp_oid_index == 0
    assert int(res[2]) >= 0
    assert res[2].snmp_type == 'TICKS'


def test_easysnmp_v1_session_get_bulk_unspported(sess_v1):  # noqa
    with pytest.raises(easysnmp.EasySNMPError):
        sess_v1.get_bulk(
            ['sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
             'sysORUpTime'],
            2, 8
        )


def test_easysnmp_v1_session_set(sess_v1):  # noqa
    res = sess_v1.set(('sysLocation', 0), 'my newer location')
    assert res == 1

    res = easysnmp.snmp_get(
        'sysLocation.0', version=1, hostname='localhost', community='public'
    )
    assert res == 'my newer location'


def test_easysnmp_v1_session_walk(sess_v1):  # noqa
    res = sess_v1.walk('system')

    assert len(res) >= 7

    assert res[0].snmp_oid == 'sysDescr'
    assert res[0].snmp_oid_index == 0
    assert platform.version() in res[0]
    assert res[0].snmp_type == 'OCTETSTR'

    assert res[3].snmp_oid == 'sysContact'
    assert res[3].snmp_oid_index == 0
    assert res[3] == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[3].snmp_type == 'OCTETSTR'

    assert res[4].snmp_oid == 'sysName'
    assert res[4].snmp_oid_index == 0
    assert res[4] == platform.node()
    assert res[4].snmp_type == 'OCTETSTR'

    assert res[5].snmp_oid == 'sysLocation'
    assert res[5].snmp_oid_index == 0
    assert res[5] == 'my newer location'
    assert res[5].snmp_type == 'OCTETSTR'
