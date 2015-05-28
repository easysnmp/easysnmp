import platform

import pytest
import easysnmp

from .fixtures import sess_v2  # noqa


def test_easysnmp_v2_get_invalid_instance():
    with pytest.raises(easysnmp.EasySNMPNoSuchInstanceError):
        easysnmp.snmp_get(
            'sysContact.1',
            version=2, hostname='localhost', community='public'
        )


def test_easysnmp_v2_get_invalid_object():
    with pytest.raises(easysnmp.EasySNMPNoSuchObjectError):
        easysnmp.snmp_get(
            'iso',
            version=2, hostname='localhost', community='public'
        )


def test_easysnmp_v2_get_bulk():
    res = easysnmp.snmp_get_bulk([
        'sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
        'sysORUpTime'], 2, 8,
        version=2, hostname='localhost', community='public'
    )

    assert len(res) == 26

    assert res[0].oid == 'sysUpTimeInstance'
    assert res[0].oid_index is ''
    assert res[0].value > 0
    assert res[0].snmp_type == 'TICKS'

    assert res[4].oid == 'sysORUpTime'
    assert res[4].oid_index == '1'
    assert res[4].value >= 0
    assert res[4].snmp_type == 'TICKS'


def test_easysnmp_v2_session_get(sess_v2):  # noqa
    res = sess_v2.get([
        ('sysUpTime', '0'),
        ('sysContact', '0'),
        ('sysLocation', '0')
    ])

    assert len(res) == 3

    assert res[0].oid == 'sysUpTimeInstance'
    assert res[0].oid_index == ''
    assert res[0].value > 0
    assert res[0].snmp_type == 'TICKS'

    assert res[1].oid == 'sysContact'
    assert res[1].oid_index == '0'
    assert res[1].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].oid == 'sysLocation'
    assert res[2].oid_index == '0'
    assert res[2].value == 'my slightly newer location'
    assert res[2].snmp_type == 'OCTETSTR'


def test_easysnmp_v2_session_get_next(sess_v2):  # noqa
    res = sess_v2.get_next([
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


def test_easysnmp_v2_session_get_bulk(sess_v2):  # noqa
    res = sess_v2.get_bulk([
        'sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
        'sysORUpTime'], 2, 8
    )

    assert len(res) == 26

    assert res[0].oid == 'sysUpTimeInstance'
    assert res[0].oid_index is ''
    assert res[0].value > 0
    assert res[0].snmp_type == 'TICKS'

    assert res[4].oid == 'sysORUpTime'
    assert res[4].oid_index == '1'
    assert res[4].value >= 0
    assert res[4].snmp_type == 'TICKS'


def test_easysnmp_v2_session_set(sess_v2):  # noqa
    success = sess_v2.set(('sysLocation', '0'), 'my even newer location')
    assert success

    res = easysnmp.snmp_get(
        ('sysLocation', '0'),
        version=2, hostname='localhost', community='public'
    )
    assert res.value == 'my even newer location'


def test_easysnmp_v2_session_walk(sess_v2):  # noqa
    res = sess_v2.walk('system')

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
    assert res[5].value >= 'my even newer location'
    assert res[5].snmp_type == 'OCTETSTR'
