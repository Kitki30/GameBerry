import time
import machine
from machine import Pin
import modules.json as json
import gc

button1 = Pin(3, Pin.IN, Pin.PULL_UP) # First button (GPIO3)
button2 = Pin(2, Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
home = Pin(15, Pin.IN, Pin.PULL_UP) # Home
btn1state = 0
btn2state = 0
homestate = 0

def show(lcd):
    global btn1state
    global btn2state
    global homestate
    btn1state = 0
    btn2state = 0
    homestate = 0
    gc.collect()
    print("Showing system menu")
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout("Loading data!")
    lcd.setCursor(0,1)
    lcd.printout("Please wait...")
    data = json.read("/system/user/settings.json")
    time.sleep(0.2)
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout("1. Sleep 2. Hide")
    lcd.setCursor(0,1)
    lcd.printout("Home: Exit")
    menuOpen = True
    sleep = False
    while menuOpen == True:
        time.sleep(0.05)
        if button1.value() == 0 and btn1state == 1:
                lcd.clear()
                lcd.setRGB(0,0,0)
                sleep = True
                menuOpen = False
                while sleep == True:
                     time.sleep(0.5)
                     if home.value() == 0:
                          sleep = False
                          show(lcd)
                          return
        if button2.value() == 0 and btn1state == 1:
             gc.collect()
             lcd.clear()
             menuOpen = False
             return
        if home.value() == 0 and btn1state == 1:
             gc.collect()
             machine.soft_reset()
        if home.value() == 1:
             homestate = 1
        if button1.value() == 1:
             btn1state = 1
        if button2.value() == 1:
             btn2state = 1
                     
                    
                    

