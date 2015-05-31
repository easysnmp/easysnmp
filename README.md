# Easy SNMP #
*A blazingly fast and Pythonic SNMP library based on the official
Net-SNMP bindings*

[![Build Status](https://travis-ci.org/fgimian/easysnmp.svg?branch=master)](https://travis-ci.org/fgimian/easysnmp)
[![Coverage Status](https://coveralls.io/repos/fgimian/easysnmp/badge.svg)](https://coveralls.io/r/fgimian/easysnmp)
[![License](https://img.shields.io/badge/license-BSD-brightgreen.svg)](https://github.com/fgimian/easysnmp/blob/master/LICENSE)

<img src="http://easysnmp.readthedocs.org/en/latest/_static/easysnmp.svg"
     alt="Easy SNMP Logo" height="150px">

Awesome artwork provided courtesy of
[Open Clip Art Library](https://openclipart.org/detail/154453/network)

Easy SNMP is a fork of the official [Net-SNMP Python Bindings](http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings)
but attempts to bring a more Pythonic interface to the library.   Check out
the [Net-SNMP website](http://www.net-snmp.org/) for more information about 
SNMP.

This module provides a full featured SNMP client API supporting all dialects
of the SNMP protocol.

## Quick Start ##

There are primarily two ways you can use the Easy SNMP library.

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

You may also use Easy SNMP via its simple interface which is intended for
one-off operations where you wish to specify all details in the request:

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

## Documentation ##

Please check out the
[Easy SNMP documentation at Read the Docs](http://easysnmp.readthedocs.org/).
This includes install instructions for various operating systems.

You may generate the documentation as follows:

```bash
pip install sphinx
cd docs
make html
```

## Acknowledgments ##

I'd like to say thanks to the following folks who have made this project
possible:

* **Giovanni Marzot**: the original author
* **ScienceLogic, LLC**: sponsored the initial development of this module
* **Wes Hardaker and the net-snmp-coders**: for their hard work and dedication

## License ##

Easy SNMP is released under the BSD license. Please see the
[LICENSE](https://github.com/fgimian/easysnmp/blob/master/LICENSE) file
for more details.

## Copyright ##

The original version of this library is copyright (c) 2006 G. S. Marzot.
All rights reserved.

This program is free software; you can redistribute it and/or modify it under 
the same terms as Net-SNMP itself.

Copyright (c) 2006 SPARTA, Inc.  All Rights Reserved.  This program is free 
software; you can redistribute it and/or modify it under the same terms as
Net-SNMP itself.
