import RPi.GPIO as GPIO
import time

# Configure the GPIO pins
GPIO.setmode(GPIO.BCM)
receive_pin1 = 17
receive_pin2 = 27
GPIO.setup(receive_pin1, GPIO.IN)
GPIO.setup(receive_pin2, GPIO.IN)

# Example: Read the pin states
while True:
    pin_state1 = GPIO.input(receive_pin1)
    pin_state2 = GPIO.input(receive_pin2)
    print(f'Pin 17 state: {pin_state1}, Pin 27 state: {pin_state2}')
    time.sleep(0.1)
