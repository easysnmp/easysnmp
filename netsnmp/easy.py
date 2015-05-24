from .variables import Varbind, VarList
from .session import Session


def snmp_get(*args, **kargs):
    sess = Session(**kargs)
    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))
    res = sess.get(var_list)
    return res


def snmp_set(*args, **kargs):
    sess = Session(**kargs)
    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))
    res = sess.set(var_list)
    return res


def snmp_get_next(*args, **kargs):
    sess = Session(**kargs)
    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))
    res = sess.get_next(var_list)
    return res


def snmp_get_bulk(non_repeaters, max_repetitions, *args, **kargs):
    sess = Session(**kargs)
    var_list = VarList()
    for arg in args:
        if isinstance(arg, Varbind):
            var_list.append(arg)
        else:
            var_list.append(Varbind(arg))
    res = sess.get_bulk(non_repeaters, max_repetitions, var_list)
    return res


def snmp_walk(*args, **kargs):
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
