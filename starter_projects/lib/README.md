# Canvas Python Sample Repository
## Library
This directory contains a library of re-usable components designed for use with the starter projects. The subfolders in this directory define "modules" of functionality to assist in building out a larger Python-based application. Each module provides one (or several related) `.py` Python script files that can be copied to a device running Canvas firmware using the Xbit tools for VS Code extension.

Modules will indicate within their `README.md` file which Canvas hardware platforms they are compatible with/designed for. Note that some modules require specific hardware that may not be available on all devices.

## Python Modules

In Python, a module is a file containing Python definitions and statements. The file name is the module name with the suffix `.py`. For example, if you have a file named `my_module.py`, you can import it in another Python script using the `import` statement:

```python
import my_module
```

Once you've imported a module, you can access its functions, classes, and variables using dot notation. For example, if `my_module` contains a function named `my_function`, you can call it like this:

```python
my_module.my_function()
```

You can also import specific functions or variables from a module using the `from` keyword. For example, if `my_module` contains a function named `my_function` and a variable named `my_variable`, you can import them like this:

```python
from my_module import my_function, my_variable
```

This allows you to use the imported functions and variables directly in your code without having to prefix them with the module name.

## Canvas Python Modules
Canvas Python is capable of using the above module paradigm as long as the module exists in the device's file system. This is easily accomplished using the Xbit VS Code extension "drag and drop" feature. After the module files have been placed on the device, a module can be imported into your python script as described above.
