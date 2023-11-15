# TempAndHum Module
The TempAndHum module is designed to provide expandable support for the TempAndHum series of MikroE Click boards.
At present this support is limited to TempAndHum4 and TempAndHum18 click boards.

## Setup
The Module actually comprises 3 files. The main TempAndHumClick.py module file and 2 'plugable' format files, TempAndHumFloat.py and TempAndHumInt.py.
The format files allow the results of temperature or humidity queries to be returned in either float or int formats according to platform.

## Copy files
The required module files must be copied onto the device, int and float format files can co-exist on the device or a single format file can be transferred if you know ahead of time which you need.

## Usage
Both TempAndHum boards are utilised in the same way as they use the I2C control interface.
An instance object is instanciated with an input of the control interface description (SCL, SDA, (optional)Address control, (optional)Address), the object returned is then used to setup, control and query the device.

## temp_and_hum_click_simple.py Example.
This is a simple example of how to setup and use the module. The example has the following functionality.
- Create a TempAndHumClick18 object.
- Set the resolution of the device
- Get any device ID information
- Get temperature in C
- Get the status of the previous operation.
- Get the relative humidity
- Get the status of the previous operation.
- Get the temperature in F
- Get the status of the previous operation.
- Get the Temperature in C AND the relative humidity at the same time
- Get the status of the previous operation.
- Get the Temperature in F AND the relative humidity at the same time
- Get the status of the previous operation.

The example will automatically detect which Canvas board you are using (Lyra24 or 'non Lyra24') and adjust the interface specifications accordingly. The Module will also, as stated, auto detect the platform and determine the need for int or float formatting. If Int formatting is required on a float capable module it is possible to remove the autodetection and explicity use a particular format module. See the comments in TempAndHumClick.py