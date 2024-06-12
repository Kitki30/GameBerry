import ntptime

def sync(wlan):
    try:
        while not wlan.isconnected():
            pass
        ntptime.settime()
    except:
        print("Error")

