# PyNetSNMP #

This is a fork of the official [Net-SNMP Python Bindings](http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings)
but attempts to bring a more Pythonic interface to the library.   Check out
the [Net-SNMP website](http://www.net-snmp.org/) for more information about 
SNMP.

This module provides a full featured, tri-lingual SNMP (SNMPv3, SNMPv2c,
SNMPv1) client API.

## Quick Start ##

There are primarily two ways you can use the PyNetSNMP library.

The first is with the use of a Session object which is most suitable when you 
are planning on requesting multiple pieces of SNMP data from a source.

```python
from pynetsnmp import Session

# Create an SNMP session to be used for all our requests
session = Session(hostname='localhost', community='public', version=2)

# You may retrieve an individual OID using an SNMP GET
location = session.get('sysLocation.0')

# You may also specify the OID as a tuple (name, index)
contact = session.get(('sysContact', 0))

# Set a variable using an SNMP SET
session.set('sysLocation.0', 'The SNMP Lab')

# Perform an SNMP walk
system_items = session.walk('system')

# Each returned item can be used normally as its related type (str or int) but 
# also has several extended attributes with SNMP-specific information
for item in system_items:
    print '{oid}.{oid_index} {type} = {value}'.format(
        oid=item.snmp_oid,
        oid_index=item.snmp_oid_index,
        type=item.snmp_type,
        value=item
    )
```

You may also use PyNetSNMP via its simple interface which is intended for
one-off operations where you wish to specify all details in the request:

```python
from pynetsnmp import snmp_get, snmp_set, snmp_walk

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

## Installation ##

PyNetSNMP has been tested and is supported on the following operating systems:

* CentOS 6 and CentOS 7
* Debian 7 (Wheezy) and 8 (Jessie)
* Ubuntu Server 12.04 (Precise Pangolin) and 14.04 (Trusty Tahr)

Install PyNetSNMP via pip as follows:

```bash
pip install PyNetSNMP
```

## Documentation ##

Coming soon! :smile:

## Troubleshooting ##

If problems occur there are number areas to look at to narrow down the 
possibilities.

The first step should be to test the Net-SNMP installation independently from 
the Python 'netsnmp' Extension.

1. Try running the apps from the Net-SNMP distribution
2. Make sure your agent (snmpd) is running and properly configured with
   read-write access for the community you are using.
3. Ensure that your MIBs are installed and environment variables are set
   appropriately (see man mib_api)
4. Be sure to ensure headers and libraries from old CMU installations are
   not being used by mistake (see -NET-SNMP-PATH).

If the problem occurs during compilation/linking check that the snmp library 
being linked is actually the Net-SNMP library (there have been name conflicts 
with existing snmp libs).

Also check that the header files are correct and up to date.

If you cannot resolve the problem you can
[post an issue](https://github.com/fgimian/PyNetSNMP/issues).

Please provide sufficient information to analyze the problem (OS type, 
versions for OS, Python, Net-SNMP, compiler, complete error output, etc.).

## Acknowledgments ##

I'd like to say thanks to the following folks who have made this project
possible:

* **Giovanni Marzot**: the original author
* **ScienceLogic, LLC**: sponsored the initial development of this module
* **Wes Hardaker and the net-snmp-coders**: for their hard work and dedication

## License ##

PyNetSNMP is released under the BSD license. Please see the
[LICENSE](https://github.com/fgimian/PyNetSNMP/blob/master/LICENSE) file
for more details.

## Copyright ##

The original version of this library is copyright (c) 2006 G. S. Marzot.
All rights reserved.

This program is free software; you can redistribute it and/or modify it under 
the same terms as Net-SNMP itself.

Copyright (c) 2006 SPARTA, Inc.  All Rights Reserved.  This program is free 
software; you can redistribute it and/or modify it under the same terms as
Net-SNMP itself.
