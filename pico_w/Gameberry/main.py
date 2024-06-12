import modules.RGB1602 as RGB1602
import uos
import modules.json as json
import utime as time, utime
from machine import Pin, PWM, Timer
import machine
import network
import modules.files as files
import modules.ntp as ntp
import modules.time as timezones
import _thread
import gc

events_working = False
runEvents = True

version = "v0.6"

gc.collect()


# Initialize buttons
button1 = Pin(3, Pin.IN, Pin.PULL_UP) # First button (GPIO3)
button2 = Pin(2, Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
home = Pin(15, Pin.IN, Pin.PULL_UP) # Home button (GPIO15)
button1state = 1
button2state = 1
homestate = 1

safeboot = False

if home.value() == 0:
    safeboot = True
    while safeboot == True:
        print("Machine is in safeboot")
        print("Press button 1 to continue execution of main.py")
        if button1.value() == 0:
            safeboot = False
        time.sleep(5)

# Gameberry logo
timeFormatted = utime.localtime(timezones.get_timezoned())
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
print("GameBerry "+version+" on " + uos.uname().machine)
print("Machine frequency: "+str(machine.freq() / 1000000)+" Mhz")
print(str(timeFormatted[2])+"."+str(timeFormatted[1])+"."+str(timeFormatted[0])+" "+str(timeFormatted[3])+":"+str(timeFormatted[4])+":"+str(timeFormatted[5]))
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

# RTC Clock
rtc = machine.RTC()


if files.exist("/settings.json"):
    print("Settings exist!")
else:
    files.copy("./default/settings.json", "./settings.json")

data = json.read("/settings.json")
sys_data = data["sys_data"]
if sys_data["first_start"] == False:
    import modules.firstStart as firstStart
    gc.collect()
    firstStart.start()
    machine.soft_reset()




if files.exist("/savedata"):
    print("Savedata exists")
else:
    files.create_folder("/savedata")



# Start connecting to Wi-Fi
wifiExists = False

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(data.get("Wi-Fi").get("wifi_ssid"), data.get("Wi-Fi").get("wifi_password"))
        

# Led blink
print("Waiting one second")
led = Pin("LED", Pin.OUT)
blinks = 0
while blinks is not 10:
    blinks = blinks + 1
    time.sleep(0.025)
    led.on()
    time.sleep(0.025)
    led.off()
led.on()

def eventloop():
    global runEvents
    global events_working
    rtc_sync_time = 0
    while runEvents == True:
        time.sleep(1)
        rtc_sync_time = rtc_sync_time + 1
        if rtc_sync_time == 30 and wlan.isconnected() == True:
            rtc_sync_time = 0
            events_working = True
            ntp.sync(wlan)
            events_working = False

# Run event loop
print("Running event loop thread")
# _thread.start_new_thread(events_working, ())


# Initialize lcd
print("Initializing lcd")
lcd=RGB1602.RGB1602(16,2)
lcd.clear()
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

# Initialize buzzer (GPIO8)
print("Initializing buzzer")
buzzer = PWM(Pin(8, Pin.OUT))
buzzer.duty_u16(0)

# Connect to wifi
lcd.setCursor(0,0)
lcd.printout("Connecting to")
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
        lcd.printout("Error")
        lcd.setCursor(0,1)
        lcd.printout("Connection Fail")
        connectBlock = True
        time.sleep(1)
    elif wlan.status() == -2:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("Error")
        lcd.setCursor(0,1)
        lcd.printout("AP not found")
        connectBlock = True
        time.sleep(1)
    elif wlan.status() == -3:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("Error")
        lcd.setCursor(0,1)
        lcd.printout("Wrong password")
        connectBlock = True
        time.sleep(1)
    wifiChecks = wifiChecks + 1
    led.off()
    time.sleep(0.05)
    led.on()
    time.sleep(0.05)
led.on()


# Sync clock
if wlan.isconnected() == True and timeFormatted[0] < 2024:
    print("Sync rtc clock..")
    lcd.clear()
    lcd.printout("Setting clock...")
    ntp.sync(wlan)

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
        lcd.printout("Game")
    lcd.setCursor(0,1)
    lcd.printout("1. Play  2. Next")
    print("Current menu: "+str(currentMenu))

# Settings menu
def settings():
    global currentMenu
    currentMenu = 1
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Settings")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

# Exit
def exit():
    global currentMenu
    currentMenu = 2
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Exit")
    lcd.setCursor(0,1)
    lcd.printout("1. Exit  2. Next")
    print("Current menu: "+str(currentMenu))

def play():
    try:
        ram = gc.mem_free() / 1024
        gc.collect()
        print("Cleaned garbage!!!")
        print(str((gc.mem_free() / 1024)) + "KB Ram free" + " was "+str(ram)+"KB")
        import game.game as game
        print("Game imported, launching...")
        lcd.clear()
        game.run(wlan, lcd)
        machine.reset()
    except ImportError as e:
        print(f"Failed to import the game: {e}")
        print("Rebooting")
        lcd.clear()
        temp_lcd_brightness = data.get('lcd_brightness')
        lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
        lcd.setCursor(0,0)
        lcd.printout("Game not found")
        lcd.setCursor(0,1)
        lcd.printout("Rebooting...")
        time.sleep(1)
        reset()

def reset():
    print("Soft reset process started...")
    print("Disabling power led")
    led.off()
    lcd.setRGB(0,0,0)
    lcd.clear()
    print("Rebooting...")
    machine.soft_reset()

def settings1():
    global currentMenu
    currentMenu = 3
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Machine")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def settings_display():
    global currentMenu
    currentMenu = 18
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Display")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

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
    print("Current menu: "+str(currentMenu))

def settings_display_brightness():
    global currentMenu
    currentMenu = 19
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Brightness")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def settings_display_back():
    global currentMenu
    currentMenu = 20
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Back")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def settings_buzzer():
    global currentMenu
    currentMenu = 22
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Buzzer")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))  

def settings_buzzer_volume():
    global currentMenu
    currentMenu = 23
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Volume")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))  

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
    print("Current menu: "+str(currentMenu))  

def settings_buzzer_back():
    global currentMenu
    currentMenu = 24
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Back")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu)) 

def settings2():
    global currentMenu
    currentMenu = 14
    lcd.clear()
    temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Back")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def settings3():
    global currentMenu
    currentMenu = 15
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Bootloader")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def settings4():
    global currentMenu
    currentMenu = 16
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Back")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def settings5():
    global currentMenu
    currentMenu = 17
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Enter Bootloader")
    lcd.setCursor(0,1)
    lcd.printout("1. Yes     2. No")
    print("Current menu: "+str(currentMenu))

def exit1():
    gc.collect()
    print("Prepairing to shutdown...")
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
    lcd.printout("Apps")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def apps():
    global currentMenu
    currentMenu = 5
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Wi-Fi")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def appsExit():
    global currentMenu
    currentMenu = 6
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Back")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def time1():
    global currentMenu
    currentMenu = 10
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("What time is it?")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))  

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
    lcd.printout("         2. Next")
    print("Current menu: "+str(currentMenu))  

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
    lcd.printout("         2. Next")
    print("Current menu: "+str(currentMenu))  
    

def whatTimeIsIt3():
    global currentMenu
    currentMenu = 13
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Back")
    lcd.setCursor(0,1)
    lcd.printout("1. Back  2. Next")
    print("Current menu: "+str(currentMenu))  

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
    lcd.printout("1. Back  2. Next")
    print("Current menu: "+str(currentMenu))

def wifiConnect():
    global currentMenu
    currentMenu = 9
    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    if wlan.isconnected() == False:
        lcd.printout("Connect")
    else:
        lcd.printout("Disconnect")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")
    print("Current menu: "+str(currentMenu))

def connect():
    print("Connecting to wlan...")
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.setCursor(0,0)
    lcd.printout("Connecting to")
    lcd.setCursor(0,1)
    if len(data.get("Wi-Fi").get("wifi_ssid")) > 16:
        lcd.printout("Wi-Fi")
    else:
        lcd.printout(data.get("Wi-Fi").get("wifi_ssid"))
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(data.get("Wi-Fi").get("wifi_ssid"), data.get("Wi-Fi").get("wifi_password"))
    lcd.setCursor(0,0)
    lcd.printout("Connecting to")
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
            lcd.printout("Error")
            lcd.setCursor(0,1)
            lcd.printout("Connection Fail")
            connectBlock = True
            time.sleep(1)
        elif wlan.status() == -2:
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout("Error")
            lcd.setCursor(0,1)
            lcd.printout("AP not found")
            connectBlock = True
            time.sleep(1)
        elif wlan.status() == -3:
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout("Error")
            lcd.setCursor(0,1)
            lcd.printout("Wrong password")
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
        lcd.printout("Connection failed!")
        print("Connection failed")
        time.sleep(1)

    # Sync clock
    if wlan.isconnected() == True and timeFormatted[0] < 2024:
        print("Sync rtc clock..")
        lcd.clear()
        lcd.printout("Setting clock...")
        ntp.sync(wlan)



print("Going to the menu for first time...")
main()

while True:

    if button1.value() == 0 and button1state == 1:
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
            print("Entering bootloader(BOOTSEL)")
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout("Entering")
            lcd.setCursor(0,1)
            lcd.printout("bootloader...")
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
            json.write("/settings.json", data)
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
            json.write("/settings.json", data)
            settings_buzzer_volume_selection()
    elif button1.value() == 1 and button1state == 0:
        print("Button state updated")
        button1state = 1
     
    if button2.value() == 0 and button2state == 1:
        button2state = 0
        buzzer.duty_u16(data.get('buzzer_volume'))
        buzzer.freq(659)
        time.sleep(0.05)
        buzzer.duty_u16(0)
        if currentMenu == 0:
            apps1()
        elif currentMenu == 7:
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
            json.write("/settings.json", data)
            settings_display_brightness_selector()
        elif currentMenu == 22:
            settings2()
        elif currentMenu == 23:
            settings_buzzer_back()
        elif currentMenu == 24:
            settings_buzzer_volume()
        elif currentMenu == 25:
            if data['buzzer_volume'] is not 0:
                data['buzzer_volume'] = data['buzzer_volume'] - 100
            json.write("/settings.json", data)
            settings_buzzer_volume_selection()
    elif button2.value() == 1 and button2state == 0:
        print("Button state updated")
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
        else:
            main()
    elif home.value() == 1 and homestate == 0:
        print("Button state updated")
        homestate = 1

    if currentMenu == 11:
        whatTimeIsIt1()
    elif currentMenu == 12:
        whatTimeIsIt2()
    
    
    time.sleep(0.025)