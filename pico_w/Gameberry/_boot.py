# POST

# Blink code:
# Broken lcd - 3 blinks
# Broken lcd - 4 blinks

print("POST:")
import machine
import modules.customExceptions
import modules.blinker as blinker
import modules.json as json
import modules.battery as battery
import rp2
if rp2.bootsel_button() == 1:
    raise Exception("Safe mode")
battery.calibrate()
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
    except OSError as osError:
        print("LCD - Broken\n")
        blinker.blink(3, 0.25)
        raise modules.customExceptions.LcdDisplayError("LCD Display is not connected or has broken please check the display and connection to the board!\nError:\n"+str(osError))

print("\nAll things working ready to boot!")

# Boot
import device_config
boot_config = json.read_from_string(device_config.data())
print("Booting "+boot_config["main"]["name"]+" "+boot_config["main"]["file"])
exec(open(boot_config["main"]["file"]).read())