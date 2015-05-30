import pytest
import easysnmp


def test_invalid_snmp_version():
    with pytest.raises(easysnmp.EasySNMPError):
        easysnmp.Session(version=4)


def test_unable_to_open_session():
    with pytest.raises(easysnmp.EasySNMPError):
        session = easysnmp.Session(hostname='invalid', version=2)
        session.get('sysContact.0')
