import time

print("Escalating sleep example")
sleep_time = 250

while sleep_time <= 2000:
    print("Time: ", sleep_time)
    time.sleep_ms(sleep_time)
    sleep_time = sleep_time + 250

print("Finished")

