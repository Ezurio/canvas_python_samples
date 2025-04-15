# Canvas Python Sample Repository
## Demos
This directory contains fully functional applications targeted at quickly demonstrating specific use cases with Canavs compatible hardware products.

Demo applications indicate within their `README.md` file which Canvas hardware platforms they are compatible with/designed for. Note that some demo applications require specific hardware that may not be available on all devices.

## Installing a Demo Application from source
Each demo application directory contains a `src` subdirectory where the source Python (`.py`) script files and other resources necessary to run the demo are located. Follow the instructions in the corresponding `README.md` file found in the demo application subfolder for details on what hardware the demo is designed for and how to install and run the demo application.

## Installing a Demo Application via an installer .zip package
Some demo applications also provide a packaged `.zip` file that can be directly installed to a compatible device running Canvas firmware. To install the Python application, rename the application's `.zip` file to `update.zip`, copy the `update.zip` file to the `update` directory in the device's filesystem, and finally trigger a RESET of the device (e.g., press the RESET button or send Ctrl+d to the REPL terminal). The Canvas firmware will recognize the `update.zip` file in the `update` directory and automatically extract, install and run the new application.
