import pynetsnmp

import pytest


@pytest.fixture
def sess_v1():
    return pynetsnmp.Session(
        version=1, hostname='localhost', community='public'
    )


@pytest.fixture
def sess_v2():
    return pynetsnmp.Session(
        version=2, hostname='localhost', community='public'
    )


@pytest.fixture
def sess_v3():
    return pynetsnmp.Session(
        version=3, hostname='localhost',
        security_level='authPriv', security_username='initial',
        privacy_password='priv_pass', auth_password='auth_pass'
    )
