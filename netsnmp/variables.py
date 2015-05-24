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

        # Parse iid out of tag if needed
        if iid is None and tag is not None:
            regex = re.compile(r'^((?:\.\d+)+|(?:\w+(?:[-:]*\w+)+))\.?(.*)$')
            match = regex.match(tag)
            if match:
                self.tag, self.iid = match.group(1, 2)

    def __setattr__(self, name, val):
        self.__dict__[name] = tostr(val)


class VarList(object):
    def __init__(self, *vs):
        self.varbinds = []

        for var in vs:
            if isinstance(var, Varbind):
                self.varbinds.append(var)
            else:
                self.varbinds.append(Varbind(var))

    def __len__(self):
        return len(self.varbinds)

    def __getitem__(self, index):
        return self.varbinds[index]

    def __setitem__(self, index, val):
        if isinstance(val, Varbind):
            self.varbinds[index] = val
        else:
            raise TypeError

    def __iter__(self):
        return iter(self.varbinds)

    def __delitem__(self, index):
        del self.varbinds[index]

    def __repr__(self):
        return repr(self.varbinds)

    def __getslice__(self, i, j):
        return self.varbinds[i:j]

    def append(self, *vars):
        for var in vars:
            if isinstance(var, Varbind):
                self.varbinds.append(var)
            else:
                raise TypeError
