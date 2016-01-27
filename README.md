# EzSNMP #
*A fork of the blazingly fast easysnmp*

EzSNMP is a fork of easysnmp, which is a python extension written in Clang and is geared towards solving issues with easysnmp and adding more features as needed.
It is based on [Net-SNMP Python Bindings](http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings)
Learn more from the [Net-SNMP website](http://www.net-snmp.org/).
Learn more about [easysnmp](https://github.com/fgimian/easysnmp) and [Easy SNMP documentation at Read the Docs](http://easysnmp.readthedocs.org/).

## Quick Start ##

There are primarily two ways you can use the EzSNMP library.

The first is with the use of a Session object which is most suitable when you 
are planning on requesting multiple pieces of SNMP data from a source.

```python
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
```

For one-off operations where you wish to specify all details in the request:

```python
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
```

## Testing ##

You will need to install snmp, snmpd, snmp-mibs-downloader.

Use the provided snmpd.conf in the test folder and start snmpd.

Run `python setup.py test`.

Make sure snmpd is running with that config or you will encounter errors during testing.

## Documentation ##

You may generate documentation as follows:

```bash
# Install Sphinx
pip install sphinx

# You may optionally export the READTHEDOCS environment variable to build docs
# on systems where you haven't built the C interface
export READTHEDOCS=1

# Build the documentation into static HTML pages
cd docs
make html
```

## License ##

EzSNMP is released under the BSD license.

## Copyright ##

The original version of this library is copyright (c) 2006 G. S. Marzot.
All rights reserved.

This program is free software; you can redistribute it and/or modify it under 
the same terms as Net-SNMP itself.

Copyright (c) 2006 SPARTA, Inc.  All Rights Reserved.  This program is free 
software; you can redistribute it and/or modify it under the same terms as
Net-SNMP itself.
