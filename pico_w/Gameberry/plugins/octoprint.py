import modules.json as json
import network
import time
import machine
import plugins.octolib as octo
import gc
from micropython import const
import ujson
import modules.files as files
from machine import Pin

updates = 0

curr = 0

_SKIP_PROFILE_CHECK = const(False) # Set values under this

heatedChamber = False
heatedBed = True

button1 = Pin(3, Pin.IN, Pin.PULL_UP) # First button (GPIO3)
button2 = Pin(2, Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
home = Pin(15, Pin.IN, Pin.PULL_UP) # Home button (GPIO15)
button1state = 1
button2state = 1
homestate = 1

config = None

def start(lcd):
    global config
    keyTested = False
    lcd.clear()
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected() == False:
        lcd.setCursor(0,0)
        lcd.printout("Wi-Fi not")
        lcd.setCursor(0,1)
        lcd.printout("connected")
        time.sleep(1)
        machine.soft_reset()
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.printout("OctoPrint Remote")
    lcd.setCursor(0,1)
    lcd.printout("Kitki30")
    time.sleep(0.25)
    print("Loading OctoPrint app")
    print("Collect trash...")
    gc.collect()
    print("Read config")
    config = json.read("/plugins/octoprint-config.json")
    print("Check url")
    if config["url"] == "":
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("URL not set")
        time.sleep(1)
        machine.soft_reset()
    else:
        octo.setOctoPrintUrl(config["url"])
    print("Check apikey")
    if config["apiKey"] == "":
        print("No apikey set checking for appkeys plugin")
        if octo.appKeysProbe() == True:
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout("Requesting ApiKe")
            lcd.setCursor(0,1)
            lcd.printout("y check Panel")
            token = octo.appKeysRequest("OctoPrint Remote for GameBerry")
            if token == "":
                print("Chosen no or timed out")     
                lcd.clear()
                lcd.setCursor(0,0)
                lcd.printout("set apiKey")
                time.sleep(1)
                machine.soft_reset()
            else:
                octo.setOctoPrintApiKey(token)
                if octo.testApiKey == False:
                    print("Bad api key")     
                    lcd.clear()
                    lcd.setCursor(0,0)
                    lcd.printout("set apiKey")
                    time.sleep(1)
                    machine.soft_reset() 
                else:
                    keyTested = True
                    config["apiKey"] = token
                    json.write("/plugins/octoprint-config.json", config)
                    lcd.clear()
                    lcd.setCursor(0,0)
                    lcd.printout("Restarting...")
                    f = open('/startOptions.gameberry', 'w')
                    f.write('octo-plugin')
                    f.close()
                    time.sleep(1)
                    machine.soft_reset() 
        
        else:
            print("No appkeys plugin detected")     
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout("apiKey not set")
            time.sleep(1)
            machine.soft_reset()
    octo.setOctoPrintApiKey(config["apiKey"])
    if octo.testApiKey == False:
        print("Bad api key")     
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("set apiKey")
        config["apiKey"] = ""
        json.write("/plugins/octoprint-config.json", config)
        time.sleep(1)
        machine.soft_reset() 
    else:
        setup(lcd)
    
    
def setup(lcd):
    global heatedBed
    global heatedChamber
    gc.collect()
    if _SKIP_PROFILE_CHECK == False:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("Reading printer")
        lcd.setCursor(0,1)
        lcd.printout("info...")
        profile = octo.getPrinterProfile("_default")
        if profile == "":
            print("Cannot get print profile info looking for cache!")     
            if files.exist("/plugins/octo-cache.cache"):
                cache = json.read("/plugins/octo-cache.cache")
                heatedChamber = cache["heatedChamber"]
                heatedBed = cache["heatedBed"]
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.printout("Cannot get print")
            lcd.setCursor(0,1)
            lcd.printout("profile info!")
            time.sleep(1)
            machine.soft_reset() 
        else:
            print("Profile "+profile["id"]+"\nName: "+profile["name"]+"\nPrinter: "+profile["model"]+"\nDefault: "+str(profile["default"])+"\nCurrent: "+str(profile["current"])+"\nHeated Bed: "+str(profile["heatedBed"])+"\nHeated Chamber: "+str(profile["heatedChamber"]))
            heatedChamber = profile["heatedChamber"]
            heatedBed = profile["heatedBed"]
            SaveCache(heatedBed, heatedChamber)
            main(lcd)
    else:
        main(lcd)

def SaveCache(heatedBed, heatedChamber):
    json.write("/plugins/octo-cache.cache", ujson.dumps({"heatedBed": heatedBed, "heatedChamber": heatedChamber}))

def basicTemps(lcd):
    global curr
    curr = 0
    temp = octo.getTemps()
    if heatedBed == True:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("Bed: "+str(round(temp["temperature"]["bed"]["actual"])))
        lcd.write(0)
        lcd.printout("C")
        lcd.setCursor(0,1)
        lcd.printout("Tool: "+str(round(temp["temperature"]["tool0"]["actual"])))
        lcd.write(0)
        lcd.printout("C")
    else:
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("Tool: "+str(round(temp["temperature"]["tool0"]["actual"])))
        lcd.write(0)
        lcd.printout("C")
        if heatedChamber == True:
            lcd.setCursor(0,1)
            lcd.printout("Chamber: "+str(round(temp["temperature"]["tool0"]["actual"])))
            lcd.write(0)
            lcd.printout("C")

def chamberTemp(lcd):
    global curr
    curr = 1
    temp = octo.getTemps()
    lcd.clear()
    lcd.setCursor(0,1)
    lcd.printout("Chamber: "+str(round(temp["temperature"]["chamber"]["actual"])))
    lcd.write(0)
    lcd.printout("C")

def main(lcd):
    global curr
    global updates
    basicTemps(lcd)
    while True:
        if button2.value() == 0 and button2state == 1:
            if curr == 0:
                if heatedChamber == True:
                    chamberTemp(lcd)
            if curr == 1:
                basicTemps(lcd)  
        else:
            button2state = 1 
    