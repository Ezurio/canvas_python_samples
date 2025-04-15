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
