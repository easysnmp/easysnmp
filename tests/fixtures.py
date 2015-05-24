import netsnmp

import pytest


@pytest.fixture
def sess_v1():
    sess = netsnmp.Session(Version=1,
                           DestHost='localhost',
                           Community='public')
    return sess


@pytest.fixture
def sess_v2():
    sess = netsnmp.Session(Version=2,
                           DestHost='localhost',
                           Community='public')
    sess.UseEnums = 1
    sess.UseLongNames = 1
    return sess


@pytest.fixture
def sess_v3():
    sess = netsnmp.Session(Version=3,
                           DestHost='localhost',
                           SecLevel='authPriv',
                           SecName='initial',
                           PrivPass='priv_pass',
                           AuthPass='auth_pass')
    sess.UseSprintValue = 1
    return sess
