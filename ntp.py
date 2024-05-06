import machine
import network
import ntptime
import secrets

def sync(wlan):
    while not wlan.isconnected():
        pass
    rtc = machine.RTC()
    ntptime.settime()

