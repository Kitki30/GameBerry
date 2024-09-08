import modules.ina219 as ina219
import modules.RGB1602 as RGB1602
from machine import Pin,I2C
import modules.json as json
import time
import modules.math as math
import machine
import network

def calculate_battery_level(V_current, V_min, V_max):
    if V_current < V_min:
        V_min = V_current
        json.write("/system/configs/battery_calibration.json", {"v_max": V_max, "v_min": V_min})
    elif V_current > V_max:
        V_max = V_current
        json.write("/system/configs/battery_calibration.json", {"v_max": V_max, "v_min": V_min})
    battery_level_percent = ((V_current - V_min) / (V_max - V_min)) * 100
    return int(round(battery_level_percent))  