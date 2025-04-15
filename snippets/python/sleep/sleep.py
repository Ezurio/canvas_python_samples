# Demonstrates use of the time module's sleep function to pause execution
# for a specified number of seconds.
import time

print("Execution will pause for 3 seconds...")
time.sleep(3)  # Pause execution for 3 seconds
print("Execution resumed after 3 seconds.")

# time.delay_ms can be used to pause for a number of milliseconds
print("Execution will pause for 500 milliseconds...")
time.sleep_ms(500)  # Pause execution for 500 milliseconds (0.5 seconds)
print("Execution resumed after 500 milliseconds.")

