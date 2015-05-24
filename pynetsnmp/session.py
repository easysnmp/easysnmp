import re

import client_intf

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
        # passed to the C interface.  Sadly, they must stay in CamelCase
        # for the time being.
        self.sess_ptr = None
        self.UseLongNames = 0
        self.UseNumeric = 0
        self.UseSprintValue = 0
        self.UseEnums = 0
        self.BestGuess = 0
        self.RetryNoSuch = 0
        self.ErrorStr = ''
        self.ErrorNum = 0
        self.ErrorInd = 0

        # Check for transports that may be tunneled
        tunneled = re.match('^(tls|dtls|ssh)', self.hostname)

        # Tunneled
        if tunneled:
            self.sess_ptr = client_intf.session_tunneled(
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
            self.sess_ptr = client_intf.session_v3(
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
            self.sess_ptr = client_intf.session(
                self.version,
                self.community,
                self.hostname,
                self.local_port,
                self.retries,
                self.timeout
            )

    def get(self, var_list):
        """Perform an SNMP GET operation using the prepared session to
        retrieve a particular piece of information
        """

        result = client_intf.get(self, var_list)
        return result

    def set(self, var_list):
        """Perform an SNMP SET operation using the prepared session to
        retrieve a particular piece of information
        """

        result = client_intf.set(self, var_list)
        return result

    def get_next(self, var_list):
        """Uses an SNMP GETNEXT operation using the prepared session to
        retrieve the next variable after the chosen item
        """

        result = client_intf.getnext(self, var_list)
        return result

    def get_bulk(self, non_repeaters, max_repetitions, var_list):
        """Performs a bulk SNMP GET operation using the prepared session to
        retrieve multiple pieces of information in a single packet
        """

        if self.version == 1:
            return None

        result = client_intf.getbulk(
            self, non_repeaters, max_repetitions, var_list
        )
        return result

    def walk(self, var_list):
        """Uses SNMP GETNEXT operation using the prepared session to
        automatically retrieve multiple pieces of information in an OID
        """

        result = client_intf.walk(self, var_list)
        return result

    def __del__(self):
        """Deletes the session and frees up memory"""
        return client_intf.delete_session(self)
