#
# reload.py
#
# This module provides a function to reload a module.
# It is useful when you are working with a module that is being modified
# and you want to reload it without restarting the interpreter.
#
# Usage:
#   import my_module
#   my_module = reload(my_module)
#
import gc
import sys
def reload(mod):
  mod_name = mod.__name__
  del sys.modules[mod_name]
  gc.collect()
  return __import__(mod_name)
