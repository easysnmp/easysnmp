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
        self, Version=3, DestHost='localhost', Community='public',
        Timeout=1000000, Retries=3, RemotePort=161, LocalPort=0,
        SecLevel='noAuthNoPriv', SecName='initial', PrivProto='DEFAULT',
        PrivPass='', AuthProto='DEFAULT', AuthPass='', ContextEngineId='',
        SecEngineId='', Context='', Engineboots=0, Enginetime=0, UseNumeric=0,
        OurIdentity='', TheirIdentity='', TheirHostname='', TrustCert=''
    ):
        self.Version = Version
        self.DestHost = DestHost
        self.Community = Community
        self.Timeout = Timeout
        self.Retries = Retries
        self.RemotePort = RemotePort
        self.LocalPort = LocalPort
        self.SecLevel = SecLevel
        self.SecName = SecName
        self.PrivProto = PrivProto
        self.PrivPass = PrivPass
        self.AuthProto = AuthProto
        self.AuthPass = AuthPass
        self.ContextEngineId = ContextEngineId
        self.SecEngineId = SecEngineId
        self.Context = Context
        self.Engineboots = Engineboots
        self.Enginetime = Enginetime
        self.UseNumeric = UseNumeric
        self.OurIdentity = OurIdentity
        self.TheirIdentity = TheirIdentity
        self.TheirHostname = TheirHostname
        self.TrustCert = TrustCert

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

        # check for transports that may be tunneled
        transportCheck = re.compile('^(tls|dtls|ssh)')
        match = transportCheck.match(self.DestHost)

        if match:
            self.sess_ptr = client_intf.session_tunneled(
                self.Version,
                self.DestHost,
                self.LocalPort,
                self.Retries,
                self.Timeout,
                self.SecName,
                SECURITY_LEVEL_MAPPING[self.SecLevel],
                self.ContextEngineId,
                self.Context,
                self.OurIdentity,
                self.TheirIdentity,
                self.TheirHostname,
                self.TrustCert)
        elif self.Version == 3:
            self.sess_ptr = client_intf.session_v3(
                self.Version,
                self.DestHost,
                self.LocalPort,
                self.Retries,
                self.Timeout,
                self.SecName,
                SECURITY_LEVEL_MAPPING[self.SecLevel],
                self.SecEngineId,
                self.ContextEngineId,
                self.Context,
                self.AuthProto,
                self.AuthPass,
                self.PrivProto,
                self.PrivPass,
                self.Engineboots,
                self.Enginetime)
        else:
            self.sess_ptr = client_intf.session(
                self.Version,
                self.Community,
                self.DestHost,
                self.LocalPort,
                self.Retries,
                self.Timeout)

    def get(self, varlist):
        res = client_intf.get(self, varlist)
        return res

    def set(self, varlist):
        res = client_intf.set(self, varlist)
        return res

    def getnext(self, varlist):
        res = client_intf.getnext(self, varlist)
        return res

    def getbulk(self, nonrepeaters, maxrepetitions, varlist):
        if self.Version == 1:
            return None
        res = client_intf.getbulk(self, nonrepeaters, maxrepetitions, varlist)
        return res

    def walk(self, varlist):
        res = client_intf.walk(self, varlist)
        return res

    def __del__(self):
        res = client_intf.delete_session(self)
        return res
