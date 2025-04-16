# Veda SL917 SoC Explorer Button LED Demo
This repository contains a Python script intended for use on the Veda SL917 SoC Explorer board to demonstrate use of pushbutton switches and LEDs. Button Press events are configured to trigger a callback function which then toggles LEDs on the SoC Explorer board.

## Loading Canvas Firmware onto the Veda SL917 SoC Explorer Board
The Veda SL917 SoC Explorer board must be running [Canvas Firmware](https://github.com/Ezurio/canvas_python_firmware). You can load this firmware (.rps file) using the [Simplicity Commander](https://www.silabs.com/developer-tools/simplicity-studio/simplicity-commander) application.

Once Canvas Firmware is loaded, you can use [Xbit tools for VS Code](https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc) to load Python scripts. You will need to attach the Veda SL917 SoC Explorer board to your workstation using a USB-C cable.

### Loading the <span>button_led.py</span> script
Once the board is attached, from within Xbit VS Code, you should see a serial port displayed in the USB DEVICES panel corresponding to your Veda SL917 SoC Explorer board with a `>>>` icon. You can drag and drop Python script files from your operating system's file explorer window to the device entry in the `USB DEVICES` panel to copy it to the device's file system. Once copied to the device, rename this file to `main.py` by right-clicking the file within VS Code and selecting `Rename File`. Reset the Veda SL917 SoC Explorer board to begin running the script (e.g., click the Reset button under `Tools` in Xbit VS Code or press the physical RESET button on the Veda SL917 SoC Explorer board).

## Intended Use
Once the Veda SL917 SoC Explorer board has been programmed with Canvas Firwmare and the Python script in this repository (making sure to rename `button_led.py` to `main.py` so the script runs at boot), the Veda SL917 SoC Explorer board will respond to pressing one of the two buttons (labeled BTN0 and BTN1) by toggling a corresponding LED (LED0 and LED1).
