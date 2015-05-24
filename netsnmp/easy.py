from .variables import Varbind, VarList
from .session import Session


def snmpget(*args, **kargs):
    sess = Session(**kargs)
    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))
    res = sess.get(var_list)
    return res


def snmpset(*args, **kargs):
    sess = Session(**kargs)
    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))
    res = sess.set(var_list)
    return res


def snmpgetnext(*args, **kargs):
    sess = Session(**kargs)
    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))
    res = sess.getnext(var_list)
    return res


def snmpgetbulk(nonrepeaters, maxrepetitions, *args, **kargs):
    sess = Session(**kargs)
    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))
    res = sess.getbulk(nonrepeaters, maxrepetitions, var_list)
    return res


def snmpwalk(*args, **kargs):
    sess = Session(**kargs)
    if isinstance(args[0], VarList):
        var_list = args[0]
    else:
        var_list = VarList()
        for arg in args:
            if isinstance(arg, Varbind):
                var_list.append(arg)
            else:
                var_list.append(Varbind(arg))
    res = sess.walk(var_list)
    return res
