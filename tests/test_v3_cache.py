from __future__ import unicode_literals

import pytest
from easysnmp import Session
from easysnmp.exceptions import EasySNMPConnectionError


def test_v3_not_caching_user(sess_v3):
    s = Session(**sess_v3)
    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    s.update_session(privacy_password="wrong_pass")

    with pytest.raises(EasySNMPConnectionError):
        res = s.get("sysDescr.0")

    d = dict(**sess_v3)
    d["privacy_password"] = "wrong_pass"
    s = Session(**d)
    with pytest.raises(EasySNMPConnectionError):
        res = s.get("sysDescr.0")

    s.update_session(privacy_password="priv_pass")
    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
