import re

from . import interface
from .exceptions import PyNetSNMPError, PyNetSNMPNoSuchObjectError
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
        try:
            varbind.iid = int(varbind.iid)
        except ValueError:
            varbind.iid = None

        # print 'Mapping type={}, tag={}, iid={}, val={}'.format(
        #     varbind.type, varbind.tag, varbind.iid, varbind.val
        # )
        # print '--- {} ---'.format(varbind.val)
        if varbind.type == 'NOSUCHOBJECT':
            raise PyNetSNMPNoSuchObjectError('No such object could be found')
        elif (
            varbind.type not in TYPE_MAPPING or
            not TYPE_MAPPING[varbind.type]
        ):
            print(
                'Unsupported SNMP type {}: {}'.format(
                    varbind.type, varbind.val
                )
            )
        else:
            SNMPDataType = TYPE_MAPPING[varbind.type]
            results.append(SNMPDataType(varbind.val, varbind.tag, varbind.iid))

    return results


class Session(object):
    """A Net-SNMP session which may be setup once and then used to query
    and manipulate SNMP data.

    :param version: the SNMP version to use (1, 2 or 3)
    :param hostname: hostname of the device to communicate with
    :param community: community string to use when communicating
                      (SNMP v1 and v2 only)
    :param timeout:
    :param retries:
    :param remote_port:
    :param local_port:
    :param security_level:
    :param security_username:
    :param privacy_protocol:
    :param privacy_password:
    :param auth_protocol:
    :param auth_password:
    :param context_engine_id:
    :param security_engine_id:
    :param context:
    :param engine_boots:
    :param engine_time:
    :param our_identity:
    :param their_identity:
    :param their_hostname:
    :param trust_cert:
    """

    def __init__(
        self, version=3, hostname='localhost', community='public',
        timeout=1000000, retries=3, remote_port=161, local_port=0,
        security_level='no_auth_or_privacy', security_username='initial',
        privacy_protocol='DEFAULT', privacy_password='',
        auth_protocol='DEFAULT', auth_password='', context_engine_id='',
        security_engine_id='', context='', engine_boots=0, engine_time=0,
        our_identity='', their_identity='', their_hostname='',
        trust_cert=''
    ):
        self.version = version
        self.hostname = hostname
        self.community = community
        self.timeout = timeout
        self.retries = retries
        # TODO: Implement the ability to set the remote port explicitly
        self.remote_port = remote_port
        self.local_port = local_port
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
        self.sess_ptr = None
        self.use_long_names = 0
        self.use_numeric = 0
        self.use_sprint_value = 0
        self.use_enums = 0
        self.best_guess = 0
        self.retry_no_such = 0
        self.error_str = ''
        self.error_num = 0
        self.error_ind = 0

        # Check for transports that may be tunneled
        tunneled = re.match('^(tls|dtls|ssh)', self.hostname)

        # Tunneled
        if tunneled:
            self.sess_ptr = interface.session_tunneled(
                self.version,
                self.hostname,
                self.local_port,
                self.retries,
                self.timeout,
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
                self.timeout,
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
                self.timeout
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

    def set(self, var_list):
        """Perform an SNMP SET operation using the prepared session to
        retrieve a particular piece of information
        """

        result = interface.set(self, var_list)
        return result

    def get_next(self, oids):
        """Uses an SNMP GETNEXT operation using the prepared session to
        retrieve the next variable after the chosen item
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
        """

        if self.version == 1:
            raise PyNetSNMPError(
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
