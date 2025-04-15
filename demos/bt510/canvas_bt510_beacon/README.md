# Canvas BT510 "Beacon" Containing All Sensor Data
This demo configures each of the sensors on the BT510 and configures BLE advertisements containing the sensor data. The `app.py` file may be edited to adjust the data update interval and advertising interval based on the required battery lifetime for a specific use case.

Periodic advertisements are configured containing a manufacturer-specific data element with the status of the various sensors on the BT510. The data element payload structure contains companyId, followed by a 2 byte protocolId. In this case, the protocolId is set to [0xC9, 0x00] to match that of the “tilt sensor demo”, with some additional fields concatenated beyond accelerometer axis data containing other sensor data.

## Advertising Format
```
    Canvas BT510 beacon format:                           battery voltage (mv)
                                             raw temperature sensor bytes    |
                                                          status flags  |    |
                                             8-bit sequence counter  |  |    |
                                            accelx/y/z            |  |  |    |
                 name                  protocolId    |            |  |  |    |
   ble flags        |              companyId    |    |            |  |  |    |
     [-----|-] [----|--------------] [-----|----|----|------------|--|--|----|--]
     02 01 06 09 09 4254352d43343641 11 ff 7700 c900 xxxxyyyyzzzz ss gg tttt vvvv
```

### protocolId byte format:

* 2 bytes, 0xC9 0x00

### accelx/y/z byte format:

* 2 bytes signed 16-bit x axis value

* 2 bytes signed 16-bit y axis value

* 2 bytes signed 16-bit z axis value

### 8-bit sequence counter byte format:

* unsigned 8 bit counter, increments each time data is updated. Rolls over from 0xff to 0x00

### status flags byte format:

* bit 0x01: battery ok flag (0: Low, 1: OK)

* bit 0x02: magnet sensor state (0: Open, 1: Close)

* bit 0x04: button state (0: Not Pressed, 1: Pressed)

### raw temperature sensor bytes byte format:

* Use formula from si705x datasheet to convert sample to temperature value in Celsius

* Temperature (°C) = ((175.72*Temp_Code)/65536) - 46.85 where Temp_Code is the 16 bit value from the advertisement in big endian byte order.

### battery voltage (mv) byte format:

* 2 byte unsigned 16-bit value (big-endian byte order): battery voltage read by ADC in millivolts
