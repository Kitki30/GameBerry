import modules.ina219
import modules.RGB1602 as l
import time
from machine import I2C, Pin

lcd = l.RGB1602(16,2)
i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)
SHUNT_OHMS = 0.1
ina = modules.ina219.INA219(SHUNT_OHMS, i2c)
while True:
    lcd.setCursor(0,0)
    lcd.printout(str(ina.current()))
    lcd.setCursor(0,1)
    lcd.printout(str(ina.bus_voltage()))
    time.sleep(0.1)