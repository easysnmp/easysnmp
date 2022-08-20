import sys

PY3 = sys.version_info[0] == 3

if PY3:  # Clear Flake8 warnings
    unicode = None

if PY3:
    text_type = str

    def ub(s):
        return s

    def urepr(s):
        return repr(s)

else:
    text_type = unicode

    def ub(s):
        return s.decode("latin-1")

    def urepr(s):
        if isinstance(s, unicode):
            return repr(s)[1:]
        else:
            return repr(s)
