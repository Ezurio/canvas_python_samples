class AltBeacon:
    """
    Alt Beacon Class
    AltBeacon is a protocol specification that defines a message format
    for proximity beacon advertisements. AltBeacon proximity beacon
    advertisements are transmitted by devices for the purpose of signaling
    their proximity to nearby receivers. The contents of the emitted
    message contain information that the receiving device can use to
    identify the beacon and to compute its relative distance to the
    beacon.
    The receiving device may use this information as a contextual trigger
    to execute procedures and implement behaviors that are relevant to
    being in proximity to the transmitting beacon.
    """
    
    """
    Common alt Beacon advert header
    """
    message_header = [
        0x02, 0x01, 0x06,
        0x1b, 0xff
    ]
    
    ALT_BEACON_CODE = [0xBE, 0xAC]
    
    def __init__(self, mfg_id:int, beacon_id:any, beacon_data:any, ranging_data:int, mfg_data:int):
        if mfg_id > 0xffff or mfg_id < 0:
            raise Exception("Manufacturer ID must be 16 bits.")
        if len(beacon_id) != 16:
            raise Exception("Beacon ID must be 16 bytes")
        if ranging_data > 0 or ranging_data < -127:
            raise Exception("Ranging data must be in range")
        
        self.mfg_id = mfg_id
        self.beacon_id = beacon_id
        self.ranging_data = ranging_data
        self.__build(beacon_data, mfg_data)
    
    def get_beacon(self) -> any:
        return self.message
    
    def update(self, beacon_data:any, mfg_data:int):
        self.__build(beacon_data, mfg_data)
    
    def __build(self, beacon_data:any, mfg_data:int):
        """
        Private build function for AltBeacon objects
        
        :param major (int): A 16 bit integer representing 'major' user data
        :param minor (int): A 16 bit integer representing 'minor' user data
        """
        if len(beacon_data) != 4:
            raise Exception("Beacon data must be 4 bytes")
        if mfg_data > 0xff or mfg_data < 0:
            raise Exception("Manufacturer data must be 8 bits")
        
        self.message = []
        self.message += AltBeacon.message_header
        self.message.append(self.mfg_id & 0x00ff)
        self.message.append((self.mfg_id & 0xff00) >> 8)
        self.message += AltBeacon.ALT_BEACON_CODE
        self.message += self.beacon_id
        self.message += beacon_data
        self.message.append(self.ranging_data & 0xFF)
        self.message.append(mfg_data)
