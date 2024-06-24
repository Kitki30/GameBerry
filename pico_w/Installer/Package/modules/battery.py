import machine

vbus_pin = machine.Pin(24, machine.Pin.IN)

def is_usb_powered():
    return vbus_pin.value()

