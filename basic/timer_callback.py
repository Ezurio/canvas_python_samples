import time
import canvas

print("Timer callback example")

# Python callback outputs the event data string and count
def timer_callback(event):
    event["countUp"] = event["countUp"] +1
    print("String: %s CountDown: %d" %(event["string"],  event["countDown"]))
    print("CountUp: %d" %(event["countUp"]))

# Initialise event data
event_data = {"string":"Test String",
              "countUp": 0,
              "countDown": 40}
print(event_data["string"])
print(event_data["countUp"])
print(event_data["countDown"])

# Initialise the timer to fire evert second, be repeating and have event data
timer = canvas.Timer(1000, True, timer_callback, event_data)

# Start the timer
timer.start()

# Loop for 40 itterations
while (event_data["countDown"] > 0):
    # Update the count
    event_data["countDown"] = event_data["countDown"] - 1
    print("MainLoop countUp: ", event_data["countUp"])
    # Sleep for 250ms
    time.sleep_ms(250)

# Stop the timer
timer.stop()

# Delete the timer and all resources.
del(timer)

# Finished
print("Finished")
