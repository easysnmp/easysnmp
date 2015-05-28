from easysnmp.data_types import (
    SNMPBaseIntegerType, SNMPBaseStringType,
    SNMPBits, SNMPObjectIdentifier, SNMPOctetString, SNMPInteger,
    SNMPNetworkAddress, SNMPIPAddress, SNMPCounter, SNMPGauge, SNMPTimeTicks,
    SNMPOpaque, SNMPCounter64, SNMPUnsigned32, SNMPInteger32
)


def test_easysnmp_base_integer_type():
    var = SNMPBaseIntegerType('12345', 'nsCacheTimeout', '0')
    assert var.value == 12345
    assert var.oid == 'nsCacheTimeout'
    assert var.oid_index == '0'


def test_easysnmp_base_integer_type_repr():
    var = SNMPBaseIntegerType('12345', 'nsCacheTimeout', '0')
    assert var.__repr__() == (
        "<SNMPBaseIntegerType value=12345 "
        "(oid='nsCacheTimeout', oid_index='0')>"
    )


def test_easysnmp_base_integer_type():
    var = SNMPBaseIntegerType('12345', 'nsCacheTimeout', '0')
    assert var.value == 12345
    assert var.oid == 'nsCacheTimeout'
    assert var.oid_index == '0'


def test_easysnmp_base_string_type():
    var = SNMPBaseStringType('my thingo', 'sysDescr', '0')
    assert var.value == 'my thingo'
    assert var.oid == 'sysDescr'
    assert var.oid_index == '0'


def test_easysnmp_base_string_type_repr():
    var = SNMPBaseStringType('my thingo', 'sysDescr', '0')
    assert var.__repr__() == (
        "<SNMPBaseStringType value='my thingo' "
        "(oid='sysDescr', oid_index='0')>"
    )


def test_easysnmp_base_string_type_repr_binary():
    var = SNMPBaseStringType(
        chr(20) + 'my thingo' + chr(155),
        'sysDescr', '0'
    )
    assert var.__repr__() == (
        "<SNMPBaseStringType value='my thingo (contains binary)' "
        "(oid='sysDescr', oid_index='0')>"
    )


def test_easysnmp_base_string_type_repr_binary_only():
    var = SNMPBaseStringType(
        chr(20) + chr(155),
        'sysDescr', '0'
    )
    assert var.__repr__() == (
        "<SNMPBaseStringType value='(contains binary)' "
        "(oid='sysDescr', oid_index='0')>"
    )
