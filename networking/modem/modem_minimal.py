import canvas_net


def modem_cb(e: tuple):
    print("Modem event: {}".format(e))


modem = canvas_net.Modem(modem_cb)
# Ensure the correct APN is set to get on the network
modem.set_apn("")
# Ensure the right bands are set to get on the network
modem.set_bands("809189F")
# Ensure the right RAT is set to get on the network
modem.set_rat(0)
