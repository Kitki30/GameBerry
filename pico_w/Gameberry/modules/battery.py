import modules.ina219 as ina219
import modules.RGB1602 as RGB1602
from machine import Pin,I2C
import modules.json as json
import time
import modules.math as math
import machine
import network

def calculate_battery_level(V_current, V_min, V_max):
    # Ensure the current voltage is within the expected range
    if V_current < V_min:
        V_current = V_min
    elif V_current > V_max:
        V_current = V_max
    
    # Calculate the battery level as a percentage
    battery_level_percent = ((V_current - V_min) / (V_max - V_min)) * 100
    return int(round(battery_level_percent))  # Round to the nearest whole number

def calculate_discharge_time(capacity_mAh, discharge_current_mA):
    discharge_current_mA = abs(discharge_current_mA)
    if discharge_current_mA <= 0:
        raise ValueError("Discharge current must be greater than zero.")
    
    discharge_time_hours = capacity_mAh / discharge_current_mA
    return discharge_time_hours

def calibrate():
    battery = json.read("/system/user/settings.json")
    capacity = battery["Battery"]["capacity"]
    charge_max_V = 0.0
    charge_min_V = 0.0
    button1 = Pin(3, Pin.IN, Pin.PULL_UP) # First button (GPIO3)
    button2 = Pin(2, Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
    home = Pin(15, Pin.IN, Pin.PULL_UP) # Home button (GPIO15)
    lcd = RGB1602.RGB1602(16,2)
    lcd.setCursor(0,0)
    i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)
    SHUNT_OHMS = 0.1
    ina = ina219.INA219(SHUNT_OHMS, i2c)
    lcd.printout("Charge battery t")
    lcd.setCursor(0,1)
    lcd.printout("o max click home")
    while home.value() == 1:
        time.sleep(.05)
    if math.is_positive(ina.current()) == True:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("Error: Charger")
        lcd.setCursor(0,0)
        lcd.printout("is connected!")
        time.sleep(5)
        machine.soft_reset()
    charge_max_V = round(ina.bus_voltage(), 2)
    json.write("/battery_calibration.json", { "max_V": charge_max_V, "min_V": charge_min_V, "calibration_in_progress": True })
    lcd.clear()
    lcd.setRGB(255,255,255)
    lcd.setCursor(0,0)
    lcd.printout("Discharging")
    lcd.setCursor(0,1)
    lcd.printout("Don't charge")
    i = 0
    fileWrite = 1
    print("Calibration")
    print("Capacity read: "+str(capacity)+"mah")
    print("Max voltage: "+str(charge_max_V) +"V")
    print("Activating Wi-Fi module for faster discharge")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    while True:
        i = i + 1
        if i == 1000000 / 2:
            wlan.scan()
        if i == 1000000:
            charge_min_V = round(ina.bus_voltage(), 2)
            if fileWrite == 1: # Write to two files to avoid corruption of config on battery power loss
                json.write("/battery_calibration.json", { "max_V": charge_max_V, "min_V": charge_min_V, "calibration_in_progress": True })
                fileWrite = 2
            else:
                json.write("/battery_calibration2.json", { "max_V": charge_max_V, "min_V": charge_min_V, "calibration_in_progress": True })
                fileWrite = 1
            lcd.clear()
            lcd.setRGB(255,255,255)
            lcd.setCursor(0,0)
            lcd.printout("Calibration...")
            lcd.setCursor(0,1)
            lcd.printout("ETA: "+ str(round(calculate_discharge_time(capacity, ina.current()), 1))+"h")
            print("ETA: "+ str(round(calculate_discharge_time(capacity, ina.current()), 1))+"h")
            print("Battery voltage: "+str(round(ina.bus_voltage(), 2)) + "V")
            print("Current: "+str(ina.current())+"mA")
            print("Power: "+str(ina.power())+"mW")
            i = 0