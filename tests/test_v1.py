import platform

import pytest
import easysnmp

from .fixtures import sess_v1  # noqa


def test_v1_get():
    res = easysnmp.snmp_get(
        'sysDescr.0',
        version=1, hostname='localhost', community='public'
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_v1_get_tuple():
    res = easysnmp.snmp_get(
        ('sysDescr', '0'),
        version=1, hostname='localhost', community='public'
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_v1_get_fully_qualified():
    res = easysnmp.snmp_get(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0',
        version=1, hostname='localhost', community='public'
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_v1_get_fully_qualified_tuple():
    res = easysnmp.snmp_get(
        ('.iso.org.dod.internet.mgmt.mib-2.system.sysDescr', '0'),
        version=1, hostname='localhost', community='public'
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_v1_get_numeric():
    res = easysnmp.snmp_get(
        ('.1.3.6.1.2.1.1.1', '0'),
        version=1, hostname='localhost', community='public'
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_v1_get_unknown():
    with pytest.raises(easysnmp.EasySNMPInterfaceError):
        easysnmp.snmp_get(
            'sysDescripto.0',
            version=1, hostname='localhost', community='public'
        )


def test_v1_get_next():
    res = easysnmp.snmp_get_next(
        'nsCacheEntry', version=1, hostname='localhost', community='public'
    )

    assert res.oid == 'nsCacheTimeout'
    assert res.oid_index == '1.3.6.1.2.1.2.2'
    assert res.value >= 0
    assert res.snmp_type == 'INTEGER'


def test_v1_get_next_numeric():
    res = easysnmp.snmp_get_next(
        ('.1.3.6.1.2.1.1.1', '0'),
        version=1, hostname='localhost', community='public'
    )

    assert res.oid == 'sysObjectID'
    assert res.oid_index == '0'
    assert res.value == '.1.3.6.1.4.1.8072.3.2.10'
    assert res.snmp_type == 'OBJECTID'


def test_v1_set_string():
    res = easysnmp.snmp_get(
        ('sysLocation', '0'),
        version=1, hostname='localhost', community='public'
    )
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value != 'my marginally newer location'
    assert res.snmp_type == 'OCTETSTR'

    success = easysnmp.snmp_set(
        ('sysLocation', '0'), 'my marginally newer location',
        version=1, hostname='localhost', community='public'
    )
    assert success

    res = easysnmp.snmp_get(
        ('sysLocation', '0'),
        version=1, hostname='localhost', community='public'
    )
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value == 'my marginally newer location'
    assert res.snmp_type == 'OCTETSTR'


def test_v1_set_integer():
    success = easysnmp.snmp_set(
        ('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), 65,
        version=1, hostname='localhost', community='public'
    )
    assert success

    res = easysnmp.snmp_get(
        ('nsCacheTimeout', '.1.3.6.1.2.1.2.2'),
        version=1, hostname='localhost', community='public'
    )
    assert res.oid == 'nsCacheTimeout'
    assert res.oid_index == '1.3.6.1.2.1.2.2'
    assert res.value == '65'
    assert res.snmp_type == 'INTEGER'


def test_v1_set_multiple():
    success = easysnmp.snmp_set_multiple({
        'sysLocation.0': 'my marginally newer location',
        ('nsCacheTimeout', '.1.3.6.1.2.1.2.2'): 162
    }, version=1, hostname='localhost', community='public')
    assert success

    res = easysnmp.snmp_get(
        ['sysLocation.0', 'nsCacheTimeout.1.3.6.1.2.1.2.2'],
        version=1, hostname='localhost', community='public'
    )
    assert res[0].value == 'my marginally newer location'
    assert res[1].value == '162'


# TODO: This test needs completion but it seems to break SNMPD in Ubuntu 14.04
# def test_v1_set_restart_agent():
#     var = easysnmp.SNMPVariable('sysUpTime', '0')
#     res = easysnmp.snmp_get(
#         var, version=1, hostname='localhost', community='public'
#     )

#     print "uptime = ", res[0]

#     var = easysnmp.SNMPVariable('versionRestartAgent','0', 1)
#     res = easysnmp.snmp_set(
#         var, version=1, hostname='localhost', community='public'
#     )

#     var = easysnmp.SNMPVariable('sysUpTime','0')
#     res = easysnmp.snmp_get(
#         var, version=1, hostname='localhost', community='public'
#     )

#     print "uptime = ", res[0]


def test_v1_session_set_multiple_next(sess_v1):  # noqa
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

    assert res[0].oid == 'snmpTargetAddrTDomain'
    assert res[0].oid_index == '116.101.115.116'
    assert res[0].value == '.1.3.6.1.6.1.1'
    assert res[0].snmp_type == 'OBJECTID'

    assert res[1].oid == 'snmpTargetAddrTAddress'
    assert res[1].oid_index == '116.101.115.116'
    assert res[1].value == '1234'
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].oid == 'snmpTargetAddrRowStatus'
    assert res[2].oid_index == '116.101.115.116'
    assert res[2].value == '3'
    assert res[2].snmp_type == 'INTEGER'


def test_v1_session_set_clear(sess_v1):  # noqa
    res = sess_v1.set('.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116', 6)
    assert res == 1

    res = sess_v1.get_next([
        'snmpTargetAddrTDomain', 'snmpTargetAddrTAddress',
        'snmpTargetAddrRowStatus'
    ])

    assert len(res) == 3

    assert res[0].oid == 'snmpUnavailableContexts'
    assert res[0].oid_index == '0'
    assert res[0].value == '0'
    assert res[0].snmp_type == 'COUNTER'

    assert res[1].oid == 'snmpUnavailableContexts'
    assert res[1].oid_index == '0'
    assert res[1].value == '0'
    assert res[1].snmp_type == 'COUNTER'

    assert res[2].oid == 'snmpUnavailableContexts'
    assert res[2].oid_index == '0'
    assert res[2].value == '0'
    assert res[2].snmp_type == 'COUNTER'


def test_v1_walk():
    res = easysnmp.snmp_walk(
        'system', version=1, hostname='localhost', community='public'
    )
    assert len(res) >= 7

    assert platform.version() in res[0].value
    assert res[3].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[4].value == platform.node()
    assert res[5].value == 'my marginally newer location'


def test_v1_walk_res():
    res = easysnmp.snmp_walk(
        'system', version=1, hostname='localhost', community='public'
    )

    assert len(res) >= 7

    assert res[0].oid == 'sysDescr'
    assert res[0].oid_index == '0'
    assert platform.version() in res[0].value
    assert res[0].snmp_type == 'OCTETSTR'

    assert res[3].oid == 'sysContact'
    assert res[3].oid_index == '0'
    assert res[3].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[3].snmp_type == 'OCTETSTR'

    assert res[4].oid == 'sysName'
    assert res[4].oid_index == '0'
    assert res[4].value == platform.node()
    assert res[4].snmp_type == 'OCTETSTR'

    assert res[5].oid == 'sysLocation'
    assert res[5].oid_index == '0'
    assert res[5].value == 'my marginally newer location'
    assert res[5].snmp_type == 'OCTETSTR'


def test_v1_session_get(sess_v1):  # noqa
    res = sess_v1.get([
        ('sysUpTime', '0'),
        ('sysContact', '0'),
        ('sysLocation', '0')
    ])

    assert len(res) == 3

    assert res[0].oid == 'sysUpTimeInstance'
    assert res[0].oid_index is ''
    assert res[0].value > 0
    assert res[0].snmp_type == 'TICKS'

    assert res[1].oid == 'sysContact'
    assert res[1].oid_index == '0'
    assert res[1].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].oid == 'sysLocation'
    assert res[2].oid_index == '0'
    assert res[2].value == 'my marginally newer location'
    assert res[2].snmp_type == 'OCTETSTR'


def test_v1_session_get_next(sess_v1):  # noqa
    res = sess_v1.get_next([
        ('sysUpTime', '0'),
        ('sysContact', '0'),
        ('sysLocation', '0')
    ])

    assert len(res) == 3

    assert res[0].oid == 'sysContact'
    assert res[0].oid_index == '0'
    assert res[0].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[0].snmp_type == 'OCTETSTR'

    assert res[1].oid == 'sysName'
    assert res[1].oid_index == '0'
    assert res[1].value == platform.node()
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].oid == 'sysORLastChange'
    assert res[2].oid_index == '0'
    assert res[2].value >= 0
    assert res[2].snmp_type == 'TICKS'


def test_v1_session_get_bulk_unspported(sess_v1):  # noqa
    with pytest.raises(easysnmp.EasySNMPError):
        sess_v1.get_bulk(
            ['sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
             'sysORUpTime'],
            2, 8
        )


def test_v1_session_set(sess_v1):  # noqa
    success = sess_v1.set(('sysLocation', '0'), 'my newer location')
    assert success

    res = easysnmp.snmp_get(
        'sysLocation.0', version=1, hostname='localhost', community='public'
    )
    assert res.value == 'my newer location'


def test_v1_session_set_multiple(sess_v1):  # noqa
    success = sess_v1.set_multiple({
        'sysLocation.0': 'my slightly newer location',
        ('nsCacheTimeout', '.1.3.6.1.2.1.2.2'): '160'
    })
    assert success

    res = easysnmp.snmp_get(
        ['sysLocation.0', 'nsCacheTimeout.1.3.6.1.2.1.2.2'],
        version=1, hostname='localhost', community='public'
    )
    assert res[0].value == 'my slightly newer location'
    assert res[1].value == '160'


def test_v1_session_walk(sess_v1):  # noqa
    res = sess_v1.walk('system')

    assert len(res) >= 7

    assert res[0].oid == 'sysDescr'
    assert res[0].oid_index == '0'
    assert platform.version() in res[0].value
    assert res[0].snmp_type == 'OCTETSTR'

    assert res[3].oid == 'sysContact'
    assert res[3].oid_index == '0'
    assert res[3].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[3].snmp_type == 'OCTETSTR'

    assert res[4].oid == 'sysName'
    assert res[4].oid_index == '0'
    assert res[4].value == platform.node()
    assert res[4].snmp_type == 'OCTETSTR'

    assert res[5].oid == 'sysLocation'
    assert res[5].oid_index == '0'
    assert res[5].value == 'my slightly newer location'
    assert res[5].snmp_type == 'OCTETSTR'
