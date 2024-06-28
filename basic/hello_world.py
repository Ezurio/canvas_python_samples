#
# hello_world.py
#
# This sample prints a message to the console in a loop.
#
# To use this sample, connect to your device using Xbit tools for VS Code
# (https://marketplace.visualstudio.com/items?itemName=rfp-canvas.xbit-vsc)
# and save the content of this file as 'hello_world.py' to the device.
# Click the device name in the USB DEVICES panel to open a TERMINAL providing
# access to the REPL serial port of your device. Press 'Enter' in the TERMINAL
# tab and ensure you see the '>>>' prompt. You can run the 'hello_world.py'
# script by typing 'import hello_world'. The hello message will print 20 times.
#
# NOTE: Because of how the Python import statement works, you will need to
# reset the device if you would like to run the script again.
#
str = "Hello, world!"
counter = 0
while counter < 20:
    print(str,  counter)
    counter += 1
