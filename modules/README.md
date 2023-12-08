# Python Modules

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

# Canvas Python Modules
Canvas Python is capable of using the above module paradigm, the module must exist in the device's file system, this is easily done using XBits drag and drop facility and that's it! After the module file has been placed on the device it can be imported into your python script as above.
To get things started therre are currently 2 modules available.

### Beacons
- This module provides support for iBeacons, AltBeacons and Eddystone Beacons.

### Click_Boards
- This module provides support for TempAndHum 4 and 18 click boards. The module also provides automatic switching for float and integer results based on the module capabilities. This can easily be manually changed if int support is wanted on a float capable platform.

