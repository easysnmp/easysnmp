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

Installation
------------
Easy SNMP has been tested and is supported on the following operating systems:

* CentOS 6 and CentOS 7
* Debian 7 (Wheezy) and 8 (Jessie)
* Ubuntu Server 12.04 (Precise Pangolin) and 14.04 (Trusty Tahr)

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

    # Each returned item can be used normally as its related type (str or int) but
    # also has several extended attributes with SNMP-specific information
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