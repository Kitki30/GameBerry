import machine
import time
def blink(blinks, delay):
    led = machine.Pin("LED", machine.Pin.OUT)
    i = 0
    while i is not blinks:
        led.off()
        time.sleep(delay /2)
        led.on()
        time.sleep(delay /2)
        i = i + 1
