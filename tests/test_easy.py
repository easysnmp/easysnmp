import platform

import pytest
from easysnmp.easy import (
    snmp_get, snmp_set, snmp_set_multiple, snmp_get_next, snmp_get_bulk,
    snmp_walk
)
from easysnmp.exceptions import (
    EasySNMPError, EasySNMPUnknownObjectIDError, EasySNMPNoSuchObjectError,
    EasySNMPNoSuchInstanceError
)

from .fixtures import sess_v1_args, sess_v2_args, sess_v3_args
from .helpers import snmp_set_via_cli


@pytest.yield_fixture(autouse=True)
def reset_values():
    snmp_set_via_cli('sysLocation.0', 'my original location', 's')
    snmp_set_via_cli('nsCacheTimeout.1.3.6.1.2.1.2.2', '0', 'i')
    yield


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_regular(sess_args):
    res = snmp_get('sysDescr.0', **sess_args)

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_tuple(sess_args):
    res = snmp_get(('sysDescr', '0'), **sess_args)

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_fully_qualified(sess_args):
    res = snmp_get(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0', **sess_args
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_fully_qualified_tuple(sess_args):
    res = snmp_get(
        ('.iso.org.dod.internet.mgmt.mib-2.system.sysDescr', '0'), **sess_args
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_numeric(sess_args):
    res = snmp_get(('.1.3.6.1.2.1.1.1', '0'), **sess_args)

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_unknown(sess_args):
    with pytest.raises(EasySNMPUnknownObjectIDError):
        snmp_get('sysDescripto.0', **sess_args)


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_invalid_instance(sess_args):
    # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
    # invalid object ID, so it raises the same exception for both
    if sess_args['version'] == 1:
        with pytest.raises(EasySNMPNoSuchObjectError):
            snmp_get('sysContact.1', **sess_args)
    else:
        with pytest.raises(EasySNMPNoSuchInstanceError):
            snmp_get('sysContact.1', **sess_args)


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_invalid_object(sess_args):
    with pytest.raises(EasySNMPNoSuchObjectError):
        snmp_get('iso', **sess_args)


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_next(sess_args):
    res = snmp_get_next('nsCacheEntry', **sess_args)

    assert res.oid == 'nsCacheTimeout'
    assert res.oid_index == '1.3.6.1.2.1.2.2'
    assert int(res.value) >= 0
    assert res.snmp_type == 'INTEGER'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_next_numeric(sess_args):
    res = snmp_get_next(('.1.3.6.1.2.1.1.1', '0'), **sess_args)

    assert res.oid == 'sysObjectID'
    assert res.oid_index == '0'
    assert res.value == '.1.3.6.1.4.1.8072.3.2.10'
    assert res.snmp_type == 'OBJECTID'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_next_unknown(sess_args):
    with pytest.raises(EasySNMPUnknownObjectIDError):
        snmp_get_next('sysDescripto.0', **sess_args)


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_set_string(sess_args):
    res = snmp_get(('sysLocation', '0'), **sess_args)
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value != 'my newer location'
    assert res.snmp_type == 'OCTETSTR'

    success = snmp_set(
        ('sysLocation', '0'), 'my newer location', **sess_args
    )
    assert success

    res = snmp_get(('sysLocation', '0'), **sess_args)
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value == 'my newer location'
    assert res.snmp_type == 'OCTETSTR'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_set_integer(sess_args):
    success = snmp_set(
        ('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), 65, **sess_args
    )
    assert success

    res = snmp_get(
        ('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), **sess_args
    )
    assert res.oid == 'nsCacheTimeout'
    assert res.oid_index == '1.3.6.1.2.1.2.2'
    assert res.value == '65'
    assert res.snmp_type == 'INTEGER'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_set_unknown(sess_args):
    with pytest.raises(EasySNMPUnknownObjectIDError):
        snmp_set('nsCacheTimeoooout', 1234, **sess_args)


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_set_multiple(sess_args):
    res = snmp_get(
        ['sysLocation.0', 'nsCacheTimeout.1.3.6.1.2.1.2.2'], **sess_args
    )
    assert res[0].value != 'my newer location'
    assert res[1].value != '162'

    success = snmp_set_multiple([
        ('sysLocation.0', 'my newer location'),
        (('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), 162)
    ], **sess_args)
    assert success

    res = snmp_get(
        ['sysLocation.0', 'nsCacheTimeout.1.3.6.1.2.1.2.2'], **sess_args
    )
    assert res[0].value == 'my newer location'
    assert res[1].value == '162'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_get_bulk(sess_args):
    if sess_args['version'] == 1:
        with pytest.raises(EasySNMPError):
            snmp_get_bulk([
                'sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
                'sysORUpTime'], 2, 8, **sess_args
            )
    else:
        res = snmp_get_bulk([
            'sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
            'sysORUpTime'], 2, 8, **sess_args
        )

        assert len(res) == 26

        assert res[0].oid == 'sysUpTimeInstance'
        assert res[0].oid_index is ''
        assert int(res[0].value) > 0
        assert res[0].snmp_type == 'TICKS'

        assert res[4].oid == 'sysORUpTime'
        assert res[4].oid_index == '1'
        assert int(res[4].value) >= 0
        assert res[4].snmp_type == 'TICKS'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_walk(sess_args):
    res = snmp_walk('system', **sess_args)
    assert len(res) >= 7

    assert platform.version() in res[0].value
    assert res[3].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[4].value == platform.node()
    assert res[5].value == 'my original location'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_walk_res(sess_args):
    res = snmp_walk('system', **sess_args)

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
    assert res[5].value == 'my original location'
    assert res[5].snmp_type == 'OCTETSTR'


@pytest.mark.parametrize(
    'sess_args', [sess_v1_args(), sess_v2_args(), sess_v3_args()]
)
def test_snmp_walk_unknown(sess_args):
    with pytest.raises(EasySNMPUnknownObjectIDError):
        snmp_walk('systemo', **sess_args)
