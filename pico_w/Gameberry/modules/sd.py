import machine
import modules.sdcard as sdcard
import uos
import gc

sd = None
started = False
mounted = False
mountPoint = ""

def mount(path):
    global sd
    global started
    global mounted
    global mountPoint
    print("Mounting SD Card...")
    if started == False:
        start()
    if mounted == False:
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, path)
        mounted = True
        mountPoint = path
    print("Mounted SD Card!")
    print("Path of SD: "+path)

def unmount():
    global sd
    global started
    global mounted
    global mountPoint
    print("Unmounting SD Card...")
    if mounted == True:
        uos.unmount(mountPoint)
        mounted = False
        mountPoint = ""
    print("Unmounted SD Card!")

def start():
    global sd
    global started
    print("Starting SD Card...")
    print("Initializing SPI...")
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
    print("Initializing SD Card...")
    sd = sdcard.SDCard(spi, cs)
    started = True
    print("Started SD Card!")

def stop():
    global sd
    if started == True:
        print("Stopping SD card...")
        unmount()
        sd = None
        gc.collect()
        print("SD Card stopped!")

    