# Basic Examples.


## Overview.
Some very simple python examples


## Description
### hello_world.py
- Prints 'hello world' followed by an incrementing count 1000 times.

### simple_escalating_sleep.py
- Uses the sleep_ms function to sleep for incrementing periods of time with a print of the time period between.

### timer_callback.py
- Uses the canvas.Timer module to setup a callback that will be called every second. This callback will increment a 'countUp' value in it's event data object and then print the value of the 2 values in the event object ('countUp' and 'countDown')
- A loop that ticks at a faster 250ms decrements the event data value 'countDown' and also prints the 2 event data values.
- Once the 'countDown' value reaches zero the loop is terminated and the timer is stopped.


## Other Requirements
None
