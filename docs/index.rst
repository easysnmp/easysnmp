Welcome to Easy SNMP
====================
*A blazingly fast and Pythonic SNMP library based on the official
Net-SNMP bindings*

Introduction
------------

This is a fork of the official `Net-SNMP Python Bindings`_ but attempts to
bring a more Pythonic interface to the library.   Check out the
`Net-SNMP website`_ for more information about SNMP.

This module provides a full featured SNMP client API supporting all dialects
of the SNMP protocol.

.. _Net-SNMP Python Bindings: http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings
.. _Net-SNMP website: http://www.net-snmp.org/

Why Another Library?
--------------------

* The `original Net-SNMP Python library`_ is a great starting point but is
  quite un-Pythonic and lacks proper unit tests and documentation.
* `PySNMP`_ is written in pure Python and therefore has a huge performance hit.
  In some brief tests, I estimate that both the Net-SNMP Python bindings and
  Easy SNMP are more than 4 times faster. Further to this, PySNMP has an even
  less Pythonic interface than the official Net-SNMP bindings.
* Many other libraries like `Snimpy`_ are sadly based on PySNMP and so they
  suffer the same performance penalty.

.. _original Net-SNMP Python library: http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings
.. _PySNMP: http://pysnmp.sourceforge.net/
.. _Snimpy: https://snimpy.readthedocs.org/en/latest/

Installation
------------
EasySNMP has been tested and is supported on systems running Net-SNMP
5.7.x and newer. All non-EOL versions of Python 3 are fully supported, with 2.7
and recent EOL versions of Python 3 receiving partial support.

If your OS ships with a supported version of Net-SNMP, then you can install it
without compiling it via your package manager:

On RHEL / CentOS systems:

.. code-block:: bash

    sudo yum install net-snmp-devel

On Debian / Ubuntu systems:

.. code-block:: bash

    sudo apt-get install libsnmp-dev snmp-mibs-downloader

On macOS systems:

.. code-block:: bash

    brew install net-snmp

If your OS doesn't ship with Net-SNMP 5.7.x or newer, please follow instructions
provided on the `Net-SNMP install page <http://www.net-snmp.org/docs/INSTALL.html>`_
to build and install Net-SNMP on your system.

You'll also need to ensure that you have the following packages installed so
that Easy SNMP installs correctly:

On RHEL / CentOS systems:

.. code-block:: bash

    sudo yum install gcc python-devel

On Debian / Ubuntu systems:

.. code-block:: bash

    sudo apt-get install gcc python-dev

On macOS systems:

.. code-block:: bash

    brew install gcc

Install Easy SNMP via pip as follows:

.. code-block:: bash

    pip install easysnmp

Quick Start
-----------
There are primarily two ways you can use the Easy SNMP library.

The first is with the use of a Session object which is most suitable when you
are planning on requesting multiple pieces of SNMP data from a source.

.. code-block:: python

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

You may also use Easy SNMP via its simple interface which is intended for
one-off operations where you wish to specify all details in the request:

.. code-block:: python

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

API
---

.. toctree::
   :maxdepth: 2

   session_api
   easy_api
   exceptions
