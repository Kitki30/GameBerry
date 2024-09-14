# Hardware controlling script
# By Kitki30
# Made for game devs to controll hardware easier!

import modules.json as json
import ujson

# Read config
gpio_conf = json.read("/system/configs/gpio_config.json")
ina_conf = json.read("/system/configs/ina219_config.json")
device_config = json.read("/device_config.json")

# Buttons
def button_conf():
    return ujson.dumps({"buttons": {"button_1": gpio_conf["buttons"]["button_1"], "button_2": gpio_conf["buttons"]["button_2"], "home": gpio_conf["buttons"]["home"]}})

# Buzzer
def buzzer_conf():
    return gpio_conf["buzzer"]

# LCD
def lcd_sda():
    return gpio_conf["lcd"]["sda"]

def lcd_scl():
    return gpio_conf["lcd"]["scl"]

def lcd_num():
    return gpio_conf["lcd"]["i2c_num"]

# INA219
def ina_sda():
    return gpio_conf["ina"]["sda"]

def ina_scl():
    return gpio_conf["ina"]["scl"]

def ina_num():
    return gpio_conf["ina"]["i2c_num"]

def ina_shunt():
    return ina_conf["shunt_ohms"]

def ina_ena():
    return device_config["INA219"]

# IR Blaster
def ir_ena():
    return device_config["ir"]