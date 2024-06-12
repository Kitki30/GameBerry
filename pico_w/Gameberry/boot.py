from machine import UART, Pin
import uos

# Run terminal on UART0
uart = UART(0, 115200)
uos.dupterm(uart)

