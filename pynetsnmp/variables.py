import re


def tostr(s):
    """Converts any variable to a string"""
    return None if s is None else str(s)


class Varbind(object):
    def __init__(self, tag=None, iid=None, val=None, type=None):
        self.tag = tostr(tag)
        self.iid = tostr(iid)
        self.val = tostr(val)
        self.type = tostr(type)

        # Parse index id out of tag if needed
        if iid is None and tag is not None:
            regex = re.compile(r'^((?:\.\d+)+|(?:\w+(?:[-:]*\w+)+))\.?(.*)$')
            match = regex.match(tag)
            if match:
                self.tag, self.iid = match.group(1, 2)

    def __setattr__(self, name, val):
        self.__dict__[name] = tostr(val)


class VarList(list):
    """An slight variation of a list which is used internally by the
    Net-SNMP C interface"""
    def __init__(self, *items):
        self.extend(items)

    @property
    def varbinds(self):
        return self
