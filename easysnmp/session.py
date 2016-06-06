from __future__ import unicode_literals

import os
import re

# Don't attempt to import the C interface if building docs on RTD
if not os.environ.get('READTHEDOCS', False):  # noqa
    from . import interface

from .exceptions import (
    EasySNMPError, EasySNMPNoSuchObjectError, EasySNMPNoSuchInstanceError
)
from .variables import SNMPVariable, SNMPVariableList

# Mapping between security level strings and their associated integer values.
# Here we provide camelCase naming as per the original spec but also more
# Pythonic variations for those who wish to use them.
SECURITY_LEVEL_MAPPING = {
    'noAuthNoPriv': 1,
    'authNoPriv': 2,
    'authPriv': 3,
    'no_auth_or_privacy': 1,
    'auth_without_privacy': 2,
    'auth_with_privacy': 3
}


def build_varlist(oids):
    """
    Prepare the variable binding list which will be used by the
    C interface.

    :param oids: an individual or list of strings or tuples representing
                 one or more OIDs
    :return: a tuple containing where the first item is a list of SNMPVariable
             objects or an individual SNMPVariable and a boolean indicating
             whether or not the first tuple item is a list or single item
    """

    if isinstance(oids, list):
        is_list = True
    else:
        is_list = False
        oids = [oids]

    varlist = SNMPVariableList()
    for oid in oids:
        # OIDs specified as a tuple (e.g. ('sysContact', 0))
        if isinstance(oid, tuple):
            oid, oid_index = oid
            varlist.append(SNMPVariable(oid, oid_index))
        # OID . is specified (which we convert to iso)
        elif oid == '.':
            varlist.append(SNMPVariable('iso'))
        # OIDs specefied as a string (e.g. 'sysContact.0')
        else:
            varlist.append(SNMPVariable(oid))

    return varlist, is_list


def validate_results(varlist):
    """
    Validates a list of SNMPVariable objects and raises any appropriate
    exceptions where necessary.

    :param varlist: a variable list containing SNMPVariable objects to be
                    processed
    """

    for variable in varlist:
        # Create a printable variable string for the error
        varstr = variable.oid
        if variable.oid_index:
            varstr += ' with index {0}'.format(variable.oid_index)

        if variable.snmp_type == 'NOSUCHOBJECT':
            raise EasySNMPNoSuchObjectError(
                'no such object {0} could be found'.format(varstr)
            )
        if variable.snmp_type == 'NOSUCHINSTANCE':
            raise EasySNMPNoSuchInstanceError(
                'no such instance {0} could be found'.format(varstr)
            )


class Session(object):
    """
    A Net-SNMP session which may be setup once and then used to query and
    manipulate SNMP data.

    :param hostname: hostname or IP address of SNMP agent
    :param version: the SNMP version to use; 1, 2 (equivalent to 2c) or 3
    :param community: SNMP community string (used for both R/W) (v1 & v2)
    :param timeout: seconds before retry
    :param retries: retries before failure
    :param remote_port: allow remote UDP port to be overridden (this will
                        communicate on port 161 at its default setting)
    :param local_port: allow overriding of the local SNMP port
    :param security_level: security level (no_auth_or_privacy,
                           auth_without_privacy or auth_with_privacy) (v3)
    :param security_username: security name (v3)
    :param privacy_protocol: privacy protocol (v3)
    :param privacy_password: privacy passphrase (v3)
    :param auth_protocol: authentication protocol (MD5 or SHA) (v3)
    :param auth_password: authentication passphrase (v3)
    :param context_engine_id: context engine ID, will be probed if not
                              supplied (v3)
    :param security_engine_id: security engine ID, will be probed if not
                               supplied (v3)
    :param context: context name (v3)
    :param engine_boots: the number of times the SNMP engine has
                         re-booted/re-initialized since SNMP engine ID was
                         last configured (v3)
    :param engine_time: the number of seconds since the engine_boots counter
                        was last incremented (v3)
    :param our_identity: the fingerprint or file name for the local X.509
                         certificate to use for our identity (run
                         net-snmp-cert to create and manage certificates)
                         (v3 TLS / DTLS)
    :param their_identity: the fingerprint or file name for the local X.509
                           certificate to use for their identity
                           (v3 TLS / DTLS)
    :param their_hostname: their hostname to expect; either their_hostname
                           or a trusted certificate plus a hostname is needed
                           to validate the server is the proper server
                           (v3 TLS / DTLS)
    :param trust_cert: a trusted certificate to use for validating
                       certificates; typically this would be a CA
                       certificate (v3 TLS / DTLS)
    :param use_long_names: set to True to have <tags> for getnext methods
                           generated preferring longer Mib name convention
                           (e.g., system.sysDescr vs just sysDescr)
    :param use_numeric: set to True to have <tags> returned by the get
                        methods untranslated (i.e. dotted-decimal). Setting
                        the use_long_names value for the session is highly
                        recommended
    :param use_sprint_value: set to True to have return values for get
                             and getnext methods formatted with the libraries
                             sprint_value function. This will result in
                             certain data types being returned in
                             non-canonical format Note: values returned with
                             this option set may not be appropriate for set
                             operations
    :param use_enums: set to True to have integer return values converted
                      to enumeration identifiers if possible, these values
                      will also be acceptable when supplied to set operations
    :param best_guess: this setting controls how oids are parsed; setting
                       to 0 causes a regular lookup.  setting to 1 causes a
                       regular expression match (defined as -Ib in snmpcmd);
                       setting to 2 causes a random access lookup (defined
                       as -IR in snmpcmd).
    :param retry_no_such: if enabled NOSUCH errors in get pdus will be
                          repaired, removing the SNMP variable in error, and
                          resent; undef will be returned for all NOSUCH
                          SNMP variables, when set to False this feature is
                          disabled and the entire get request will fail on
                          any NOSUCH error (applies to v1 only)
    :param abort_on_nonexistent: raise an exception if no object or no
                                 instance is found for the given oid and
                                 oid index
    """

    def __init__(
        self, hostname='localhost', version=3, community='public',
        timeout=1, retries=3, remote_port=0, local_port=0,
        security_level='no_auth_or_privacy', security_username='initial',
        privacy_protocol='DEFAULT', privacy_password='',
        auth_protocol='DEFAULT', auth_password='', context_engine_id='',
        security_engine_id='', context='', engine_boots=0, engine_time=0,
        our_identity='', their_identity='', their_hostname='',
        trust_cert='', use_long_names=False, use_numeric=False,
        use_sprint_value=False, use_enums=False, best_guess=0,
        retry_no_such=False, abort_on_nonexistent=False
    ):
        # Validate and extract the remote port
        if ':' in hostname:
            if remote_port:
                raise ValueError(
                    'a remote port was specified yet the hostname appears '
                    'to have a port defined too'
                )
            else:
                hostname, remote_port = hostname.split(':')
                remote_port = int(remote_port)

        self.hostname = hostname
        self.version = version
        self.community = community
        self.timeout = timeout
        self.retries = retries
        self.local_port = local_port
        self.remote_port = remote_port
        self.security_level = security_level
        self.security_username = security_username
        self.privacy_protocol = privacy_protocol
        self.privacy_password = privacy_password
        self.auth_protocol = auth_protocol
        self.auth_password = auth_password
        self.context_engine_id = context_engine_id
        self.security_engine_id = security_engine_id
        self.context = context
        self.engine_boots = engine_boots
        self.engine_time = engine_time
        self.our_identity = our_identity
        self.their_identity = their_identity
        self.their_hostname = their_hostname
        self.trust_cert = trust_cert
        self.use_long_names = use_long_names
        self.use_numeric = use_numeric
        self.use_sprint_value = use_sprint_value
        self.use_enums = use_enums
        self.best_guess = best_guess
        self.retry_no_such = retry_no_such
        self.abort_on_nonexistent = abort_on_nonexistent

        # The following variables are required for internal use as they are
        # passed to the C interface

        #: internal field used to cache a created session structure
        self.sess_ptr = None

        #: read-only, holds the error message assoc. w/ last request
        self.error_string = ''

        #: read-only, holds the snmp_err or status of last request
        self.error_number = 0

        #: read-only, holds the snmp_err_index when appropriate
        self.error_index = 0

        # Check for transports that may be tunneled
        tunneled = re.match('^(tls|dtls|ssh)', self.hostname)

        # Calculate our timeout in microseconds
        timeout_microseconds = int(self.timeout * 1000000)

        # Tunneled
        if tunneled:
            # TODO: Determine the best way to test this
            self.sess_ptr = interface.session_tunneled(
                self.version,
                self.connect_hostname,
                self.local_port,
                self.retries,
                timeout_microseconds,
                self.security_username,
                SECURITY_LEVEL_MAPPING[self.security_level],
                self.context_engine_id,
                self.context,
                self.our_identity,
                self.their_identity,
                self.their_hostname,
                self.trust_cert
            )

        # SNMP v3
        elif self.version == 3:
            self.sess_ptr = interface.session_v3(
                self.version,
                self.connect_hostname,
                self.local_port,
                self.retries,
                timeout_microseconds,
                self.security_username,
                SECURITY_LEVEL_MAPPING[self.security_level],
                self.security_engine_id,
                self.context_engine_id,
                self.context,
                self.auth_protocol,
                self.auth_password,
                self.privacy_protocol,
                self.privacy_password,
                self.engine_boots,
                self.engine_time
            )

        # SNMP v1 & v2
        else:
            self.sess_ptr = interface.session(
                self.version,
                self.community,
                self.connect_hostname,
                self.local_port,
                self.retries,
                timeout_microseconds
            )

    @property
    def connect_hostname(self):
        if self.remote_port:
            return '{0}:{1}'.format(self.hostname, self.remote_port)
        else:
            return self.hostname

    def get(self, oids):
        """
        Perform an SNMP GET operation using the prepared session to
        retrieve a particular piece of information.

        :param oids: you may pass in a list of OIDs or single item; each item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        :return: an SNMPVariable object containing the value that was
                 retrieved or a list of objects when you send in a list of
                 OIDs
        """

        # Build our variable bindings for the C interface
        varlist, is_list = build_varlist(oids)

        # Perform the SNMP GET operation
        interface.get(self, varlist)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            validate_results(varlist)

        # Return a list or single item depending on what was passed in
        return list(varlist) if is_list else varlist[0]

    def set(self, oid, value, snmp_type=None):
        """
        Perform an SNMP SET operation using the prepared session.

        :param oid: the OID that you wish to set which may be a string
                    representing the entire OID (e.g. 'sysDescr.0') or may
                    be a tuple containing the name as its first item and
                    index as its second (e.g. ('sysDescr', 0))
        :param value: the value to set the OID to
        :param snmp_type: if a numeric OID is used and the object is not in
                          the parsed MIB, a type must be explicitly supplied
        :return: a boolean indicating the success of the operation
        """

        varlist = SNMPVariableList()
        # OIDs specified as a tuple (e.g. ('sysContact', 0))
        if isinstance(oid, tuple):
            oid, oid_index = oid
            varlist.append(SNMPVariable(oid, oid_index, value, snmp_type))
        # OIDs specefied as a string (e.g. 'sysContact.0')
        else:
            varlist.append(SNMPVariable(oid, value=value, snmp_type=snmp_type))

        # Perform the set operation and return whether or not it worked
        success = interface.set(self, varlist)
        return bool(success)

    def set_multiple(self, oid_values):
        """
        Perform an SNMP SET operation on multiple OIDs with multiple
        values using the prepared session.

        :param oid_values: a list of tuples whereby each tuple contains a
                           (oid, value) or an (oid, value, snmp_type)
        :return: a list of SNMPVariable objects containing the values that
                 were retrieved via SNMP
        """

        varlist = SNMPVariableList()
        for oid_value in oid_values:
            if len(oid_value) == 2:
                oid, value = oid_value
                snmp_type = None
            # TODO: Determine the best way to test this
            else:
                oid, value, snmp_type = oid_value

            # OIDs specified as a tuple (e.g. ('sysContact', 0))
            if isinstance(oid, tuple):
                oid, oid_index = oid
                varlist.append(SNMPVariable(oid, oid_index, value, snmp_type))
            # OIDs specefied as a string (e.g. 'sysContact.0')
            else:
                varlist.append(
                    SNMPVariable(oid, value=value, snmp_type=snmp_type)
                )

        # Perform the set operation and return whether or not it worked
        success = interface.set(self, varlist)
        return bool(success)

    def get_next(self, oids):
        """
        Uses an SNMP GETNEXT operation using the prepared session to
        retrieve the next variable after the chosen item.

        :param oids: you may pass in a list of OIDs or single item; each item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        :return: an SNMPVariable object containing the value that was
                 retrieved or a list of objects when you send in a list of
                 OIDs
        """

        # Build our variable bindings for the C interface
        varlist, is_list = build_varlist(oids)

        # Perform the SNMP GET operation
        interface.getnext(self, varlist)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            validate_results(varlist)

        # Return a list or single item depending on what was passed in
        return list(varlist) if is_list else varlist[0]

    def get_bulk(self, oids, non_repeaters=0, max_repetitions=10):
        """
        Performs a bulk SNMP GET operation using the prepared session to
        retrieve multiple pieces of information in a single packet.

        :param oids: you may pass in a list of OIDs or single item; each item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        :param non_repeaters: the number of objects that are only expected to
                              return a single GETNEXT instance, not multiple
                              instances
        :param max_repetitions: the number of objects that should be returned
                                for all the repeating OIDs
        :return: a list of SNMPVariable objects containing the values that
                 were retrieved via SNMP
        """

        if self.version == 1:
            raise EasySNMPError(
                'you cannot perform a bulk GET operation for SNMP version 1'
            )

        # Build our variable bindings for the C interface
        varlist, _ = build_varlist(oids)

        interface.getbulk(self, non_repeaters, max_repetitions, varlist)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            validate_results(varlist)

        # Return a list of variables
        return varlist

    def walk(self, oids='.1.3.6.1.2.1'):
        """
        Uses SNMP GETNEXT operation using the prepared session to
        automatically retrieve multiple pieces of information in an OID.

        :param oids: you may pass in a single item (multiple values currently
                     experimental) which may be a string representing the
                     entire OID (e.g. 'sysDescr.0') or may be a tuple
                     containing the name as its first item and index as its
                     second (e.g. ('sysDescr', 0))
        :return: a list of SNMPVariable objects containing the values that
                 were retrieved via SNMP
        """

        # Build our variable bindings for the C interface
        varlist, _ = build_varlist(oids)

        # Perform the SNMP walk using GETNEXT operations
        interface.walk(self, varlist)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            validate_results(varlist)

        # Return a list of variables
        return list(varlist)

    def bulkwalk(self, oids='.1.3.6.1.2.1', non_repeaters=0,
                 max_repetitions=10):
        """
        Uses SNMP GETBULK operation using the prepared session to
        automatically retrieve multiple pieces of information in an OID
        :param oids: you may pass in a single item (multiple values currently
                     experimental) which may be a string representing the
                     entire OID (e.g. 'sysDescr.0') or may be a tuple
                     containing the name as its first item and index as its
                     second (e.g. ('sysDescr', 0))
        :return: a list of SNMPVariable objects containing the values that
                 were retrieved via SNMP
        """

        if self.version == 1:
            raise EasySNMPError(
                "BULKWALK is not available for SNMP version 1")

        # Build our variable bindings for the C interface
        varlist, _ = build_varlist(oids)

        # Perform the SNMP walk using GETNEXT operations
        interface.bulkwalk(self, non_repeaters, max_repetitions, varlist)

        # Validate the variable list returned
        if self.abort_on_nonexistent:
            validate_results(varlist)

        # Return a list of variables
        return varlist
