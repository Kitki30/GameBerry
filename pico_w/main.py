import RGB1602
import time
import os
import sys
import utime
from machine import Pin, PWM
import machine
import rp2
import network
import files
import ntp
from buzzer_music import music

# PicoBerry logo
timeFormatted = utime.localtime(utime.time())
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
print("PicoBerry v0.5 on " + sys.platform)
print(str(timeFormatted[2])+"."+str(timeFormatted[1])+"."+str(timeFormatted[0])+" "+str(timeFormatted[3])+":"+str(timeFormatted[4])+":"+str(timeFormatted[5]))
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

# Check for files
if files.exist("/secrets.py"):
    print("Secrets exist!")
else:
    files.copy("./default/secrets_default.py", "./secrets.py")
import secrets

# Led blink
print("Waiting one second")
led = Pin("LED", Pin.OUT)
blinks = 0
while blinks is not 10:
    blinks = blinks + 1
    time.sleep(0.05)
    led.on()
    time.sleep(0.05)
    led.off()
led.on()

# Initialize buttons
print("Initializing buttons")
button1 = Pin(3, Pin.IN, Pin.PULL_UP) # First button (GPIO3)
button2 = Pin(2, Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
button1state = 1
button2state = 1
print("Button 1 state: "+str(button1.value()))
print("Button 2 state: "+str(button2.value()))

# Turn on main power pin (GPIO9)
print("Turning on main power pin...")
mainPower = Pin(9, Pin.OUT)
mainPower.on()

# Initialize lcd
print("Initializing lcd")
lcd=RGB1602.RGB1602(16,2)
lcd.clear()
lcd.setRGB(0,0,0)



# Initialize buzzer (GPIO8)
print("Initializing buzzer")
buzzer = PWM(Pin(8))
print("Playing test tone")
buzzer.duty_u16(0)
buzzer.duty_u16(1000)
buzzer.freq(659)
time.sleep(0.3)
buzzer.duty_u16(0)

# Connect to wifi
print("Connecting to wlan...")
lcd.setColorWhite()
lcd.setCursor(0,0)
lcd.printout("Connecting to")
lcd.setCursor(0,1)
if len(secrets.wifi_ssid) > 16:
    lcd.printout("Wi-Fi")
else:
    lcd.printout(secrets.wifi_ssid)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.wifi_ssid, secrets.wifi_password)
wifiChecks = 0
while wlan.isconnected() == False and wifiChecks is not 200:
    wifiChecks = wifiChecks + 1
    time.sleep(0.1)
if wlan.isconnected() == False:
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout("Connection failed!")
    print("Connection failed")
    time.sleep(1)

# Sync clock
if wlan.isconnected() == True:
    print("Sync rtc clock..")
    lcd.clear()
    lcd.printout("Setting clock...")
    ntp.sync(wlan)
    print(utime.localtime())

# Menu 

# Menu variables
currentMenu = 0

# Main menu
def main():
    global currentMenu
    currentMenu = 0
    lcd.clear()
    lcd.setColorWhite()
    lcd.setCursor(0,0)
    lcd.printout("GameBerry")
    lcd.setCursor(0,1)
    lcd.printout("1. Play  2. Next")
    print("Current menu: "+str(currentMenu))

# Settings menu
def settings():
    global currentMenu
    currentMenu = 1
    lcd.clear()
    lcd.setColorWhite()
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
    lcd.setColorWhite()
    lcd.setCursor(0,0)
    lcd.printout("Exit")
    lcd.setCursor(0,1)
    lcd.printout("1. Exit  2. Next")
    print("Current menu: "+str(currentMenu))

def play():
    filename = "game.py"
    try:
        import game
        print("Game imported, launching...")
        lcd.clear()
        lcd.setRGB(0,0,0)
        game.run()
        machine.reset()
    except ImportError as e:
        print(f"Failed to import the game: {e}")
        print("Rebooting")
        lcd.clear()
        lcd.setColorWhite()
        lcd.setCursor(0,0)
        lcd.printout("Game not found")
        lcd.setCursor(0,1)
        lcd.printout("Rebooting...")
        time.sleep(1)
        reset()

def reset():
    print("Soft reset process started...")
    print("Disabling power on GPIO9")
    mainPower.off()
    print("Disabling power led")
    led.off()
    print("Rebooting...")
    sys.exit()

def settings1():
    global currentMenu
    currentMenu = 3
    lcd.clear()
    lcd.setColorWhite()
    lcd.setCursor(0,0)
    lcd.printout("Settings not")
    lcd.setCursor(0,1)
    lcd.printout("found!")
    print("Current menu: "+str(currentMenu))
    time.sleep(1)
    settings()

def exit1():
    print("Prepairing to shutdown...")
    global currentMenu
    currentMenu = 4
    lcd.clear()
    lcd.setColorWhite()
    lcd.setCursor(0,0)
    lcd.printout("You can now")
    lcd.setCursor(0,1)
    lcd.printout("unplug power!")
    time.sleep(4)
    mainPower.off()
    led.off()
    wlan.disconnect()
    print("Putting machine to infinite loop")
    while True:
        if button1.value() == 0:
            machine.reset()
        time.sleep(1)
    


print("Going to the menu for first time...")
main()

while True:
    if button1.value() == 0 and button1state == 1:
        button1state = 0
        buzzer.duty_u16(1000)
        buzzer.freq(659)
        time.sleep(0.1)
        buzzer.duty_u16(0)
        if (currentMenu == 0):
            play()
        elif (currentMenu == 1):
            settings1()
        elif (currentMenu == 2):
            exit1()
    elif button1.value() == 1 and button1state == 0:
        print("Button state updated")
        button1state = 1
     
    if button2.value() == 0 and button2state == 1:
        button2state = 0
        buzzer.duty_u16(1000)
        buzzer.freq(659)
        time.sleep(0.05)
        buzzer.duty_u16(0)
        if currentMenu == 0:
            settings()
        elif currentMenu == 1:
            exit()
        elif currentMenu == 2:
            main()
    elif button2.value() == 1 and button2state == 0:
        print("Button state updated")
        button2state = 1
    
    time.sleep(0.05)