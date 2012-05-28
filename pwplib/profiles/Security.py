import wmi, os, platform
from pwplib.Machine import *
from pwplib.OperatingSystem import *

class Security(Machine):
    """
        Security Profile example --> to be extended ;)
    """
    __c2 = None # security machine wmi handle
    __c3 = None # security machine wmi handle2
    
    def __init__(self, connection=None):
        """
            Initialize a new Machine object, gathering few informations for its description.
            connection: handle to a remote server (returned by connect_server method from WMI).
        """
        Machine.__init__(self, connection)
        self.__c2 = wmi.WMI(wmi=connection, namespace=r"root\SecurityCenter")
        self.__c3 = wmi.WMI(wmi=connection, namespace=r"root\SecurityCenter2")
        
    def WQLsec(self, wql):
        """
            Performs a wql query from SecurityCenter's namespace.
            WQLsec(self, wql) -->  _wmi_object representations of the results.
            
                wql: should be a string representing the query.
        """
        result = (0, [])
        if self.__c2 is not None:
            result = (0, self.__c2.query(wql)) # The first element of the tuple show which handle we are using to get the result
            if len(result[1]) == 0: # if the result is empty we look to the second namespace
                result = (1, self.__c3.query(wql))
        return result

    def checkforDEP(self):
        """
            Few assesments that perform a DEP security check (32bit apps, Drivers, availability, and so on)
            more infos: http://msdn.microsoft.com/en-us/library/windows/desktop/aa394239%28v=vs.85%29.aspx
            
                Returns: Definitions of machine's DEP states
        """
        defs = {}
        osinfo = self.WQL("Select * From Win32_OperatingSystem")[0]
        defs["DriverDEP"] = osinfo.DataExecutionPrevention_Drivers
        defs["AvailableDEP"] = osinfo.DataExecutionPrevention_Available
        defs["32bitDEP"] = osinfo.DataExecutionPrevention_32BitApplications
        support = osinfo.DataExecutionPrevention_SupportPolicy
        description = ""
        if support == 0:
            description = "DEP is turned off for all 32-bit applications on the computer with no exceptions. This setting is not available for the user interface."
        elif support == 1:
            description = "DEP is enabled for all 32-bit applications on the computer. This setting is not available for the user interface."
        elif support == 2:
            description = "DEP is enabled for a limited number of binaries, the kernel, and all Windows-based services. However, it is off by default for all 32-bit applications. A user or administrator must explicitly choose either the AlwaysOn or the OptOut setting before DEP can be applied to 32-bit applications."
        elif support == 3:
            description = "DEP is enabled by default for all 32-bit applications. A user or administrator can explicitly remove support for a 32-bit application by adding the application to an exceptions list."
        defs["DEPSupportPolicy"] = {"Code":support, "Description":description}
        
        return defs
        
    def getEncryptionLevel(self):
        """
            Returns the encryption level used for transactions.
        """
        osinfo = self.WQL("Select * From Win32_OperatingSystem")[0]
        return osinfo.EncryptionLevel
        
    def getSecurityUpdatesList(self):
        """
            Returns the list of Installed QuickFixes
        """
        list = []
        quickfixes = self.WQL("Select * from Win32_QuickFixEngineering") # Search for QuickFixes
        for quickfixe in quickfixes:
            list.append({'HotFixID':quickfixe.HotFixID})
        return list
    
    def getAVList(self):
        """
            Get the list of installed Antiviruses
            
                getAVList() --> List of Antiviruses with properties
        """
        nhandle, results = self.WQLsec("Select * from AntivirusProduct")
        glist = []
        for result in results:
            defs = {}
            if nhandle == 0:
                defs["comanyName"] = result.companyName
                defs["displayName"] = result.displayName
                defs["onAccessScanningEnabled"] = result.onAccessScanningEnabled
                defs["productUptoDate"] = result.productUptoDate
                defs["versionNumber"] = result.versionNumber
            else:
                defs["displayName"] = result.displayName
                defs["productState"] = result.productState
            glist.append(defs)
        return glist
        
    def getFirewallList(self):
        """
            Get the list of installed Firewall(s)
            
                getFirewallist() --> List of Firewall(s) with properties
        """
        nhandle, results = self.WQLsec("Select * from FirewallProduct")
        glist = []
        for result in results:
            defs = {}
            if nhandle == 0:
                defs["comanyName"] = result.companyName
                defs["displayName"] = result.displayName
                defs["enabled"] = result.enabled
                defs["versionNumber"] = result.versionNumber
            else:
                defs["displayName"] = result.displayName
                defs["productState"] = result.productState
            glist.append(defs)
        return glist
        
    def getASpyList(self):
        """
            Get the list of installed Anti-Spywares
            
                getASpyList() --> List of Anti-Spywares with properties
        """
        nhandle, results = self.WQLsec("Select * from AntiSpywareProduct")
        glist = []
        for result in results:
            defs = {}
            if nhandle == 0:
                defs["comanyName"] = result.companyName
                defs["displayName"] = result.displayName
                defs["enabled"] = result.productEnabled
            else:
                defs["displayName"] = result.displayName
                defs["productState"] = result.productState
            glist.append(defs)
        return glist

    def checkforPAE(self):
            keyPath = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
            key = OpenKey(HKEY_LOCAL_MACHINE, keyPath, 0)
            value = QueryValueEx(key, "PhysicalAddressExtension")
            return value[0]