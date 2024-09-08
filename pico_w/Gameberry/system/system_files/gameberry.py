import modules.RGB1602 as RGB1602
import modules.ina219 as ina219
import uos
import modules.json as json
import utime as time, utime
from machine import Pin, PWM, I2C
import machine
import network
import modules.files as files
import modules.ntp as ntp
import gc
import modules.customExceptions as exceptions
import modules.translations as translation
import modules.requests as requests
import system.modules.hardware.hardware as hw
import system.modules.eggs as eggs
import modules.battery as bat

events_working = False
runEvents = True
event_ok = 0

ina_vol_meter = None

if hw.ina_ena() == True:
    i2c = I2C(hw.ina_num(), scl=Pin(hw.ina_scl()), sda=Pin(hw.ina_sda()), freq=100000)
    ina_vol_meter = modules.ina219.INA219(hw.ina_shunt(), i2c)

gc.collect()


# Initialize buttons
# Read button config
button_conf = hw.button_conf()
button1 = Pin(button_conf["buttons"]["button_1"], Pin.IN, Pin.PULL_UP) # First button (GPIO3)
button2 = Pin(button_conf["buttons"]["button_2"], Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
home = Pin(button_conf["buttons"]["home"], Pin.IN, Pin.PULL_UP) # Home button (GPIO15)
button1state = 1
button2state = 1
homestate = 1

bat_calibration = json.read("/system/configs/battery_calibration.json")

version_info = json.read("/system/info/version_info.json")

version = version_info["version"]

lcd=RGB1602.RGB1602(16,2)
lcd.clear()
if files.exist("/system/user/settings.json"):
    print(translation.get("debugger", "settings_exist")) # Settings exist!
else:
    if files.exist("/system/default/settings_default.json"):
        try:
             files.copy("/system/default/settings_default.json", "/system/user/settings.json")
        except:
            exceptions.ShowErrorScreen_with_code(lcd, "file_copy_error")
            raise exceptions.FileCopyError("Cannot copy /system/default/settings_default.json to /settings.json! Cannot boot!")
    else:
        exceptions.ShowErrorScreen_with_code(lcd, "defaults_error")
        raise exceptions.DefaultsNotFound("Default file /system/default/settings_default.json, not found! Cannot boot!")
data = json.read("/system/user/settings.json")

import modules.time as timezones

translation.load(data["language"])

# Gameberry logo
timeFormatted = utime.localtime(timezones.get_timezoned())
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
print("GameBerry v"+str(version)+"-"+str(version_info["version-stage"])+" for "+ version_info["device"] + " " + translation.get("debugger", "gameberry_on") +" "+ uos.uname().machine) # Gameberry v{version} on {machine name}
print(translation.get("debugger", "machine_freq")+": "+str(machine.freq() / 1000000)+" Mhz") # Machine frequency: {freq}Mhz
print(str(timeFormatted[2])+"."+str(timeFormatted[1])+"."+str(timeFormatted[0])+" "+str(timeFormatted[3])+":"+str(timeFormatted[4])+":"+str(timeFormatted[5]))
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

# RTC Clock
rtc = machine.RTC()


if files.exist("/system/user"):
    print(translation.get("debugger", "user_exist")) # User exist!
else:
    files.create_folder("/system/user")

if files.exist("/system/user/savedata"):
    print(translation.get("debugger", "savedata_exist")) # Savedata exist!
else:
    files.create_folder("/system/user/savedata")



# Start connecting to Wi-Fi
wifiExists = False

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(data.get("Wi-Fi").get("wifi_ssid"), data.get("Wi-Fi").get("wifi_password"))
        
import modules.basicThread
modules.basicThread.start()

# Led blink
print(translation.get("debugger", "waiting_one_second")) # Waiting one second
led = Pin("LED", Pin.OUT)
blinks = 0
while blinks is not 10:
    blinks = blinks + 1
    time.sleep(0.025)
    led.on()
    time.sleep(0.025)
    led.off()
led.on()




# Boot screen
_temp_lcd_brightness = data.get('lcd_brightness')
lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
lcd.printout("GameBerry")
lcd.setCursor(0,1)
lcd.printout("Kitki30")
time.sleep(0.5)
lcd.clear()

"""
    STAT_IDLE -- 0
    STAT_CONNECTING -- 1
    STAT_WRONG_PASSWORD -- -3
    STAT_NO_AP_FOUND -- -2
    STAT_CONNECT_FAIL -- -1
    STAT_GOT_IP -- 3
"""

#  Buzzer (GPIO16)
buzzer = PWM(Pin(hw.buzzer_conf(), Pin.OUT))
buzzer.duty_u16(0)

# Connect to wifi
lcd.setCursor(0,0)
lcd.printout(translation.get("wifi", "connecting_to")) # Connecting to
lcd.setCursor(0,1)
if len(data.get("Wi-Fi").get("wifi_ssid")) > 16:
    lcd.printout("Wi-Fi")
else:
    lcd.printout(data.get("Wi-Fi").get("wifi_ssid"))
wifiChecks = 0
connectBlock = False
while wlan.isconnected() == False and wifiChecks is not 200 and connectBlock == False:
    if wlan.status() == -1:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout(translation.get("global", "error")) # Error
        lcd.setCursor(0,1)
        lcd.printout(translation.get("wifi", "connection_fail")) # Connection Fail
        connectBlock = True
        time.sleep(1)
    elif wlan.status() == -2:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout(translation.get("global", "error")) # Error
        lcd.setCursor(0,1)
        lcd.printout(translation.get("wifi", "ap_not_found")) # AP not found
        connectBlock = True
        time.sleep(1)
    elif wlan.status() == -3:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout(translation.get("global", "error")) # Error
        lcd.setCursor(0,1)
        lcd.printout(translation.get("wifi", "wrong_password")) # Wrong password
        connectBlock = True
        time.sleep(1)
    wifiChecks = wifiChecks + 1
    led.off()
    time.sleep(0.05)
    led.on()
    time.sleep(0.05)
led.on()




# Menu 

# Menu variables
currentMenu = 0

# Main menu
def main():
    global currentMenu
    currentMenu = 0
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    if files.exist("/game/game_info.json"):
        gameInfo = json.read("/game/game_info.json")
        lcd.printout(gameInfo["name"])
    else:
        lcd.printout(translation.get("global", "game")) # Game
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "play_next")) # 1. Play  2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

# Settings menu
def settings():
    global currentMenu
    currentMenu = 1
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("global", "settings")) # Settings
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK    2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

# Exit
def exit():
    global currentMenu
    currentMenu = 2
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("global", "exit")) # Exit
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "exit_next")) # 1. Exit  2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def play():
    try:
        ram = gc.mem_free() / 1024
        gc.collect()
        print(translation.get("debugger", "play_gc_col")) # Cleaned garbage!
        print(str((gc.mem_free() / 1024)) + "KB Ram free" + " was "+str(ram)+"KB")
        import game.game as game
        print(translation.get("debugger", "play_imported")) # Game imported, launching..."
        lcd.clear()
        game.run(wlan, lcd)
        main()
    except ImportError as e:
        print(f"{translation.get("debugger", "play_imp_err")} {e}") # Failed to import the game:
        lcd.clear()
        temp_lcd_brightness = data.get('lcd_brightness')
        lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
        lcd.setCursor(0,0)
        lcd.printout(translation.get("menu", "play_not_f")) # Game not found!
        time.sleep(2.5)
        main()

def reset():
    print(translation.get("debugger", "reset_start")) # Soft reset process started!
    print(translation.get("debugger", "reset_pwr_led")) # Disabling power led
    led.off()
    lcd.setRGB(0,0,0)
    lcd.clear()
    print(translation.get("debugger", "rebooting")) # Rebooting...
    machine.soft_reset()

def settings1():
    global currentMenu
    currentMenu = 3
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("settings", "machine")) # Machine
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings_display():
    global currentMenu
    currentMenu = 18
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("settings", "display")) # Display
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings_display_brightness_selector():
    global currentMenu
    currentMenu = 21
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(str(data.get('lcd_brightness')))
    lcd.setCursor(0,1)
    lcd.printout("1. +        2. -")
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings_display_brightness():
    global currentMenu
    currentMenu = 19
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("settings", "brightness")) # Brightness
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings_display_back():
    global currentMenu
    currentMenu = 20
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("menu", "back")) # Back
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings_buzzer():
    global currentMenu
    currentMenu = 22
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("settings", "buzzer")) # Buzzer
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings_buzzer_volume():
    global currentMenu
    currentMenu = 23
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("settings", "volume")) # Volume
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings_buzzer_volume_selection():
    global currentMenu
    currentMenu = 25
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(str(data.get('buzzer_volume')))
    lcd.setCursor(0,1)
    lcd.printout("1. +        2. -")
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings_buzzer_back():
    global currentMenu
    currentMenu = 24
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("menu", "back")) # Back
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings2():
    global currentMenu
    currentMenu = 14
    lcd.clear()
    temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("menu", "back")) # Back
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings3():
    global currentMenu
    currentMenu = 15
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("setttings", "bootloader")) # Bootloader
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings4():
    global currentMenu
    currentMenu = 16
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("menu", "back")) # Back
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def settings5():
    global currentMenu
    currentMenu = 17
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("settings", "enter_bootloader")) # Enter bootloader
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "yes_no")) # 1. Yes 2. No
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)
    
def settings6():
    global currentMenu
    currentMenu = 31
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("settings", "update")) # Update
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def exit1():
    gc.collect()
    print(translation.get("debugger", "prepare_shutdown")) # Pepairing to shutdown...
    global currentMenu
    currentMenu = 4
    wlan.disconnect()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    
    time.sleep(2)
    lcd.clear()
    lcd.setRGB(0,0,0)
    led.off()
    wlan.disconnect()
    wlan.active(False)
    while True:
        time.sleep(10)
        if button1.value() == 0:
            machine.soft_reset()
        

def apps1():
    global currentMenu
    currentMenu = 7
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("global", "apps")) # Apps
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def apps():
    global currentMenu
    currentMenu = 5
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("apps", "app_wifi")) # Wi-Fi
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def appsExit():
    global currentMenu
    currentMenu = 6
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("menu", "back")) # Back
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def time1():
    global currentMenu
    currentMenu = 10
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("apps", "app_what_time")) # What time is it?
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def whatTimeIsIt1():
    global currentMenu
    currentMenu = 11
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    timeFormatted = utime.localtime(timezones.get_timezoned())

    lcd.printout(str(timeFormatted[3])+":"+str(timeFormatted[4])+":"+str(timeFormatted[5]))
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "next")) # 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)  

def whatTimeIsIt2():
    global currentMenu
    currentMenu = 12
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    timeFormatted = utime.localtime(timezones.get_timezoned())
    lcd.printout(str(timeFormatted[2])+"."+str(timeFormatted[1])+"."+str(timeFormatted[0]))
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "next")) # 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)
    

def whatTimeIsIt3():
    global currentMenu
    currentMenu = 13
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("menu", "back")) # Back
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def wifi():
    global currentMenu
    currentMenu = 8
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    if len(data.get("Wi-Fi").get("wifi_ssid")) > 16:
        lcd.printout("Wi-Fi")
    else:
        lcd.printout(data.get("Wi-Fi").get("wifi_ssid"))
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "back_next"))
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def wifiConnect():
    global currentMenu
    currentMenu = 9
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    if wlan.isconnected() == False:
        lcd.printout(translation.get("wifi", "connect")) # Connect
    else:
        lcd.printout(translation.get("wifi", "disconnect")) # Disconnect
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu)

def connect():
    print(translation.get("debugger", "connecting_to_wlan")) # Conntecting to wlan...
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("wifi", "connecting_to")) # Connecting to
    lcd.setCursor(0,1)
    if len(data.get("Wi-Fi").get("wifi_ssid")) > 16:
        lcd.printout("Wi-Fi")
    else:
        lcd.printout(data.get("Wi-Fi").get("wifi_ssid"))
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(data.get("Wi-Fi").get("wifi_ssid"), data.get("Wi-Fi").get("wifi_password"))
    lcd.setCursor(0,0)
    lcd.printout(translation.get("wifi", "connecting_to")) # Connecting to
    lcd.setCursor(0,1)
    if len(data.get("Wi-Fi").get("wifi_ssid")) > 16:
        lcd.printout("Wi-Fi")
    else:
        lcd.printout(data.get("Wi-Fi").get("wifi_ssid"))
    wifiChecks = 0
    connectBlock = False
    while wlan.isconnected() == False and wifiChecks is not 200 and connectBlock == False:
        if wlan.status() == -1:
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout(translation.get("global", "error")) # Error
            lcd.setCursor(0,1)
            lcd.printout(translation.get("wifi", "connecction_fail")) # Connection fail
            connectBlock = True
            time.sleep(1)
        elif wlan.status() == -2:
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout(translation.get("global", "error")) # Error
            lcd.setCursor(0,1)
            lcd.printout(translation.get("wifi", "ap_not_found")) # AP not found
            connectBlock = True
            time.sleep(1)
        elif wlan.status() == -3:
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout(translation.get("global", "error")) # Error
            lcd.setCursor(0,1)
            lcd.printout(translation.get("wifi", "wrong_password")) # Wrong password
            connectBlock = True
            time.sleep(1)
        wifiChecks = wifiChecks + 1
        led.off()
        time.sleep(0.05)
        led.on()
        time.sleep(0.05)
        led.on()
    if wlan.isconnected() == False:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout(translation.get("wifi", "connection_failed")) # Connection failed!
        print(translation.get("wifi", "connection_failed")) # Connection failed!
        time.sleep(1)

    # Sync clock
    if wlan.isconnected() == True and timeFormatted[0] < 2024:
        print(translation.get("rtc", "debugger_rtc")) # Sync rtc clock...
        lcd.clear()
        lcd.printout(translation.get("rtc", "setting_clock")) # Settings clock...
        ntp.sync(wlan)

def OctoPrint1():
    global currentMenu
    currentMenu = 30
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("OctoPrint")
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu) 

def OctoPrint():
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout(translation.get("global", "loading")) # Loading...
    lcd.setCursor(0,1)
    lcd.printout("0/3")
    file1 = False
    file2 = False
    if files.exist("/plugins/octoprint.py"):
        file1 = True
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout(translation.get("global", "loading")) # Loading...
    lcd.setCursor(0,1)
    lcd.printout("1/3")
    if files.exist("/plugins/octolib.py"):
        file2 = True
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout(translation.get("global", "loading")) # Loading...
    lcd.setCursor(0,1)
    lcd.printout("2/3")
    if file1 == True and file2 == True:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout(translation.get("global", "loading")) # Loading...
        lcd.setCursor(0,1)
        lcd.printout("3/3")
        import plugins.octoprint as ocp
        ocp.start(lcd)
    else:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout(translation.get("global", "please_install")) # Please install
        lcd.setCursor(0,1)
        lcd.printout("OctoPrint Plugin")
        time.sleep(1)
        main()

def update():
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("update", "check_1")) # Checking for
    lcd.setCursor(0,1)
    lcd.printout(translation.get("update", "check_2")) # update
    if wlan.isconnected() == False:
        lcd.clear()
        _temp_lcd_brightness = data.get('lcd_brightness')
        lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
        lcd.setCursor(0,0)
        lcd.printout(translation.get("update", "no_wifi_1")) # No Wi-Fi
        lcd.setCursor(0,1)
        lcd.printout(translation.get("update", "no_wifi_2")) # connection
        time.sleep(2.5)
        main()
        return
    print(translation.get("update", "debug_down_ver_file")) # Downloading version file
    requests.download_file("https://raw.githubusercontent.com/Kitki30/GameBerry/main/pico_w/Gameberry/version_info.json", "/system/temp/version_info.json")
    version_info_temp = json.read("/system/temp/version_info.json")
    if version_info["version"] >= version_info_temp["version"]:
        lcd.clear()
        _temp_lcd_brightness = data.get('lcd_brightness')
        lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
        lcd.setCursor(0,0)
        lcd.printout(translation.get("update", "no_need_1")) # No need to
        lcd.setCursor(0,1)
        lcd.printout(translation.get("update", "no_need_2")) # update!
        time.sleep(2.5)
        main()
        return
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("update", "downloading_1")) # Downloading
    lcd.setCursor(0,1)
    lcd.printout(translation.get("update", "downloading_2")) # update...
    print(translation.get("update", "debug_down_update")) # Downloading update file
    requests.download_file("https://raw.githubusercontent.com/Kitki30/GameBerry/main/pico_w/update.py", "/system/temp/update.py")
    requests.download_file("https://raw.githubusercontent.com/Kitki30/GameBerry/main/pico_w/boot_py_update.py", "/boot.py")
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(translation.get("update", "install_1")) # Installing
    lcd.setCursor(0,1)
    lcd.printout(translation.get("update", "install_2")) # update...
    machine.reset()
    
def battery():
    global currentMenu
    currentMenu = 33
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Battery")
    lcd.setCursor(0,1)
    lcd.printout(translation.get("menu", "ok_next")) # 1. OK 2. Next
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu) 

def battery1():
    global currentMenu
    global bat_calibration
    bat_calibration = json.read("/system/configs/battery_calibration.json")
    currentMenu = 34
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout(bat.calculate_battery_level(ina_vol_meter.bus_voltage(), bat_calibration["v_min"], bat_calibration["v_max"]) + "%")
    lcd.setCursor(0,1)
    lcd.printout(ina_vol_meter.current()+"mA") # Exit
    print(translation.get("debugger", "curr_menu")+str(currentMenu)) # Current menu: (menu) 

# Sync clock
if wlan.isconnected() == True:
    print(translation.get("rtc", "debugger_rtc")) # Sync rtc clock...
    lcd.clear()
    lcd.printout(translation.get("rtc", "setting_clock")) # Setting clock...
    ntp.sync(wlan)
        
main()

while True:

    if button1.value() == 0 and button1state == 1:
        event_ok = 0
        button1state = 0
        buzzer.duty_u16(data.get('buzzer_volume'))
        buzzer.freq(659)
        time.sleep(0.1)
        buzzer.duty_u16(0)
        if currentMenu == 0:
            play()
        elif currentMenu == 1:
            settings1()
        elif currentMenu == 7:
            apps()
        elif currentMenu == 2:
            exit1()
        elif currentMenu == 33:
            battery1()
        elif currentMenu == 6:
            apps1()
        elif currentMenu == 5:
            wifi()
        elif currentMenu == 9:
            if wlan.isconnected() == True:
                wlan.disconnect()
            else:
                connect()
            wifi()
        elif currentMenu == 8:
            apps()
        elif currentMenu == 13:
            time1()
        elif currentMenu == 10:
            whatTimeIsIt1()
        elif currentMenu == 14:
            settings()
        elif currentMenu == 3:
            settings3()
        elif currentMenu == 16:
            settings1()
        elif currentMenu == 15:
            settings5()
        elif currentMenu == 17:
            print(translation.get("debugger", "entering_bootloader")) # Entering bootloader(BOOTSEL)
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout(translation.get("settings", "entering_boot_1")) # Entering
            lcd.setCursor(0,1)
            lcd.printout(translation.get("settings", "entering_boot_1")) # bootloader...
            time.sleep(1)
            lcd.clear()
            lcd.setRGB(0,0,0)
            machine.bootloader()
        elif currentMenu == 18:
            settings_display_brightness()
        elif currentMenu == 20:
            settings_display()
        elif currentMenu == 19:
            settings_display_brightness_selector()
        elif currentMenu == 21:
            if data['lcd_brightness'] is not 255:
                data['lcd_brightness'] = data['lcd_brightness'] + 5
            json.write("/system/user/settings.json", data)
            settings_display_brightness_selector()
        elif currentMenu == 22:
            settings_buzzer_volume()
        elif currentMenu == 23:
            settings_buzzer_volume_selection()
        elif currentMenu == 24:
            settings_buzzer()
        elif currentMenu == 25:
            if data['buzzer_volume'] is not 2000:
                data['buzzer_volume'] = data['buzzer_volume'] + 100
            json.write("/system/user/settings.json", data)
            settings_buzzer_volume_selection()
        elif currentMenu == 30:
            OctoPrint()
        elif currentMenu == 31:
            update()
    elif button1.value() == 1 and button1state == 0:
        print(translation.get("debugger", "button_state")) # Button state updated
        button1state = 1
     
    if button2.value() == 0 and button2state == 1:
        event_ok = 0
        button2state = 0
        buzzer.duty_u16(data.get('buzzer_volume'))
        buzzer.freq(659)
        time.sleep(0.05)
        buzzer.duty_u16(0)
        if currentMenu == 0:
            apps1()
        elif currentMenu == 7:
            if hw.ina_ena() == True:
                battery()
            else:
                settings()
        elif currentMenu == 33:
            settings()
        elif currentMenu == 1:
            exit()
        elif currentMenu == 2:
            main()
        elif currentMenu == 5:
            time1()
        elif currentMenu == 6:
            apps()
        elif currentMenu == 8:
            wifiConnect()
        elif currentMenu == 9:
            wifi()
        elif currentMenu == 10:
            OctoPrint1()
        elif currentMenu == 30:
            appsExit()
        elif currentMenu == 11:
            whatTimeIsIt2()
        elif currentMenu == 12:
            whatTimeIsIt3()
        elif currentMenu == 13:
            whatTimeIsIt1()
        elif currentMenu == 14:
            settings1()
        elif currentMenu == 3:
            settings_display()
        elif currentMenu == 17:
            settings3()
        elif currentMenu == 16:
            settings3()
        elif currentMenu == 15:
            settings4()
        elif currentMenu == 18:
            settings_buzzer()
        elif currentMenu == 19:
            settings_display_back()
        elif currentMenu == 20:
            settings_display_brightness()
        elif currentMenu == 21:
            if data['lcd_brightness'] is not 0:
                data['lcd_brightness'] = data['lcd_brightness'] - 5
            json.write("/system/user/settings.json", data)
            settings_display_brightness_selector()
        elif currentMenu == 22:
            settings6()
        elif currentMenu == 31:
            settings2()
        elif currentMenu == 23:
            settings_buzzer_back()
        elif currentMenu == 24:
            settings_buzzer_volume()
        elif currentMenu == 25:
            if data['buzzer_volume'] is not 0:
                data['buzzer_volume'] = data['buzzer_volume'] - 100
            json.write("/system/user/settings.json", data)
            settings_buzzer_volume_selection()
    elif button2.value() == 1 and button2state == 0:
        print(translation.get("debugger", "button_state")) # Button state updated
        button2state = 1

    if home.value() == 0 and homestate == 1:
        gc.collect()
        homestate = 0
        buzzer.duty_u16(data.get('buzzer_volume'))
        buzzer.freq(659)
        time.sleep(0.05)
        buzzer.duty_u16(0)
        if currentMenu == 21:
            settings_display_brightness()
        elif currentMenu == 25:
            settings_buzzer_volume()
        elif currentMenu == 0:
            event_ok = event_ok + 1
            if event_ok == 5:
                eggs.menu_game(lcd)
            elif event_ok == 8:
                eggs.menu_game2(lcd)
                event_ok = 0
        else:
            main()
    elif home.value() == 1 and homestate == 0:
        print(translation.get("debugger", "button_state")) # Button state updated
        homestate = 1

    if currentMenu == 11:
        whatTimeIsIt1()
    elif currentMenu == 12:
        whatTimeIsIt2()
    elif currentMenu == 34:
        battery1()

    if battery_calib == 20:
        battery_calib = 0
        bat_calibration = json.read("/system/configs/battery_calibration.json")
        bat.calculate_battery_level(ina_vol_meter.bus_voltage(), bat_calibration["v_min"], bat_calibration["v_max"]) 
    
    battery_calib = battery_calib + 1

    time.sleep(0.025)