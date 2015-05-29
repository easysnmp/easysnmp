from easysnmp.session import build_varlist, build_results


def test_build_varlist():
    varlist, is_list = build_varlist('sysContact.0')
    assert len(varlist) == 1
    assert varlist[0].tag == 'sysContact'
    assert varlist[0].iid == '0'
    assert varlist[0].val is None
    assert varlist[0].type is None
    assert not is_list


def test_build_varlist_list():
    varlist, is_list = build_varlist(['sysContact.0', ('sysDescr', '0')])
    assert len(varlist) == 2
    assert varlist[0].tag == 'sysContact'
    assert varlist[0].iid == '0'
    assert varlist[0].val is None
    assert varlist[0].type is None
    assert varlist[1].tag == 'sysDescr'
    assert varlist[1].iid == '0'
    assert varlist[1].val is None
    assert varlist[1].type is None
    assert is_list
