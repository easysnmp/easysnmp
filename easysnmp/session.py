import re

from . import interface
from .exceptions import EasySNMPError, EasySNMPNoSuchObjectError
from .data_types import TYPE_MAPPING
from .variables import Varbind, VarList

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
    """Prepare the variable binding list which will be used by the
    C interface"""
    if isinstance(oids, list):
        is_list = True
    else:
        is_list = False
        oids = [oids]

    varlist = VarList()
    for oid in oids:
        # OIDs specified as a tuple (e.g. ('sysContact', 0))
        if isinstance(oid, tuple):
            tag, iid = oid
            varlist.append(Varbind(tag, iid))
        # OIDs specefied as a string (e.g. 'sysContact.0')
        else:
            varlist.append(Varbind(oid))

    return varlist, is_list


def build_results(varlist):
    """Converts variable bindings into SNMP data types"""
    results = []

    for varbind in varlist:
        if varbind.type == 'NOSUCHOBJECT':
            raise EasySNMPNoSuchObjectError('No such object could be found')
        elif (
            varbind.type not in TYPE_MAPPING or
            not TYPE_MAPPING[varbind.type]
        ):
            raise EasySNMPError(
                'Unsupported SNMP type {} for {}.{}: {}'.format(
                    varbind.type, varbind.tag, varbind.iid, varbind.val
                )
            )
        else:
            SNMPDataType = TYPE_MAPPING[varbind.type]
            results.append(SNMPDataType(varbind.val, varbind.tag, varbind.iid))

    return results


class Session(object):
    """A Net-SNMP session which may be setup once and then used to query
    and manipulate SNMP data.

    :param hostname: hostname or IP address of SNMP agent
    :param version: the SNMP version to use; 1, 2 (equivalent to 2c) or 3
    :param community: SNMP community string (used for both R/W) (v1 & v2)
    :param timeout: seconds before retry
    :param retries: retries before failure
    :param remote_port: allow remote UDP port to be overridden
    :param local_port: TODO
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
    :param engine_boots: TODO (v3)
    :param engine_time: TODO (v3)
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
    """

    def __init__(
        self, hostname='localhost', version=3, community='public',
        timeout=1, retries=3, remote_port=161, local_port=0,
        security_level='no_auth_or_privacy', security_username='initial',
        privacy_protocol='DEFAULT', privacy_password='',
        auth_protocol='DEFAULT', auth_password='', context_engine_id='',
        security_engine_id='', context='', engine_boots=0, engine_time=0,
        our_identity='', their_identity='', their_hostname='',
        trust_cert=''
    ):
        self.hostname = hostname
        self.version = version
        self.community = community
        self.timeout = timeout
        self.retries = retries
        self.local_port = local_port
        # TODO: Implement the ability to set the remote port explicitly
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

        # The following variables are required for internal use as they are
        # passed to the C interface.

        #: internal field used to cache a created session structure
        self.sess_ptr = None

        #: set to non-zero to have <tags> for 'getnext' methods generated
        #: preferring longer Mib name convention (e.g., system.sysDescr vs
        #: just sysDescr)
        self.use_long_names = 0

        #: set to non-zero to have <tags> returned by the 'get'
        #: methods untranslated (i.e. dotted-decimal). Setting the
        #: use_long_names value for the session is highly recommended.
        self.use_numeric = 0

        #: set to non-zero to have return values for 'get' and 'getnext'
        #: methods formatted with the libraries sprint_value function. This
        #: will result in certain data types being returned in non-canonical
        #: format Note: values returned with this option set may not be
        #: appropriate for 'set' operations (see discussion of value formats
        #: in <vars> description section)
        self.use_sprint_value = 0

        #: set to non-zero to have integer return values converted to
        #: enumeration identifiers if possible, these values will also be
        #: acceptable when supplied to 'set' operations
        self.use_enums = 0

        #: this setting controls how <tags> are parsed.  setting to 0 causes
        #: a regular lookup.  setting to 1 causes a regular expression match
        #: (defined as -Ib in snmpcmd). setting to 2 causes a random access
        #: lookup (defined as -IR in snmpcmd).
        self.best_guess = 0

        #: default '0', if enabled NOSUCH errors in 'get' pdus will be
        #: repaired, removing the varbind in error, and resent - undef will
        #: be returned for all NOSUCH varbinds, when set to '0' this feature
        #: is disabled and the entire get request will fail on any NOSUCH
        #: error (applies to v1 only)
        self.retry_no_such = 0

        #: read-only, holds the error message assoc. w/ last request
        self.error_str = ''

        #: read-only, holds the snmp_err or status of last request
        self.error_num = 0

        #: read-only, holds the snmp_err_index when appropriate
        self.error_ind = 0

        # Check for transports that may be tunneled
        tunneled = re.match('^(tls|dtls|ssh)', self.hostname)

        # Calculate our timeout in microseconds
        timeout_microseconds = self.timeout * 1000000

        # Tunneled
        if tunneled:
            self.sess_ptr = interface.session_tunneled(
                self.version,
                self.hostname,
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
                self.hostname,
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
                self.hostname,
                self.local_port,
                self.retries,
                timeout_microseconds
            )

    def get(self, oids):
        """Perform an SNMP GET operation using the prepared session to
        retrieve a particular piece of information

        :param oids: you may pass in a list of OIDs or single item; eoch item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        """

        # Build our variable bindings for the C interface
        varlist, is_list = build_varlist(oids)

        # Perform the SNMP GET operation
        interface.get(self, varlist)

        # Convert the varbind results into SNMP data types
        results = build_results(varlist)

        # Return a list or single item depending on what was passed in
        return list(results) if is_list else results[0]

    def set(self, oid, value):
        """Perform an SNMP SET operation using the prepared session

        :param oids: you may pass in a list of OIDs or single item; eoch item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        """

        varlist = VarList()
        # OIDs specified as a tuple (e.g. ('sysContact', 0))
        if isinstance(oid, tuple):
            tag, iid = oid
            varlist.append(Varbind(tag, iid, val=value))
        # OIDs specefied as a string (e.g. 'sysContact.0')
        else:
            varlist.append(Varbind(oid, val=value))

        # Perform the set operation and return whether or not it worked
        success = interface.set(self, varlist)
        return bool(success)

    def set_multiple(self, oid_values):
        """Perform an SNMP SET operation on multiple OIDs with multiple
        values using the prepared session

        :param oid_values: a dict containing OIDs as keys and their
                           respective values to be set
        """

        varlist = VarList()
        for oid, value in oid_values.iteritems():
            # OIDs specified as a tuple (e.g. ('sysContact', 0))
            if isinstance(oid, tuple):
                tag, iid = oid
                varlist.append(Varbind(tag, iid, val=value))
            # OIDs specefied as a string (e.g. 'sysContact.0')
            else:
                varlist.append(Varbind(oid, val=value))

        # Perform the set operation and return whether or not it worked
        success = interface.set(self, varlist)
        return bool(success)

    def get_next(self, oids):
        """Uses an SNMP GETNEXT operation using the prepared session to
        retrieve the next variable after the chosen item

        :param oids: you may pass in a list of OIDs or single item; eoch item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        """

        # Build our variable bindings for the C interface
        varlist, is_list = build_varlist(oids)

        # Perform the SNMP GET operation
        interface.getnext(self, varlist)

        # Convert the varbind results into SNMP data types
        results = build_results(varlist)

        # Return a list or single item depending on what was passed in
        return list(results) if is_list else results[0]

    def get_bulk(self, oids, non_repeaters, max_repetitions):
        """Performs a bulk SNMP GET operation using the prepared session to
        retrieve multiple pieces of information in a single packet

        :param oids: you may pass in a list of OIDs or single item; eoch item
                     may be a string representing the entire OID
                     (e.g. 'sysDescr.0') or may be a tuple containing the
                     name as its first item and index as its second
                     (e.g. ('sysDescr', 0))
        """

        if self.version == 1:
            raise EasySNMPError(
                'You cannot perform a bulk GET operation for SNMP version 1'
            )

        # Build our variable bindings for the C interface
        varlist, _ = build_varlist(oids)

        interface.getbulk(self, non_repeaters, max_repetitions, varlist)

        # Convert the varbind results into SNMP data types
        results = build_results(varlist)

        # Return a list of results
        return results

    def walk(self, oids='.1.3.6.1.2.1'):
        """Uses SNMP GETNEXT operation using the prepared session to
        automatically retrieve multiple pieces of information in an OID

        :param oids: you may pass in a single item (multiple values currently
                     experimental) which may be a string representing the
                     entire OID (e.g. 'sysDescr.0') or may be a tuple
                     containing the name as its first item and index as its
                     second (e.g. ('sysDescr', 0))
        """

        # Build our variable bindings for the C interface
        varlist, _ = build_varlist(oids)

        # Perform the SNMP walk using GETNEXT operations
        interface.walk(self, varlist)

        # Convert the varbind results into SNMP data types
        results = build_results(varlist)

        # Return a list of results
        return list(results)

    def __del__(self):
        """Deletes the session and frees up memory"""
        return interface.delete_session(self)
