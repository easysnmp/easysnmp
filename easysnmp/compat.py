import sys

PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str

    def ub(s):
        return s
else:
    text_type = unicode  # noqa

    def ub(s):
        return s.decode('latin-1')
