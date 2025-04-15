# Canvas Python Sample Repository
## Starter Projects
This directory contains starter projects and a library of re-usable Python components designed for developers to start with and build upon for their specific use case. Projects in this directory may depend on other files in the `lib` directory, so keep in mind when developing on a Canvas compatible device to copy over not just the project `.py` files but any referenced `.py` files from the `lib` directory as well.

The starter projects focus on structuring the Python scripts more closely to how a production application would be structured. This means use of Python classes and other modular concepts are preferred in some cases over code readability. Though this may mean the resulting application is more complex, there are benefits to modular and re-usable code in terms of maintenance and upgradeability of separate components. Each starter project provides one (or several related) `.py` Python script files that can be directly installed to a device running Canvas firmware using the Xbit tools for VS Code extension. Projects may also reference other `.py` modules/files located in the `lib` directory (NOTE: these files must also be copied to the device filesystem in order for the starter project to run properly).

Starter projects will indicate within their `README.md` file which Canvas hardware platforms they are compatible with/designed for. Note that some projects require specific hardware that may not be available on all devices.

## Starter Project Manifest Files
Starter project folders may contain a `project.yml` file called a "manifest file". These manifest files contain information such as the board(s) the project is intended/designed for, listing of any dependencies from the `lib` subdirectory, project metadata and version information.
