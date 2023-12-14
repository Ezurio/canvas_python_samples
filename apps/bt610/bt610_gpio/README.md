# Sentrius BT610 GPIO Demo
This repository contains a Python script intended for use on the Sentrius BT610 sensor to demonstrate use of pushbutton switches and LEDs. Button Press events are configured to trigger a callback function which then toggles the on-board LED.

## Loading Canvas Firmware onto the Sentrius BT610 Sensor
The Sentrius BT610 Sensor must be running [Canvas Firmware](https://github.com/LairdCP/Sentrius_BT610_Canvas_Firmware). You can load this firmware (.hex file) using the [nRF Connect Desktop](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-desktop) programmer application. You will need an appropriate SWD programming adapter such as the [USB-SWD Programming Kit](https://www.lairdconnect.com/wireless-modules/programming-kits/usb-swd-programming-kit) or a Segger J-Link adapter.

Once Canvas Firmware is loaded, you can use [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc) to load Python scripts. You will need to attach an FTDI USB-UART cable from your workstation to the J1 header on the Sentrius BT610 board to access the Python REPL.

### Loading the <span>bt610_gpio.py</span> script
Once the sensor is attached, from within Xbit VS Code, you should see a serial port displayed in the USB DEVICES panel corresponding to your sensor with a `>>>` icon. You can drag and drop Python script files from your operating system's file explorer window to the device entry in the `USB DEVICES` panel to copy it to the device's file system. Once copied to the device, rename this file to `main.py` by right-clicking the file within VS Code and selecting `Rename File`. Reset the BT610 sensor to begin running the script (e.g., click the Reset button under `Tools` in Xbit VS Code or press the physical RESET button on the BT610 sensor board).

## Intended Use
Once the Sentrius BT610 sensor has been programmed with Canvas Firwmare and the Python script in this repository (making sure to rename `bt610_gpio.py` to `main.py` so the script runs at boot), pressing either SW2 (boot button) or SW3 (tamper button) will toggle the red LED. Putting a magnet near the mag switch will turn on the green LED (and turn it off when removed). Each one also prints out the current GPIO state to the REPL.
