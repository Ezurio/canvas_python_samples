import time

class Eddystone:
    """
    Base Eddystone beacon class.
    This contains the common headers, types and other constant values
    that are necessary to construct one of the supported Eddystone
    beacon types.
    Also contains generic build and return functions for beacon data.

    Note: Encrypted Telemetry (TLM) beacons are not currently supported
    due to lack of Crypt libraries on this platform.
    """

    """
    Common advertising data for all Eddystone beacon types.
    """
    message_header1 = (
        0x02,   # Flags length
        0x01,   # Flags data type value
        0x06,   # Flags data

        0x03,   # Service UUID length
        0x03,   # Service UUID data type value
        0xaa,   # 16-bit Eddystone UUID
        0xfe,   # 16-bit Eddystone UUID
    )

    """
    Common Eddystone advert UUID
    """
    message_header2 = (
        0x16,   # Service Data data type value
        0xaa,   # 16-bit Eddystone UUID
        0xfe,   # 16-bit Eddystone UUID
    )

    """
    Eddystone message types
    """
    MESSAGE_TYPE_UID = 0x00
    MESSAGE_TYPE_URL = 0x10
    MESSAGE_TYPE_TLM = 0x20
    MESSAGE_TYPE_EID = 0x30

    """
    Values for encrypted and unencrypted Telemetry beacons
    """
    TLM_UNENCRYPTED = 0x00
    TLM_ENCRYPTED = 0x01

    def build(self, payload:bytes):
        """
        Common Build function for all Eddystone beacon types

        :param payload (bytes): bytes object containing the payload for
            the beacon
        """
        self.message += Eddystone.message_header1
        self.message.append(len(Eddystone.message_header2) + len(payload))
        self.message += Eddystone.message_header2
        self.message += payload

    def get_beacon(self) -> any:
        """
        Gets the last beacon created.

        :returns: a bytes object containing the data of the last beacon
            created by this object
        """
        return self.message

class Eddystone_UID(Eddystone):
    """
    Create an Eddystone UID format beacon.
    The Eddystone-UID frame broadcasts an opaque, unique 16-byte Beacon
    ID composed of a 10-byte namespace and a 6-byte instance / beacon ID.
    """
    def __init__(self, namespace_id:any, beacon_id:any, ranging_data:int):
        """
        Build an Eddystone UID beacon from the given values.

        :param namesapce_id (any): A bytes object containing 10 bytes of
            namespace data. This can be used to filter beacons to a
            coarse location.
        :param beacon_id (any): A bytes object containing 6 bytes of
            beacon ID data. This can be used to locate beacons to a
            finer resolution.
        :param ranging_data (int): a signed byte indicating the tx power
            at 0m in 1 db steps.
            This can be calculated by measuting the Tx power at 1m and
            adding 41dBm, 41dBm being the signal loss over 1m.
            Valid values must be between -100 to 20 inclusive
        """
        if len(namespace_id) != 10:
            raise Exception("Namespace id must be 10 bytes in length")
        if len(beacon_id) != 6:
            raise Exception("Beacon id must be 6 bytes in length")
        if ranging_data > 20 or ranging_data < -100:
            raise Exception("Ranging data must be in range")

        self.message = []
        payload = []
        payload.append(Eddystone.MESSAGE_TYPE_UID)
        payload.append(ranging_data)
        payload += (namespace_id)
        payload += (beacon_id)
        self.build(payload)


class Eddystone_URL(Eddystone):
    """
    Create an Eddystone URL format beacon
    The Eddystone-URL frame broadcasts a URL using a compressed encoding
    format in order to fit more within the limited advertisement packet.
    """

    """
    List of supported URL header schemes
    """
    schemes = [
        "http://www.",
        "https://www.",
        "http://",
        "https://",
    ]

    """
    List of suported URL extensions
    """
    extensions = [
        ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
        ".com", ".org", ".edu", ".net", ".info", ".biz", ".gov",
    ]


    def __init__(self, url:str, ranging_data:int):
        """
        Build an Eddystone URL beacon from the given values.

        :param url (str): A string containing a compatible URL
        :param ranging_data (int): a signed byte indicating the tx power
            at 0m in 1 db steps.
            This can be calculated by measuring the Tx power at 1m and
            adding 41dBm, 41dBm being the signal loss over 1m.
            Valid values must be between -100 to 20 inclusive
        """
        if ranging_data > 20 or ranging_data < -100:
            raise Exception("Ranging data must be in range")

        self.message = []
        payload = []
        payload.append(Eddystone.MESSAGE_TYPE_URL)
        payload.append(ranging_data)
        encoded_url = Eddystone_URL.__encode_url(url)
        payload += encoded_url
        self.build(payload)

    def __encode_url(url):
        """
        'Private' function to encode a url.

        :param url (str): The url to encode
        """
        i = 0
        data = []

        for s in range(len(Eddystone_URL.schemes)):
            scheme = Eddystone_URL.schemes[s]
            if url.startswith(scheme):
                data.append(s)
                i += len(scheme)
                break
        else:
            raise Exception("Invalid url scheme")

        while i < len(url):
            if url[i] == '.':
                for e in range(len(Eddystone_URL.extensions)):
                    expansion = Eddystone_URL.extensions[e]
                    if url.startswith(expansion, i):
                        data.append(e)
                        i += len(expansion)
                        break
                else:
                    data.append(0x2E)
                    i += 1
            else:
                data.append(ord(url[i]))
                i += 1

        return data

class Eddystone_TLM(Eddystone):
    """
    Create an Eddystone TLM format beacon
    Eddystone beacons may transmit data about their own operation to
    clients. This data is called telemetry and is useful for monitoring
    the health and operation of a fleet of beacons.
    Since the Eddystone-TLM frame does not contain a beacon ID, it must
    be paired with an identifying frame which provides the ID, either of
    type Eddystone-UID or Eddystone-URL.
    """
    def __init__(self, encrypted:bool, battery: int, temperature:int):
        """
        Build an Eddystone TLM beacon from the given values.

        :param encrypted (bool): Currently only unencrypted (False) beacons
            are supported as there is no crypto library available yet.
        :param battery (int): An integer containing the battery voltage in
            mv steps i.e 3.3v is represented as 3300.
            If not supported (for example in a USB-powered beacon) the value
            should be zeroed.
        :param temperature (int) The temperature in degrees Celsius sensed
            by the beacon and expressed in a signed 8.8 fixed-point notation.
            If not supported the value should be set to 0x8000, -128 °C.
        """
        self.encryption = encrypted
        self.advertising_pdu_count = 0
        self.__build_TLM(battery, temperature)

    def update(self, battery, temperature):
        """
        Update the battery and temperature values in a TLM beacon

        :param battery (int): An integer containing the battery voltage in
            mv steps i.e 3.3v is represented as 3300.
            If not supported (for example in a USB-powered beacon) the value
            should be zeroed.
        :param temperature (int) The temperature in degrees Celsius sensed
            by the beacon and expressed in a signed 8.8 fixed-point notation.
            If not supported the value should be set to 0x8000, -128 °C.
        """
        self.advertising_pdu_count += 1

        self.__build_TLM(battery, temperature)

    def __build_TLM(self, battery:int, temperature:int):
        """
        Private function used to build the TLM payload

        :param battery (int): An integer containing the battery voltage in
            mv steps i.e 3.3v is represented as 3300.
            If not supported (for example in a USB-powered beacon) the value
            should be zeroed.
        :param temperature (int) The temperature in degrees Celsius sensed
            by the beacon and expressed in a signed 8.8 fixed-point notation.
            If not supported the value should be set to 0x8000, -128 °C.

        """
        if battery > 0xffff:
            raise Exception("Battery voltage out of range")
        if temperature > 32767 or temperature < -32768:
            raise Exception("Temperature out of range")

        self.message = []
        payload = []
        payload.append(Eddystone.MESSAGE_TYPE_TLM)

        if(self.encryption):
            payload.append(Eddystone.TLM_ENCRYPTED)
            raise Exception("Encrypted TLM beacons not supported")
        else:
            payload.append(Eddystone.TLM_UNENCRYPTED)

        self.second_count = time.ticks_ms() // 100

        payload.append((battery & 0xff00) >> 8)
        payload.append(battery & 0xff)

        payload.append(temperature & 0x00ff)
        payload.append((temperature & 0xff00) >> 8)

        payload.append((self.advertising_pdu_count & 0xff000000) >> 24)
        payload.append((self.advertising_pdu_count & 0x00ff0000) >> 16)
        payload.append((self.advertising_pdu_count & 0x0000ff00) >> 8)
        payload.append((self.advertising_pdu_count & 0x000000ff))

        payload.append((self.second_count & 0xff000000) >> 24)
        payload.append((self.second_count & 0x00ff0000) >> 16)
        payload.append((self.second_count & 0x0000ff00) >> 8)
        payload.append((self.second_count & 0x000000ff))
        self.build(payload)

class Eddystone_EID(Eddystone):
    """
    Create an Ephemeral ID (EID) beacon
    The Eddystone-EID frame broadcasts an encrypted ephemeral identifier
    that changes periodically at a rate determined during the initial
    registration with a web service. The broadcast ephemeral ID can be
    resolved remotely by the service with which it was registered, but
    to other observers appears to be changing randomly. This frame type
    is intended for use in security and privacy-enhanced devices.

    Note: This is currently only supported via user defined data as
        no crypto libary is currently available.
    """
    def __init__(self, eid:any, ranging_data:int):
        """
        Build an Eddystone EID beacon from the given values.

        :param eid (str): A byte object containing the precomputed EID
            beacon data. Note this data is not constant.
        :param ranging_data (int): a signed byte indicating the tx power
            at 0m in 1 db steps.
            This can be calculated by measuting the Tx power at 1m and
            adding 41dBm, 41dBm being the signal loss over 1m.
            Valid values must be between -100 to 20 inclusive
        """
        if len(eid) != 8:
            raise Exception("EID must be 8 bytes in length")
        if ranging_data > 20 or ranging_data < -100:
            raise Exception("Ranging data must be in range")

        self.ranging_data = ranging_data
        self.__build_eid(eid)

    def update(self, eid:any):
        """
        Update an existing EID beacon

        :param eid (str): A byte object containing the precomputed EID
            beacon data. Note this data is not constant.
        """
        if len(eid) != 8:
            raise Exception("EID must be 8 bytes in length")

        self.__build_eid(eid)

    def __build_eid(self, eid):
        """
        Private function to build the EID beacon

        :param eid (str): A byte object containing the precomputed EID
            beacon data. Note this data is not constant.
        """
        self.message = []
        payload = []
        payload.append(Eddystone.MESSAGE_TYPE_EID)
        payload.append(self.ranging_data)
        payload += (eid)
        self.build(payload)
