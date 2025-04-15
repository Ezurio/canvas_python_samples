# ![Canvas Logo](starter_projects/resources/img/canvas_logo.png)

### Python Application Development for Embedded Wireless Products

**Canvas Software Suite** is Ezurio's embedded microcontroller-based software platform enabling Python application development to speed scaling from PoC to production.

Write embedded applications in Python without setting up complex SDKs or time-consuming build steps. Python support is based on the [MicroPython](https://github.com/micropython/micropython) engine.

### Canvas Software Suite Samples Repository

This repository contains three categories of Python-based sample scripts, targeting different goals during the hardware evaluation and development process. The **Demos** provide an easy way to quickly evaluate hardware functionality, whereas the **Snippets** help show minimal, focused examples of how to use specific Canvas APIs. The **Starter Projects** are designed as a starting point for developers to build their own applications on top of.

#### DEMOS

The `/demos` directory contains complete Python-based applications, purpose built to demonstrate a specific use case with Canvas compatible hardware. These demo applications are distributed as pre-packaged `.zip` files that can be installed by simply renaming the file to `update.zip`, copying the file over to the `update` folder on the Canvas device and rebooting the device. These demos are less intended as a starting point for developers to build larger applications upon and more to provide a quick way to demonstrate complex hardware capabilities without having to develop any code.

#### SNIPPETS

The `/snippets` directory contains intentionally brief scripts focused on highlighting a specific API or set of APIs to accomplish a single goal such as controlling an I/O pin or joining a network. These scripts do run on compatible hardware, however the scope is intentionally kept very focused to help developers learn APIs and get basic hardware functionality up and running quickly without alot of code.

#### STARTER PROJECTS

The `/starter_projects` directory contains both a library (`lib` folder) of re-usable Python components and a list of starter projects (`projects` directory) designed as a starting point for developers to build out a more complex Python-based application to meet their use case. Each starter project may have dependencies on one or more Python module found in the `lib` directory, so make sure when copying starter project `.py` files to a Canvas device to also include all files referenced from modules in the `lib` directory. To aid with this, each starter project contains a `project.yml` file specifying the board files the project is intended/designed for, a listing of any dependencies from the `lib` subdirectory, project metadata and version information.
