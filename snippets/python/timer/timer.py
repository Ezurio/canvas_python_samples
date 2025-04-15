# Demonstrates the use of a simple timer to periodically execute a function.
import time
import canvas

def timer_callback(event):
    """Callback function to be called by the timer."""
    print("Timer event triggered with data:", event)
    # You can add more functionality here

# Create a timer that calls the callback function every 2 seconds
timer_interval = 3000  # milliseconds
event_data = "Test event data"  # Optional data to pass to the callback
periodic = True  # Set to True for repeating/periodic execution
timer = canvas.Timer(timer_interval, periodic, timer_callback, event_data)
# Start the timer
timer.start()
# At the REPL, typing `timer.stop()` will stop the timer.

