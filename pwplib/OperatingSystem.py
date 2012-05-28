class OperatingSystem:
    """
        OperatingSystem representation
    """
    infos = {} # Operating System informations container
    
    def __init__(self, initInfos={}):
        self.infos = initInfos
    
    def __repr__(self):
        str = "<[OperatingSystem]: "
        for key, value in self.infos.iteritems():
            str += key+"=\""+value+"\"; "
        str += ">"
        return str