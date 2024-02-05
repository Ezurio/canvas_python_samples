import time
from net_helper import NetHelper
from sntp import Sntp

# Wait for network to come up
print("Waiting for network")
net = NetHelper(None)
net.wait_for_ready()

# Print the time before the sync
print("Time before sync: {}".format(time.localtime()))

# Sync the time
sntp = Sntp()
sntp.poll()

# Print the time after the sync
print("Time after sync: {}".format(time.localtime()))
