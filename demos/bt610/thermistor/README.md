# Sentrius BT610 Sensor Thermistor Read Sample
This sample application demonstrates reading analog voltage input from one or more thermistors (10K) attached to corresponding THx and GND pins. The converted temperature data (degrees Celsius) is broadcast in BLE advertisements for an external device such as a BLE gateway to read and report to a cloud application.

## Loading onto the Sentrius BT610 Sensor
The Sentrius BT610 Sensor must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware). You can load this firmware (.hex file) using the [nRF Connect Desktop](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-desktop) programmer application. You will need an appropriate SWD programming adapter such as the [USB-SWD Programming Kit](https://www.ezurio.com/wireless-modules/programming-kits/usb-swd-programming-kit) or a Segger J-Link adapter.

Once Canvas Firmware is loaded, you can use [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc) to load Python scripts. You will need to attach an FTDI USB-UART cable from your workstation to the J1 header on the Sentrius BT610 board to access the Python REPL.

### thermistor_ble_demo.py
Rename this file to `main.py` and load onto the Sentrius BT610 sensor.

### Loading the thermistor_ble_demo.py script
Once the sensor is attached via FTDI UART cable, from within Xbit VS Code, you should see a serial port displayed in the USB DEVICES panel corresponding to your sensor with a `>>>` icon. You can drag and drop Python script files from your operating system's file explorer window to the device entry in the `USB DEVICES` panel to copy it to the device's file system. Once copied to the device, rename this file to `main.py` by right-clicking the file within VS Code and selecting `Rename File`. Reset the BT610 sensor to begin running the script (e.g., click the Reset button under `Tools` in Xbit VS Code or press the physical RESET button on the BT610 sensor board).

## Intended Use
Once the Sentrius BT610 sensor has been programmed with Canvas Firwmare and the Python script in this repository (making sure to rename `thermistor_ble_demo.py` to `main.py` so the script runs at boot), the sensor will broadcast BLE advertisements containing temperature values from each of the thermistors attached at TH1, TH2, TH3 and TH4 respectively. Read the information displayed on the REPL console on startup for more information about configuring the sensor.

## Configuring TH1 - TH4 Channels for Use
For details on how to attach thermistors to the screw terminals of the BT610, see the [Hardware Configuration and Installation Guide](https://www.ezurio.com/documentation/bt610-hardware-configuration-and-installation-guide).

This demo application uses a configuration file to enable/disable TH1, TH2, TH3 and TH4 channels. To view the current configuration, type "config" at the REPL prompt (>>>).

The configuration dictionary will look something like this:
```{'th1_enabled': 1, 'network_id': 65535, 'th3_enabled': 0, 'th2_enabled': 0, 'reporting_interval_ms': 1000, 'th4_enabled': 0, 'ble_name': 'BT610-TH'}```

The enabled/disabled state of each channel is configured using the values `th1_enabled`, `th2_enabled`, `th3_enabled` and `th4_enabled`. Assigning these config values a value of `0` will disable the corresponding channel, while assigning a value of `1` will enable the channel. This only affects the data reported in the BLE advertisement and may be parsed by tools to determine which channels to display. You can also modify the reporting interval with the `reporting_interval_ms` value and the name broadcast in the BLE advertisements using the `ble_name` value.

To modify a config value, type `config["<dictionary_key_name>"] = <value>`. For example, to enable thermistor channel 3 (TH3), type:

`config["th3_enabled"] = 1`

To save the updated configuration to flash, type:

`save_config()`

## A Note about Calibration
Note this script is for demonstration purposes and therefore uses default values for ADC calibration coefficients (offset error, gain error). For more accurate readings, you may wish to measure the calibration coefficients for your specific BT610 device. The ADC calibration coefficients impact the accuracy of mapping thermistor readings to temperature values. Information about performing an ADC calibration to determine appropriate calibration coefficients for your BT610 can be found in the [Thermistor ADC Calibration](https://www.ezurio.com/documentation/application-note-bt610-thermistor-adc-calibration) application note. Once the values are determined, variables in this script can be updated to improve calculation of temperature from thermistor readings.

## Using other thermistors
The BT610 is designed to use 10k NTC thermistor sensors. If you would like to use a different thermistor from those supplied by Ezurio (133-00719/133-00719B), this [online calculator](https://www.ezurio.com/technology/bt610-thermistor-coefficient-calculator) may be helpful in calculating the Steinhart-Hart coefficients necessary to convert ADC values to temperature values with the BT610. Once determined, these coefficients can be used in the script (update the values specified for THERMISTOR_S_H_A, THERMISTOR_S_H_B and THERMISTOR_S_H_C).
