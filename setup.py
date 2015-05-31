"""
Introduction
------------

This is a fork of the official `Net-SNMP Python Bindings`_ but attempts to
bring a more Pythonic interface to the library.   Check out the
`Net-SNMP website`_ for more information about SNMP.

This module provides a full featured SNMP client API supporting all dialects
of the SNMP protocol.

.. _Net-SNMP Python Bindings: http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings
.. _Net-SNMP website: http://www.net-snmp.org/

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

Documentation
-------------

Please check out the `Easy SNMP documentation at Read the Docs`_.
This includes install instructions for various operating systems.

.. _Easy SNMP documentation at Read the Docs: http://easysnmp.readthedocs.org/
"""

import os
import re
import sys

from setuptools import setup, Extension
from setuptools.command.test import test as TestCommand

# Determine if a base directory has been provided with the --basedir option
in_tree = False
for arg in sys.argv:
    if arg.startswith('--basedir='):
        basedir = arg.split('=')[1]
        sys.argv.remove(arg)
        in_tree = True

# If a base directory has been provided, we use it
if in_tree:
    netsnmp_libs = os.popen(basedir + '/net-snmp-config --libs').read()

    libdir = os.popen(
        basedir + '/net-snmp-config --build-lib-dirs ' + basedir).read()
    incdir = os.popen(
        basedir + '/net-snmp-config --build-includes ' + basedir).read()

    libs = re.findall(r' -l(\S+)', netsnmp_libs)
    libdirs = re.findall(r' -L(\S+)', libdir)
    incdirs = re.findall(r' -I(\S+)', incdir)

# Otherwise, we use the system-installed SNMP libraries
else:
    netsnmp_libs = os.popen('net-snmp-config --libs').read()

    libs = re.findall(r' -l(\S+)', netsnmp_libs)
    libdirs = re.findall(r' -L(\S+)', netsnmp_libs)
    incdirs = []


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='easysnmp',
    version='0.1.1',
    description='A blazingly fast and Pythonic SNMP library based on the '
                'official Net-SNMP bindings',
    author='Fotis Gimian',
    author_email='fgimiansoftware@gmail.com',
    url='https://github.com/fgimian/easysnmp',
    license='BSD',
    packages=['easysnmp'],
    tests_require=['pytest', 'pytest-cov', 'pytest-flake8'],
    cmdclass={'test': PyTest},
    ext_modules=[
        Extension(
            'easysnmp.interface', ['easysnmp/interface.c'],
            library_dirs=libdirs, include_dirs=incdirs, libraries=libs
        )
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring'
    ]
)
