# POST

# Blink code:
# Broken lcd - 3 blinks
# Broken lcd - 4 blinks

version = 1.0

print("POST:")
import machine
import modules.customExceptions
import modules.blinker as blinker
import modules.json as json
import modules.files as files
import time

led = machine.Pin("LED", machine.Pin.OUT)
led.on()

postBypass = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Post skip
if postBypass.value() == 1:
    print("POST Skipped with GPIO22 PIN!")

# Flash memory
if postBypass.value() == 0:
    try:
        import random
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        chars = letters + digits
        random1 = ''.join(random.choice(chars) for _ in range(64))
        with open("/power_on_self_test_file", 'wb') as file:
            file.write(random1.encode('utf-8'))
        with open("/power_on_self_test_file", 'rb') as file:
            readed = file.read().decode('utf-8')
            if random1 == readed:
                print("Flash memory - Working")
            else:
                raise modules.customExceptions.FileReadWriteError("Test file content was different when writing({}) and when reading({})".format(random1,readed))
    except Exception as exception:
        print("Flash memory - Broken")
        blinker.blink(4, 0.25)
        raise modules.customExceptions.FileReadWriteError("Error happened when reading/writing to flash memory!\nError:\n"+str(exception))

# LCD
if postBypass.value() == 0:
    try:
        import modules.RGB1602 as l
        lcd = l.RGB1602(16,2)
        i = 0
        i2 = 0
        lcd.setCursor(0,0)
        lcd.setRGB(0,0,0)
        while i is not 2:
            while i2 is not 16:
                lcd.write(7)
                i2 = i2 + 1
            lcd.setCursor(0,1)
            i = i + 1
        lcd.clear()
        print("LCD - Working")
        lcd.clear()
        lcd.setColorWhite()
        lcd.setCursor(0,0)
        lcd.printout("Gameberry Boot")
        lcd.setCursor(0,1)
        lcd.printout("Manager v"+str(version))
    except OSError as osError:
        print("LCD - Broken\n")
        blinker.blink(3, 0.25)
        raise modules.customExceptions.LcdDisplayError("LCD Display is not connected or has broken please check the display and connection to the board!\nError:\n"+str(osError))


buzzer = machine.PWM(machine.Pin(16, machine.Pin.OUT))
buzzer.duty_u16(2000)
buzzer.freq(659)
time.sleep(0.1)
buzzer.duty_u16(0)

boot_config = json.read("/boot_config.json")

print("\nAll things working ready to boot!")

# Boot
if files.exist(boot_config["main"]["file"]):
    print("Booting main...")
    exec(open(boot_config["main"]["file"]).read())
else:
    buzzer.duty_u16(2000)
    buzzer.freq(700)
    time.sleep(0.1)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    buzzer.duty_u16(2000)
    time.sleep(0.1)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    buzzer.duty_u16(2000)
    time.sleep(0.1)
    buzzer.duty_u16(0)
    time.sleep(0.1)
    if files.exist(boot_config["recovery"]["file"]):
        print("Booting recovery...")
        boot_config = json.read_from_string("/device_config.json")
        exec(open(boot_config["recovery"]["file"]).read())
    else:
        buzzer.duty_u16(2000)
        buzzer.freq(600)
        time.sleep(0.1)
        buzzer.duty_u16(0)
        time.sleep(0.1)
        buzzer.duty_u16(2000)
        time.sleep(0.1)
        buzzer.duty_u16(0)
        time.sleep(0.1)
        buzzer.duty_u16(2000)
        time.sleep(0.1)
        buzzer.duty_u16(0)
        try:
            print("Mounting SD Card...")
            import modules.sd
            modules.sd.start()
            modules.sd.mount("/recovery")
            print("Booting SD recovery")
            exec(open("/recovery/recovery/recovery.py").read())
        except:
            buzzer.duty_u16(2000)
            buzzer.freq(500)
            time.sleep(0.1)
            buzzer.duty_u16(0)
            time.sleep(0.1)
            buzzer.duty_u16(2000)
            time.sleep(0.1)
            buzzer.duty_u16(0)
            time.sleep(0.1)
            buzzer.duty_u16(2000)
            time.sleep(0.1)
            buzzer.duty_u16(0)
            time.sleep(0.1)
            buzzer.duty_u16(2000)
            buzzer.freq(200)
            time.sleep(0.50)
            buzzer.duty_u16(0)
            import modules.RGB1602 as l
            lcd = l.RGB1602(16,2)
            modules.customExceptions.ShowErrorScreen_with_code(lcd, "no_boot_options")
            print("Error: No more boot options, please install gameberry or insert recovery SD")
            