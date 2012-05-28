import win32com.client, wmi
from core.config import *
import getpass

class Network:
    """
        Network Class to represent domains or/and workgroups
    """
    protocole = "" # Protocole : LDAP, WinNT, SQL ...
    domain = "" # Domain
    __computers = [] # List of computers (machines)
    
    def __init__(self, domain, protocole="WinNT"):
        """
            Initialize a Network Objet to browse our domain.
            
                domain: Windows domain
                protocol = protocol type (by default WinNT for WMI)
        """
        self.protocole = protocole
        self.domain = domain

    def discovery(self):
        """
            Discover computers which are from the same Group/Domain.
        """
        c = win32com.client.GetObject(self.protocole + "://" + self.domain)
        self.__computers = [x.Name for x in c if x.Class.lower() == "computer"]
        return self.__computers

    def countPC(self):
        """
            Count the number of discovered computers.
        """
        return len(self.__computers)
    
    def getComputersList(self):
        """
            Give the entire list of discovered computers.
            getComputersList() --> List of computers
        """
        return self.__computers
    
    @classmethod
    def connectTo(cls, server, user="", password="", impersonation_level="Impersonate", namespace=""):
        """
            Connect to a remote server
            connectTo(server, [user], [password], [impersonation_level], [namespace]) --> COMObject Instance
        """
        print "Connecting to '%s'" % server
        if user == "": # asking for missing login username
            user = raw_input("Username: ")
        if password == "": # asking for missing login password
            password = getpass.getpass()
        connect = wmi.connect_server(server=server, user=user, password=password, impersonation_level=impersonation_level, namespace=namespace)

        return connect