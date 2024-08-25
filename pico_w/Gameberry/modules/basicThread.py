import _thread
import time
import modules.json as json
import ujson
import modules.sdcard as sdcard
import machine
import modules.customExceptions as exceptions
import modules.RGB1602 as RGB1602
import os

thread_active = False
threadTime = 0
thread_monitor_sd_card = False
thread_reset_time = 5
sd_not_used = True

def thread_activity():
    print("Starting basicThread")
    global thread_active
    global thread_monitor_sd_card
    global threadTime
    global sd_not_used
    global thread_reset_time
    while thread_active == True:
        threadTime = threadTime + 1
        thread_temp_file = json.read("/thread_temp_file.json")
        thread_active = thread_temp_file["active"]
        thread_monitor_sd_card = thread_temp_file["sd_monitor"]
        sd_not_used = thread_temp_file["sd_not_used"]
        if thread_monitor_sd_card == True:
            if threadTime == 5 and sd_not_used == True:
                print("Checking SD Card...")
                cs = machine.Pin(13, machine.Pin.OUT)
                spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(12))
                sd = sdcard.SDCard(spi, cs)
                if sd.is_present() == False:
                    lcd = RGB1602.RGB1602(16,2)
                    exceptions.ShowErrorScreen_with_code(lcd, "SD_CARD_ERROR")
        if threadTime == thread_reset_time:
            threadTime = 0
        time.sleep(1)              
    print("Stopping basicThread")
    os.remove("/thread_temp_file.json")
    print("Stopped")
            
def start():
    thread_active = True
    json.write("/thread_temp_file.json", ujson.dumps({"active": thread_active, "sd_monitor": thread_monitor_sd_card, "sd_not_used": sd_not_used}))
    _thread.start_new_thread(thread_activity, ())
