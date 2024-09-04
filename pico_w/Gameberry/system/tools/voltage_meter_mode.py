import modules.ina219
import modules.RGB1602 as l
import time
from machine import I2C, Pin
import system.modules.hardware.hardware as hw

lcd = l.RGB1602(16,2)
i2c = I2C(hw.ina_num(), scl=Pin(hw.ina_scl()), sda=Pin(hw.ina_sda()), freq=100000)
ina = modules.ina219.INA219(hw.ina_shunt(), i2c)
while True:
    lcd.setCursor(0,0)
    lcd.printout(str(ina.current()))
    lcd.setCursor(0,1)
    lcd.printout(str(ina.bus_voltage()))
    time.sleep(0.1)