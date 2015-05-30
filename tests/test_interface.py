import pytest
import easysnmp


def test_invalid_snmp_version():
    with pytest.raises(ValueError):
        easysnmp.Session(version=4)


def test_invalid_hostname():
    with pytest.raises(easysnmp.EasySNMPConnectionError):
        session = easysnmp.Session(hostname='invalid', version=2)
        session.get('sysContact.0')


def test_invalid_port():
    with pytest.raises(easysnmp.EasySNMPTimeoutError):
        session = easysnmp.Session(remote_port=1234, version=2, timeout=0.2,
                                   retries=1)
        session.get('sysContact.0')
