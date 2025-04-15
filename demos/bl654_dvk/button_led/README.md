# BL654 DVK Button LED Demo
This repository contains a Python script intended for use on the BL654 DVK board to demonstrate use of pushbutton switches and LEDs. Button Press events are configured to trigger a callback function which then toggles one of four LEDs on the BL654 DVK board.

## Loading Canvas Firmware onto the BL654 DVK
The BL654 DVK board must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware). You can load this firmware (.hex file) using the [nRF Connect Desktop](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-desktop) programmer application.

Once Canvas Firmware is loaded, you can use [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc) to load Python scripts. You will need to attach two micro-USB cables to your workstation, one each to both the ports labeled USB2 (Atmel USB) and USB3 (nRF USB) on the silk screen.

### Loading the <span>button_led.py</span> script
Once the board is attached, from within Xbit VS Code, you should see a serial port displayed in the USB DEVICES panel corresponding to your BL654 DVK board with a `>>>` icon. You can drag and drop Python script files from your operating system's file explorer window to the device entry in the `USB DEVICES` panel to copy it to the device's file system. Once copied to the device, rename this file to `main.py` by right-clicking the file within VS Code and selecting `Rename File`. Reset the BL654 DVK to begin running the script (e.g., click the Reset button under `Tools` in Xbit VS Code or press the physical RESET button on the BL654 DVK board).

## Intended Use
Once the BL654 DVK has been programmed with Canvas Firwmare and the Python script in this repository (making sure to rename `button_led.py` to `main.py` so the script runs at boot), the BL654 DVK board will respond to pressing one of the four buttons near the center of the board (labeled BUTTON1, BUTTON2, BUTTON3 and BUTTON4) by toggling a corresponding LED (D1, D2, D3, D4).
