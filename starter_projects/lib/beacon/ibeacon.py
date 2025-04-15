class iBeacon:
    """
    Build an iBeacon
    """
    
    """
    Common iBeacon advert header
    """
    message_header = [
        0x02, 0x01, 0x06,
        0x1a, 0xff, 0x4c, 0x00, 0x02, 0x15
    ]
    
    def __init__(self, uuid:str, major:int, minor:int, measured_power:int):
        """
        Build the initial iBeacon object
        
        :param uuid (str): A sting containing the beacon UUID. This can
            be formatted with or without '-' characters but must resolve
            to 16 bytes.
        :param major (int): A 16 bit integer representing 'major' user data
        :param minor (int): A 16 bit integer representing 'minor' user data
        :param measured_power (int): An 8 bit signed integer indicating the
            measured TX power at 1m.
        """
        uuid_len = len(uuid)
        if (uuid_len == 36 or uuid_len == 32) == False:
            raise Exception("EID must be a correctly formatted UUID string '-'s may be included or omitted")
        if measured_power > 127 or measured_power < -127:
            raise Exception("Measured power is out of range")
        
        self.uuid_as_bytes = iBeacon.__uuid_from_string(uuid)
        self.measured_power = measured_power
        self.__build(major, minor)
    
    def get_beacon(self) -> any:
        """
        Get the beacon data for this iBeacon Object
        
        :returns Bytes object containing the beacon data:
        """
        return self.message
    
    def update(self, major:int, minor:int):
        """
        Update the iBeacon object data with new major and minor data
        
        :param major (int): A 16 bit integer representing 'major' user data
        :param minor (int): A 16 bit integer representing 'minor' user data
        """
        self.__build(major, minor)
    
    def __build(self, major:int, minor:int):
        """
        Private build function for iBeacon objects
        
        :param major (int): A 16 bit integer representing 'major' user data
        :param minor (int): A 16 bit integer representing 'minor' user data
        """
        if major > 0xffff or major < 0x0000:
            raise Exception("Major value must be 16 bits.")
        if minor > 0xffff or minor < 0x0000:
            raise Exception("Minor value must be 16 bits.")
        self.message = []
        self.message += iBeacon.message_header
        self.message += self.uuid_as_bytes
        self.message.append((major & 0xff00) >> 8)
        self.message.append(major & 0x00ff)
        self.message.append((minor & 0xff00) >> 8)
        self.message.append(minor & 0x00ff)
        self.message.append(self.measured_power & 0xFF)
    
    def __uuid_from_string(uuid:str) -> any:
        """
        Private conversion of a uuid string to bytes
        
        :param uuid (str): UUID to convert
        :returns Bytes object containing the converted UUD data:
        """
        no_dash_uuid = uuid.replace('-', '')
        uuid_bytes = bytes.fromhex(no_dash_uuid)
        
        padding = 16 - len(uuid_bytes)
        while(padding > 0):
            uuid_bytes.append(0)
            padding -= 1
        
        return uuid_bytes
