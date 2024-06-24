import modules.RGB1602 as RGB1602
from machine import Pin
import machine
import time
import modules.json as json
import modules.playanim as animation
import gc
import modules.onlineFunctions as online_service
import network

lcd=RGB1602.RGB1602(16,2)
led = Pin("LED", Pin.OUT)
button1 = Pin(3, Pin.IN, Pin.PULL_UP) # First button (GPIO3)
button2 = Pin(2, Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
home = Pin(15, Pin.IN, Pin.PULL_UP) # Home button (GPIO15)
button1state = 1
button2state = 1
homestate = 1

data = json.read("/settings.json")
sys_data = data["sys_data"]
wifi_data = data["Wi-Fi"]
online_data = data["online_services"]

isChecked = False

def start():
    global isChecked

    gc.collect()

    led.on()

    lcd.clear()
    _temp_lcd_brightness = data.get('lcd_brightness')
    lcd.setRGB(_temp_lcd_brightness, _temp_lcd_brightness, _temp_lcd_brightness)
    animation.play(lcd, 0, "Gameberry", 0.05)
    time.sleep(1)
    animation.play(lcd, 1, "Press button 1", 0.05)

    while isChecked == False:
        if button1.value() == 0:
            st1()
            isChecked = True
            time.sleep(0.1)
            
def st1():
    global isChecked
    gc.collect()
    if wifi_data["wifi_ssid"] == "":
        animation.play(lcd, 0, "Please set Wi-Fi", 0.025)
        animation.play(lcd, 1, "Configuration", 0.025)
        time.sleep(2)
        animation.play(lcd, 0, "On your PC", 0.025)
        animation.play(lcd, 1, "in settings.json", 0.025)
        time.sleep(1)
        isChecked = False
        while isChecked == False:
            if button1.value() == 0 or button2.value() == 0 or home.value() == 0:
                machine.soft_reset()
    else:
        if online_data['allow_activation'] == True:
            lcd.clear()
            animation.play(lcd, 0, "Activating...", 0.025)
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.connect(data.get("Wi-Fi").get("wifi_ssid"), data.get("Wi-Fi").get("wifi_password"))
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
            result = online_service.register()
            if result == "No":
                lcd.clear()
                animation.play(lcd, 0, "Failed!", 0.025)
                machine.soft_reset()
            lcd.clear()
            animation.play(lcd, 0, "Done!", 0.025)
            time.sleep(1)
            data.get("sys_data")["first_start"] = True
            data.get("sys_data")["id"] = result
            json.write("/settings.json", data)
            machine.soft_reset()
        else:
            lcd.clear()
            animation.play(lcd, 0, "First start done", 0.01)
    


start()