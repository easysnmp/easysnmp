Easy SNMP
=========

|Python Code Style| |Build Status| |Discussions| |License|

.. |Python Code Style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
.. |Build Status| image:: https://img.shields.io/github/workflow/status/easysnmp/easysnmp/build
   :target: https://github.com/easysnmp/easysnmp/actions
.. |License| image:: https://img.shields.io/badge/license-BSD-blue.svg
   :target: https://github.com/kamakazikamikaze/easysnmp/blob/master/LICENSE
.. |Discussions| image:: https://img.shields.io/github/discussions/easysnmp/easysnmp
   :alt: Join the Discussions!
   :target: https://github.com/easysnmp/easysnmp

.. image:: https://raw.githubusercontent.com/easysnmp/easysnmp/master/images/easysnmp-logo.png
    :alt: Easy SNMP Logo

Artwork courtesy of `Open Clip Art
Library <https://openclipart.org/detail/154453/network>`_


Introduction
------------

Easy SNMP is a fork of `Net-SNMP Python
Bindings <http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings>`_
that attempts to bring a more Pythonic interface to the library. Check
out the `Net-SNMP website <http://www.net-snmp.org/>`_ for more
information about SNMP.

This module provides a full-featured SNMP client API and supports all
dialects of the SNMP protocol.

Why Another Library?
--------------------

- The `original Net-SNMP Python
  library <http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings>`_
  is a great starting point but is quite un-Pythonic and lacks proper unit tests and documentation.
- `PySNMP <http://pysnmp.sourceforge.net/>`_ is entirely written in Python
  and therefore has a huge performance hit. In some brief tests, I
  estimate that both the Net-SNMP Python bindings and Easy SNMP are more than 4 times faster than PySNMP. Further to this, PySNMP has an even less Pythonic interface than the official Net-SNMP bindings.
- Many other libraries like `Snimpy <https://snimpy.readthedocs.org/en/latest/>`_ are sadly based on PySNMP, so they also suffer performance penalty.

Quick Start
-----------

There are primarily two ways you can use the Easy SNMP library:

1. By using a Session object which is most suitable
when you want to request multiple pieces of SNMP data from a
source:

.. code:: python

    from easysnmp import Session

    # Create an SNMP session to be used for all our requests
    session = Session(hostname='localhost', community='public', version=2)

    # You may retrieve an individual OID using an SNMP GET
    location = session.get('sysLocation.0')

    # You may also specify the OID as a tuple (name, index)
    # Note: the index is specified as a string as it can be of other types than
    # just a regular integer
    contact = session.get(('sysContact', '0'))

    # And of course, you may use the numeric OID too
    description = session.get('.1.3.6.1.2.1.1.1.0')

    # Set a variable using an SNMP SET
    session.set('sysLocation.0', 'The SNMP Lab')

    # Perform an SNMP walk
    system_items = session.walk('system')

    # Each returned item can be used normally as its related type (str or int)
    # but also has several extended attributes with SNMP-specific information
    for item in system_items:
        print '{oid}.{oid_index} {snmp_type} = {value}'.format(
            oid=item.oid,
            oid_index=item.oid_index,
            snmp_type=item.snmp_type,
            value=item.value
        )

2. By using Easy SNMP via its simple interface which is intended
for one-off operations (where you wish to specify all details in the
request):

.. code:: python

    from easysnmp import snmp_get, snmp_set, snmp_walk

    # Grab a single piece of information using an SNMP GET
    snmp_get('sysDescr.0', hostname='localhost', community='public', version=1)

    # Perform an SNMP SET to update data
    snmp_set(
        'sysLocation.0', 'My Cool Place',
        hostname='localhost', community='public', version=1
    )

    # Perform an SNMP walk
    snmp_walk('system', hostname='localhost', community='public', version=1)

Documentation
-------------

Please check out the `Easy SNMP documentation at Read the
Docs <http://easysnmp.readthedocs.org/>`_. This includes installation
instructions for various operating systems.

You may generate the documentation as follows:

.. code:: bash

    # Install Sphinx
    pip install sphinx

    # You may optionally export the READTHEDOCS environment variable to build docs
    # on systems where you haven't built the C interface
    export READTHEDOCS=1

    # Build the documentation into static HTML pages
    cd docs
    make html

Acknowledgments
---------------

I'd like to say thanks to the following folks who have made this project
possible:

-  **Giovanni Marzot**: the original author
-  **ScienceLogic, LLC**: sponsored the initial development of this
   module
-  **Wes Hardaker and the net-snmp-coders**: for their hard work and
   dedication
- **fgimian and nnathan**: the original contributors to this codebase

Running Tests
-------------

Tests use `Pytest <https://github.com/pytest-dev/pytest>`_. You can run
them with the following:

.. code:: bash

    git clone https://github.com/easysnmp/easysnmp.git
    cd easysnmp
    pip install pytest
    pytest

License
-------

Easy SNMP is released under the **BSD** license. Please see the
`LICENSE <https://github.com/easysnmp/easysnmp/blob/master/LICENSE>`_
file for more details.

Copyright
---------

The original version of this library is copyright (c) 2006 G. S. Marzot.
All rights reserved.

This program is free software; you can redistribute it and/or modify it
under the same terms as Net-SNMP itself.

Copyright (c) 2006 SPARTA, Inc. All Rights Reserved. This program is
free software; you can redistribute it and/or modify it under the same
terms as Net-SNMP itself.
