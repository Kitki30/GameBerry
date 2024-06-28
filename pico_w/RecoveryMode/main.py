from gpiozero import LED, Button
from time import sleep

# Define the GPIO pins
receive_pin1 = 17
receive_pin2 = 27

# Set up the pins
button1 = Button(receive_pin1)
button2 = Button(receive_pin2)

try:
    # Read the pin states
    while True:
        pin_state1 = button1.is_pressed
        pin_state2 = button2.is_pressed
        print(f'Pin 17 state: {pin_state1}, Pin 27 state: {pin_state2}')
        sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
