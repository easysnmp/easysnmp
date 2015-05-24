import re


import client_intf

# Mapping between security level strings and their associated integer values
SECURITY_LEVEL_MAPPING = {
    'noAuthNoPriv': 1,
    'authNoPriv': 2,
    'authPriv': 3
}


class Session(object):
    """A Net-SNMP session which may be setup once and then used to query
    and manipulate SNMP data.
    """

    def __init__(
        self, version=3, hostname='localhost', community='public',
        timeout=1000000, retries=3, remote_port=161, local_port=0,
        security_level='noAuthNoPriv', security_username='initial',
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

        self.sess_ptr = None

        # The following variables are required for internal use as they are
        # passed to the C interface.  Sadly, they must stay in CamelCase
        # for the time being.
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
        transport_check = re.compile('^(tls|dtls|ssh)')
        match = transport_check.match(self.hostname)

        # Tunneled
        if match:
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
        res = client_intf.get(self, var_list)
        return res

    def set(self, var_list):
        res = client_intf.set(self, var_list)
        return res

    def get_next(self, var_list):
        res = client_intf.getnext(self, var_list)
        return res

    def get_bulk(self, non_repeaters, max_repetitions, var_list):
        if self.version == 1:
            return None
        res = client_intf.getbulk(
            self, non_repeaters, max_repetitions, var_list
        )
        return res

    def walk(self, var_list):
        res = client_intf.walk(self, var_list)
        return res

    def __del__(self):
        res = client_intf.delete_session(self)
        return res
