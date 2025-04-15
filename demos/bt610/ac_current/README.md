# Sentrius BT610 Sensor ADC Read Sample
This sample application demonstrates use of the AIN1-AIN4 channels to read analog voltage input from attached AC current transducers (5V output, 20A sense) attached to corresponding AINx and GND pins. The current sense data is broadcast in BLE advertisements for an external device such as a BLE gateway to read and report to a cloud application.

This script is compatible with the **BT610 Current Sense Applet** available in the [Xbit Desktop tool](https://github.com/Ezurio/Canvas_Xbit_Desktop) and [Xbit Mobile tool](https://github.com/Ezurio/Canvas_Xbit_Mobile). This Applet can be used to visualize the current sense data from the BLE advertisements in realtime.

## Loading onto the Sentrius BT610 Sensor
The Sentrius BT610 Sensor must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware). You can load this firmware (.hex file) using the [nRF Connect Desktop](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-desktop) programmer application. You will need an appropriate SWD programming adapter such as the [USB-SWD Programming Kit](https://www.ezurio.com/wireless-modules/programming-kits/usb-swd-programming-kit) or a Segger J-Link adapter.

Once Canvas Firmware is loaded, you can use [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc) to load Python scripts. You will need to attach an FTDI USB-UART cable from your workstation to the J1 header on the Sentrius BT610 board to access the Python REPL.

### <span>xbit_bt610_ac_current_20amp.py</span>
Rename this file to `main.py` and load onto the Sentrius BT610 sensor.

### Loading the <span>xbit_bt610_ac_current_20amp.py</span> script
Once the sensor is attached via FTDI UART cable, from within Xbit VS Code, you should see a serial port displayed in the USB DEVICES panel corresponding to your sensor with a `>>>` icon. You can drag and drop Python script files from your operating system's file explorer window to the device entry in the `USB DEVICES` panel to copy it to the device's file system. Once copied to the device, rename this file to `main.py` by right-clicking the file within VS Code and selecting `Rename File`. Reset the BT610 sensor to begin running the script (e.g., click the Reset button under `Tools` in Xbit VS Code or press the physical RESET button on the BT610 sensor board).

## Intended Use
Once the Sentrius BT610 sensor has been programmed with Canvas Firwmare and the Python script in this repository (making sure to rename `xbit_bt610_ac_current_20amp.py` to `main.py` so the script runs at boot), the sensor will broadcast BLE advertisements containing current sense data values from AIN1, AIN2, AIN3 and AIN4. Read the information displayed on the REPL console on startup for more information about configuring the sensor.

## Configuring AIN1 - AIN4 Channels for Use
Note that this application uses a configuration file to enable/disable AIN1, AIN2, AIN3 and AIN4 channels. To view the current configuration, type "config" at the REPL prompt (>>>).

The configuration dictionary will look something like this:
```{'ain1_enabled': 1, 'network_id': 65535, 'ain3_enabled': 0, 'ain2_enabled': 0, 'reporting_interval_ms': 1000, 'ain4_enabled': 0, 'ble_name': 'BT610'}```

The enabled/disabled state of each channel is configured using the values `ain1_enabled`, `ain2_enabled`, `ain3_enabled` and `ain4_enabled` respectively. Assigning these config values a value of `0` will disable the channel, while assigning a value of `1` will enable the channel. This only affects the data reported in the BLE advertisement and is parsed by tools such as the Xbit BT610 Current Sense Applet. You can also modify the reporting interval with the `reporting_interval_ms` value and the name broadcast in the BLE advertisements using the `ble_name` value.

To modify a config value, type `config["<dictionary_key_name>"] = <value>`. For example, to enable analog channel 3, type:

`config["ain3_enabled"] = 1`

To save the updated configuration to flash, type:

`save_config()`
