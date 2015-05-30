import pytest
import easysnmp


def test_invalid_snmp_version():
    with pytest.raises(ValueError):
        easysnmp.Session(version=4)


@pytest.mark.parametrize('version', [1, 2, 3])
def test_invalid_hostname(version):
    with pytest.raises(easysnmp.EasySNMPConnectionError):
        session = easysnmp.Session(hostname='invalid', version=version)
        session.get('sysContact.0')


@pytest.mark.parametrize('version', [1, 2, 3])
def test_invalid_port(version):
    with pytest.raises(easysnmp.EasySNMPTimeoutError):
        session = easysnmp.Session(
            remote_port=1234, version=version, timeout=0.2, retries=1
        )
        session.get('sysContact.0')
