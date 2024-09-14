from machine import Pin
import utime as time
import system.configs.ir_list as ir_list
from system.modules.hardware.pico_ir import read_code, send_code, validate_code, InvalidCodeException

pin_out = Pin(22, mode=Pin.OUT)
button1 = Pin(3, Pin.IN, Pin.PULL_UP) # First button (GPIO3)
button2 = Pin(2, Pin.IN, Pin.PULL_UP) # Second button (GPIO2)
home = Pin(15, Pin.IN, Pin.PULL_UP) # Home
fixerBtn1 = 1
menu = 0

def start(lcd):
    global menu
    onoff(lcd)
    while True:
        if button1.value() == 0 and fixerBtn1 == 1:
            if menu == "onoff":
                menu = "wait"
                lcd.clear()
                lcd.setCursor(0,0)
                lcd.printout("Sending code")
                lcd.setCursor(0,1)
                lcd.printout("0%")
                send_list(ir_list.on_off)
                onoff(lcd)
            fixerBtn1 = 0
        elif button1.value() == 1:
            fixerBtn1 = 1
        if home.value() == 0:
            return
        time.sleep(0.025)

def onoff(lcd):
    global menu
    menu = "onoff"
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.write(0)
    lcd.setCursor(2,0)
    lcd.printout("On / Off")
    lcd.setCursor(0,1)
    lcd.printout("1. OK    2. Next")

def send_one(code):
    try:
        start_time = time.time()
        print("Sending code: "+str(code))
        validate_code(code)
        send_code(pin_out, f"{code:032b}")
        print("Sent code: "+str(code)+ " in "+start_time - time.time()+"s")
    except InvalidCodeException:
        print("InvalidCodeException:" + code)
    
def send_list(list):
    i = 0
    for code in list:
        send_one(code)
        i = i + 1
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.printout("Sending code")
        lcd.setCursor(0,1)
        lcd.printout(str(((i / len(list)) * 100)) + "%")