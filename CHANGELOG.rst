Changelog
---------

`Unreleased <https://github.com/fgimian/easysnmp/tree/HEAD>`_
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Allow ``snmp_type`` parameter in ``set(...)`` to support snmpset(1)
  type specifiers.
  (`#28 <https://github.com/fgimian/easysnmp/issues/28>`_,
  `PR#29 <https://github.com/fgimian/easysnmp/pull/29>`_)
- Support Net-SNMP 5.6.x to add support for OSX.
  (`#12 <https://github.com/fgimian/easysnmp/issues/12>`_,
  `4e121e9 <https://github.com/fgimian/easysnmp/commit/4e121e9f9b4613485bcb8f9bab48b4528a223db3>`_)
- Remove printf debug statements when making SNMPv1 fixes from interface.c.
  (`320df28 <https://github.com/fgimian/easysnmp/commit/320df2882bbc5e3f57a7e71164497b063baa855e>`_)

`Full Changelog <https://github.com/fgimian/easysnmp/compare/0.2.4...HEAD>`_

`0.2.4 <https://github.com/fgimian/easysnmp/tree/0.2.4>`_ (2015-07-09)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Ensured that the simple bitarray header is correctly referenced.

`Full Changelog <https://github.com/fgimian/easysnmp/compare/0.2.3...0.2.4>`_

`0.2.3 <https://github.com/fgimian/easysnmp/tree/0.2.3>`_ (2015-06-30)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Introduce this changelog.
- Removed dead Python 2.5.x code.
  (`PR#22 <https://github.com/fgimian/easysnmp/pull/22>`_)
- Fix SNMPv1 when using ``retry_no_such=True`` to ensure the response
  values return correctly to the corresponding supplied requested OIDs.
  (`PR#18 <https://github.com/fgimian/easysnmp/pull/18>`_)
- Allow OIDs to be specified without a leading dot.
  (`#15 <https://github.com/fgimian/easysnmp/issues/15>`_)
- By default do not throw exception if a non-existent OID is fetched,
  and introduce ``abort_on_nonexistent`` to allow user-configurable
  action.
  (`49ea15ec <https://github.com/fgimian/easysnmp/commit/49ea15ec32cd29cd2469041d0a6bab499dd7b599>`_)
- Fix C interface to not tread on existing logging configuration to
  instead import logging module and configure a NullHandler instead.
  (`PR#13 <https://github.com/fgimian/easysnmp/pull/13>`_)
- Modify ``snmpd`` to run on ``localhost:11161`` to avoid requiring
  root privilege and not clash with a local running instance of snmpd.
  (`5604a4bb <https://github.com/fgimian/easysnmp/commit/5604a4bbe72844295e966af270469aeccad19e98>`_)

`Full Changelog <https://github.com/fgimian/easysnmp/compare/0.2.2...0.2.3>`_

`0.2.2 <https://github.com/fgimian/easysnmp/tree/0.2.2>`_ (2015-06-03)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Cosmetic fixes to the codebase.
- Fixes for Python 3.x/unicode support.

`Full Changelog <https://github.com/fgimian/easysnmp/compare/0.2.1...0.2.2>`_

`0.2.1 <https://github.com/fgimian/easysnmp/tree/0.2.1>`_ (2015-06-02)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Various fixes to the C interface including better exception handling
  and removal of remnant debug code.
- Use pytest-sugar for bling-bling test output.
  (`71c567f9 <https://github.com/fgimian/easysnmp/commit/71c567f9ae0cabe8eee970ed0b102956b8c73565>`_)

`Full Changelog <https://github.com/fgimian/easysnmp/compare/0.2...0.2.1>`_

`0.2 <https://github.com/fgimian/easysnmp/tree/0.2>`_ (2015-06-02)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Introduced support for Python 3.x.

`Full Changelog <https://github.com/fgimian/easysnmp/compare/0.1.1...0.2>`_

`0.1.1 <https://github.com/fgimian/easysnmp/tree/0.1.1>`_ (2015-06-02)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Added PyPI documentation.
  (`da16cd74 <https://github.com/fgimian/easysnmp/commit/da16cd749bff13863fe6ea61d221f08f389ddca0>`_)
- Quelch stderr messages generated from the internal Net-SNMP library.
  (`15fce1ea <https://github.com/fgimian/easysnmp/commit/15fce1ea7adcee4dc86d1a42271f123e749a0241>`_)
- Improved coverage of testsuite.
- Use of fixtures and parametization in testsuite to target specific
  versions of SNMP (v1/v2/v3).
  (`427a9dfd <https://github.com/fgimian/easysnmp/commit/427a9dfd4740ce22f2af6bee617fe7a78a7bbcae>`_)

`Full Changelog <https://github.com/fgimian/easysnmp/compare/0.1...0.1.1>`_

`0.1 <https://github.com/fgimian/easysnmp/tree/0.1>`_ (2015-05-30)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Raise Python exceptions in the C interface where necessary.
- Bug fixes to the C interface when specifying context engine session
  ID and the value returned when requesting an invalid OID.
  (`PR#6 <https://github.com/fgimian/easysnmp/pull/6>`_)
- Implement python logging in the C interface and rewrite existing
  fprintf diagnostics to use the logging interface.
  (`PR#4 <https://github.com/fgimian/easysnmp/pull/4>`_)
- Unit tests rewritten in pytest and travis-ci integration.
  (`PR#2 <https://github.com/fgimian/easysnmp/pull/2>`_,
  `b2018587 <https://github.com/fgimian/easysnmp/commit/b20185875feae252b7f912f693156fca1d88b3d0>`_)
- Implement ``compat_netsnmp_memdup()`` to fix C interface to compile
  against Net-SNMP 5.7.2. ([PR#2])
- Import and overhaul of the original Net-SNMP Python bindings:
    - Wrote a README that provides an overview and quickstart of the
      project
    - Sphinx generated documentation which is also hosted on
      readthedocs.
    - Conform to PEP8 using ``flake8``
    - Coverage support via coveralls.io (integrated into travis)
    - A simple pythonic interface which resembles the use of the
      Net-SNMP CLI client utilities.
    - Python package uploaded to PyPI

`Full Changelog <https://github.com/fgimian/easysnmp/compare/6c0f8c32709fc240f57934ed50e31bf05af04e20...0.1>`_
