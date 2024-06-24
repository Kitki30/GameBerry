import time
from machine import Pin
import modules.saveDataManager as saveDataManager
import machine
import modules.gameSystemMenu as sysMenu

button1 = Pin(3, Pin.IN, Pin.PULL_UP) # First button (GPIO3)
button2 = Pin(2, Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
home = Pin(15, Pin.IN, Pin.PULL_UP) # Home
fixerBtn1 = 1
clicks = 0
saveData = None
saveclicks = 0

def run(wlan, lcd):
    print("BerryClicker is running!")
    global fixerBtn1
    global saveData
    global saveclicks
    global clicks
    loadingData(lcd)
    clicks = saveData["clicks"] # Even if shows error in IDE please leave it like that, its read on line 18
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout("BerryClicker")
    lcd.setCursor(0,1)
    lcd.printout("Kitki30")
    time.sleep(0.5)
    main(lcd)
    while True:
        if button1.value() == 0 and fixerBtn1 == 1:
            clicks = clicks + 1
            saveclicks = saveclicks + 1
            if saveclicks == 100:
                saveclicks = 0
                save(lcd)
            fixerBtn1 = 0
            main(lcd)
        elif button1.value() == 1:
            fixerBtn1 = 1
        if home.value() == 0:
            save(lcd)
            sysMenu.show(lcd)
            loadingData(lcd)
            main(lcd)
        time.sleep(0.025)

def main(lcd):
    global clicks
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout("Clicks: ")
    lcd.setCursor(0,1)
    lcd.printout(str(clicks))

def loadingData(lcd):
    global saveData
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout("Loading data!")
    lcd.setCursor(0,1)
    lcd.printout("Please wait...")
    time.sleep(0.2)
    saveData = saveDataManager.load()

def save(lcd):
    global saveData
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout("Saving data!")
    lcd.setCursor(0,1)
    lcd.printout("Please wait...")
    saveData['clicks'] = clicks
    saveDataManager.save(saveData)