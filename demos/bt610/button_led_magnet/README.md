# Sentrius BT610 Button, LED and Magnet Demo
This is a simple application intended for use on the Sentrius BT610 sensor to demonstrate use of the pushbutton the buttons, LEDs and open/close magnetic sensor. Button Press events are configured to trigger a callback function which then toggles the on-board LED.

## Loading onto the Sentrius BT610 Sensor
The Sentrius BT610 Sensor must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware). You can load this firmware (.hex file) using the [nRF Connect Desktop](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-desktop) programmer application. You will need an appropriate SWD programming adapter such as the [USB-SWD Programming Kit](https://www.ezurio.com/wireless-modules/programming-kits/usb-swd-programming-kit) or a Segger J-Link adapter.

Once Canvas Firmware is loaded, you can use [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc) to load Python scripts. You will need to attach an FTDI USB-UART cable from your workstation to the J1 header on the Sentrius BT610 board to access the Python REPL.

### <span>button_led_magnet.py</span>
Rename this file to `main.py` and load onto the Sentrius BT610 sensor.

### Loading the <span>button_led_magnet.py</span> script
Once the sensor is attached via FTDI UART cable, from within Xbit VS Code, you should see a serial port displayed in the USB DEVICES panel corresponding to your sensor with a `>>>` icon. You can drag and drop Python script files from your operating system's file explorer window to the device entry in the `USB DEVICES` panel to copy it to the device's file system. Once copied to the device, rename this file to `main.py` by right-clicking the file within VS Code and selecting `Rename File`. Reset the BT610 sensor to begin running the script (e.g., click the Reset button under `Tools` in Xbit VS Code or press the physical RESET button on the BT610 sensor board).

## Intended Use
Once the Sentrius BT610 sensor has been programmed with Canvas Firwmare and the Python script in this repository (making sure to rename `button_led_magnet.py` to `main.py` so the script runs at boot), pressing either SW2 (boot button) or SW3 (tamper button) will toggle the red LED. Putting a magnet near the mag switch will turn on the green LED (and turn it off when removed). Each one also prints out the current GPIO state to the REPL. Digital Input 1 is also being monitored and will display a message when the state of the pin goes from low to high or high to low.
