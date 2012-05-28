import wmi, os, platform
from pwplib.OperatingSystem import *
import shutil
from _winreg import (HKEY_LOCAL_MACHINE, KEY_ALL_ACCESS, OpenKey, EnumValue, QueryValueEx)

class Machine:
    """
        Machine Class to represent computers in the network giving us a Virtual Access to them.
    """
    type = "computer"
    name = "NONE"
    domain = "NONE"
    workgroup = "NONE"
    ipaddress = "0.0.0.0"
    macaddress = "00:00:00:00:00:00"
    OperatingSystem = None
    __c = None # Machine handle
    
    def __init__(self, connection=None):
        """
            Initialize a new Machine object, gathering few informations for its description.
            connection: handle to a remote server (returned by connect_server method from WMI).
        """
        self.__c = wmi.WMI(wmi=connection, privileges=["RemoteShutdown"])
        gather = self.WQL("Select * from Win32_ComputerSystem")[0]
        if connection is None:
            self.type = "localhost" # if it"s the localhost machine
        try: #try to get the DNSHostName, if it fails --> Computer Name
            self.name = gather.DNSHostName 
        except:
            self.name = gather.Name
        self.domain = self.workgroup = gather.Domain
        if gather.WorkGroup is not None:
            self.workgroup = gather.WorkGroup
        
        try: # Get Network Adaptater configurations
            minter = self.__c.Win32_NetworkAdapterConfiguration(IPEnabled=True)[0] # Machine's interface
            self.ipaddress = minter.IPAddress
            self.macaddress = minter.MACAddress
        except ImportError:
            pass
        
        self.OperatingSystem = self.getOSinformations() # Initialize OS informations
        
    def copytoshare(self, src, dst):
        """
            Copy from localhost source to destination directory.
            src: Source.
            dst: Destination
        """
        shutil.copy(src, dst)
      
    def WQL(self, wql):
        """
            Performs a wql query.
            WQL(self, wql) -->  _wmi_object representations of the results.
            
                wql: should be a string representing the query.
        """
        return self.__c.query(wql)
    
    def psExecute(self, cmd):
        """
            Execute a process using WMI Win32_Process Class.
            psExecute(self, cmd) --> state integer
            
                cmd: String representing the process to launch.
        """
        process_id, return_value = self.__c.Win32_Process.Create(CommandLine=cmd)
        return return_value
    
    def installMSI(self, path, AllUsers=False):
        """
            Install MSI using WMI Win32_Product Class.
            installMSI(self, path, [AllUsers]) --> state tuple.
            
                path: Package Location (String).
                AllUsers: True or False --> Install for all users.
        """
        status = self.__c.Win32_Product.Install(PackageLocation=path, AllUsers=AllUsers)
        return status
    
    def installEXE(self, path):
        """
            Install EXE programs.
            installEXE(self, path) --> state integer.
            
                path: Executable Location (String).
        """
        return self.psExecute(path + " /S")
    
    def getExeList(self, justpath=False):
        """
            Get a list of installed executables.
            getExeList() --> List of installed EXEs
        """
        reg = self.__c.StdRegProv # Using StdRegProv Class for registry
	l = []
        if justpath is False: # Part based on Android-scripting Engine code with few modifications
            keyPath = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
            result, names = reg.EnumKey(2147483650, keyPath)
            count = 0
            while count < len(names):
                try:      
                    path = keyPath + "\\" + names[count]
                    key = OpenKey(HKEY_LOCAL_MACHINE, path, 0)
                    temp = QueryValueEx(key, 'DisplayName')
                    displayname = str(temp[0])
                    displayversion = ''
                    try:
                        temp = QueryValueEx(key, 'DisplayVersion')
                        displayversion = str(temp[0])
                    except:
                        pass
                    l.append((displayname,displayversion))
                    count += 1
                except WindowsError:
                    l.append((names[count],))
                    count += 1
                    continue
            return l
        else: # Shows only the exec's paths
            keyPath = r"Software\Microsoft\Windows\CurrentVersion\App Paths"
            result, names = reg.EnumKey(2147483650, keyPath)
            count = 0
            while count < len(names):
                try:      
                    path = keyPath + "\\" + names[count]
                    key = OpenKey(HKEY_LOCAL_MACHINE, path, 0)
                    temp = QueryValueEx(key, 'Path')
                    tPath = str(temp[0]+'\\'+names[count])
                    l.append(tPath)
                    count += 1
                except WindowsError:
                    l.append(names[count])
                    count += 1
                    continue
            return l
    
    def getMsiList(self):
        """
            Get a descriptive list of MSI installed programs using WMI Win32_Product Class.
            getMsiList() --> List of installed MSI.
        """
        list = []
        for x in self.WQL("Select Name from Win32_Product"): # Query the Name of installed products
            list.append((x.Name, x.Version))
        return list
    
    def Reboot(self):
        """
            Reboot a computer using RemoteShutdown and Win32_OperatingSystem Class.
        """
        os = self.__c.Win32_OperatingSystem(Primary=1)[0]
        os.Reboot() # Reboot!
        
    def getOSinformations(self):
        """
            Get exta informations about the Operating System
        """
        defs = {}
        os = self.__c.Win32_OperatingSystem()[0]
        defs['name'] = os.Name.split("|")[0]
        defs['version'] = os.Version
        return OperatingSystem(defs)
    
    def __repr__(self):
        str = "\nMachine [" + self.name + "] \n{"
        str += "\n\ttype: " + self.type
        str += "\n\tname: " + self.name
        str += "\n\tworkgroup: " + self.workgroup
        str += "\n\tdomain: " + self.domain
        str += "\n\tipaddress: " + repr(self.ipaddress)
        str += "\n\tmacaddress: " + self.macaddress
        str += "\n\t" + repr(self.OperatingSystem)
        str += "\n}"
        
        return str