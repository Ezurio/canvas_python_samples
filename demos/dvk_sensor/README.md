# Ezurio DVK Sensor Demo

This application script provides a simple framework for reading sensors attached to an Ezurio DVK board and advertising the data over Bluetooth LE. Sensors are typically connected via mikroBUS or QWIIC interface. Use the Xbit desktop or mobile application to scan for and view advertised data using the "DVK Sensor Monitor" applet.

## BLE Advertising Format:
Sensor data is advertised over BLE within a **Manufacturer Specific Data** element using an extended advertisement packet. The general structure of the packet is a fixed section containing `company id`, `protocol id`, `counter`, `millivolts`, `button flags` and `led flags`, followed by zero or more optional Tag/Value segments defined by the sensors attached to the DVK. Multi-byte fields are encoded in little-endian format.

### Fixed segment at start of payload
|     | company_id | protocol_id | counter | mvolts | button | led |
|----:|:----------:|:-----------:|:-------:|:------:|:------:|:---:|
| Hex:|77 00       |CA 00        |00       |00 00   |00      |00   |
|Type:|uint16      |uint16       |uint8    |uint16  |uint8   |uint8|

### Optional Tag/Value segments for sensors
#### TempHum4 Click Data (mikroBUS)
|     | Sensor Tag/Id | temperature | humidity  |
|:---:|:-------------:|:-----------:|:---------:|
|Hex: |10             |00 00 00 00  |00 00 00 00|
|Type:|uint8          |float32      |float32    |

#### LTR-329 Ambient Light Sensor Data (QWIIC)
|     | Sensor Tag/Id | Visible+IR | IR   |
|:---:|:-------------:|:----------:|:----:|
| Hex:|11             |00 00       |00 00 |
|Type:|uint8          |uint16      |uint16|

## Compatible Hardware

### Supported DVK boards
- [BL54L15/BL54L15u DVK](https://www.ezurio.com/product/bl54l15-series-bluetooth-le-80215-4-nfc)
- [Veda SL917 SoC Explorer Board (brd2911a)](https://www.ezurio.com/product/veda-sl917-wi-fi-6-bluetooth-le-5-4-module)
- [Lyra 24 Series Development Kits](https://www.ezurio.com/wireless-modules/bluetooth-modules/bluetooth-5-modules/lyra-24-series-bluetooth-5-modules)

### Supported Sensors
- [TempHum4 Click (I2C Temperature and Humidity sensor)](https://www.mikroe.com/temp-hum-4-click)
- [LTR-329 Light Sensor (I2C Ambient Light sensor)](https://www.adafruit.com/product/5591)

## Xbit Applet for DVK Sensor Monitoring
To view the data from supported sensors attached to a DVK, install and run the [Xbit Desktop](https://github.com/Ezurio/Canvas_Xbit_Desktop) or [Xbit Mobile](https://github.com/Ezurio/Canvas_Xbit_Mobile) application. Navigate to the Applet list and select the **DVK Sensor Monitor** applet to get started. From there, you can scan and select your DVK and monitor sensors on the dashboard with real-time graph updates displaying the data sent over BLE.
