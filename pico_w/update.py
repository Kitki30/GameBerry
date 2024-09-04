# Don't change anything under than line unless you know what you are doing!
print("Running")
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

# Download list URL
download_list_url = "https://raw.githubusercontent.com/Kitki30/GameBerry/main/pico_w/download_list.txt"
download_list_path = "/system/temp/list.txt"

# Force not to format flash
force_not_to_format_flash = True

# Log Path
log_path = "/system/temp/update_log.log"

# Imports
import ujson
import urequests
import gc
import network
import time
import os
import uos
import machine
import sys

def exist(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False
    
if exist("/system/temp"):
    print("")
else:
    print("Making folder")
    os.mkdir("/system")
    os.mkdir("/system/temp")

def log(log):
    with open(log_path, "a") as file:
        file.write(str("\n"+log))

def read_json(filename):
    with open(filename, 'r') as file:
        data = ujson.load(file)
    return data

def write_json(filename, data):
    with open(filename, 'wb') as file:
        ujson.dump(data, file)

def write_device_config(ina, sd):
    write_json("/device_confg.json", ujson.dumps({"INA219": ina, "SD_READER": sd}))
    
def GET_request(url):
    log("GC Collect...")
    gc.collect()
    log("Make GET request...")
    response = urequests.get(url)
    log("Made GET request...")
    return response
    
def download_file(url, filename):
    log("Making GET request for File download")
    response = GET_request(url)
    
    if response.status_code == 200:
        log("Writing content of request to file")
        with open(filename, 'wb') as f:
            f.write(response.content)
            log("Closing response")
            response.close()
            return True
    else:
        log("Error, status code: "+response.status_code)
        log("Closing response")
        response.close()
        return False
    
def readline(line_number, filename):
    log("Reading line " + str(line_number) + " of file " + filename)
    with open(filename, 'r') as file:
        for current_line_number, line in enumerate(file, start=1):
            if current_line_number == line_number:
                return line.strip()
    return None

def remove_item(path):
    if os.stat(path)[0] & 0x4000:
        for item in os.listdir(path):
            remove_item(path + "/" + item)
        os.rmdir(path)
    else:
        os.remove(path)

def format_flash():
    files = os.listdir()
    for file in files:
        if file == log_path:
            log("Deleting: " + str(file))
            print("Deleting " + str(file))
            remove_item(file)
    
def download_list(url):
    return download_file(download_list_url, download_list_path)

def variables(text):
    x = text.replace("${machine_name}", str(uos.uname().machine)).replace("${log_path}", log_path)
    return x

def writeInstallConfig():
    write_json("/install_conf.json", ujson.dumps({"download_list": download_list_url, "log_path": log_path, "flash_format": force_not_to_format_flash}))
    
print("Reading config")
data = read_json("/settings.json")

log("Starting installer")
log("Machine name: "+str(uos.uname().machine))
print("Machine name: "+str(uos.uname().machine))
print("\033[94mWelcome to GameBerry updater by Kitki30\033[0m")
log("Connecting to Wi-Fi")
print("Connecting to the Wi-Fi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(data.get("Wi-Fi").get("wifi_ssid"), data.get("Wi-Fi").get("wifi_password"))
wifi_i = 0
while wlan.isconnected() == False and wifi_i is not 30:
    time.sleep(1)
    wifi_i = wifi_i + 1
if wlan.isconnected() == False:
    log("Could not connect to the Wi-Fi")
    log("Error: " + str(wlan.status()))
    log("Micropython Wlan Statuses:")
    log("""
    STAT_IDLE -- 0
    STAT_CONNECTING -- 1
    STAT_WRONG_PASSWORD -- -3
    STAT_NO_AP_FOUND -- -2
    STAT_CONNECT_FAIL -- -1
    STAT_GOT_IP -- 3
    """)
    print("\033[91mWi-Fi connections timeout please check your password or signal strenght\033[0m")
    log("Waiting 5 seconds")
    time.sleep(5)
    log("Reboting...")
    machine.soft_reset()
print("Format flash...")
log("force_not_to_format_flash is "+str(force_not_to_format_flash))
if force_not_to_format_flash == False:
    log("Formatting flash...")
    format_flash()
else:
    log("Skipped formatting flash...")
    print("\033[92mSkipped flash formatting, force_not_to_format_flash set to "+str(force_not_to_format_flash)+"\033[0m")
    
log("Downloading download list...")
log("Download list URL: " + download_list_url)
print("Downloading download list..")
if download_list(download_list_url) == True:
    log("Download successfull")
    print("Downloading successfull")
else:
    log("\033[91mDownload failed\033[0m")
    print("Downloading failed")
    log("Waiting 5 seconds")
    time.sleep(5)
    log("Rebooting...")
    machine.soft_reset()
log("Showing version of download list (Line 2)")
print(readline(2, download_list_path))

log("Starting install...")
print("Starting install...")
log("Reading list...")
print("Read list...")
line = 1
is_end = False
is_started = False
lines_before_start = 0
max_line_before_start = 10
while is_end == False:
    log("Reading line "+ str(line))
    read = readline(line, download_list_path)
    log("Line: "+str(read))
    if is_started == False:
        if read == "START":
            log("Download list started")
            print("Download list started")
            is_started = True
        else:
            lines_before_start = lines_before_start + 1
            log("Lines before start: "+str(lines_before_start))
            if lines_before_start == max_line_before_start:
                log("Much lines before start probably a trap")
                log("Lines before start: " + str(lines_before_start))
                log("Max lines before start: " + str(max_line_before_start))
                print("\033[91mToo much lines before start of the list probably a trap\033[0m")
                print("Please stop the script if waiting more than 15 seconds for starting")
                print("Then report as issue on Github")
    if is_started == True:
        if read == "folder":
            log("Creating folder...")
            print("Creating folder...")
            log("Reading folder name to be created...")
            line = line + 1
            read = readline(line, download_list_path)
            log("Creating folder: " + read)
            if exist("/"+read):
                print("Folder exists!")
            else:
                os.mkdir("/" + read)
            log("Created folder")
            print("Created folder: " + read)
        elif read == "download":
            log("Downloading file...")
            print("Downloading file...")
            log("Reading target path...")
            line = line + 1
            path = readline(line, download_list_path)
            log("Target file path: "+path)
            print("Path: /" + path)
            log("Reading file download URL...")
            line = line + 1
            url = readline(line, download_list_path)
            log("File download URL: "+url)
            print("URL: " + url)
            log("Downloading file...")
            download_file(url, "/" + path)
            log("Downloaded")
            print("Downloaded")
        elif read == "message":
            log("Got message from download list")
            log("Reading content")
            line = line + 1
            printer = readline(line, download_list_path)
            log("Content: "+printer)
            print(printer)
        elif read == "time":
            log("Got wait command")
            log("Reading time to wait...")
            line = line + 1
            time = readline(line, download_list_path)
            log("Time to wait: "+str(time))
            log("Waiting...")
            # time.sleep(float(time))
        elif read == "log-message":
            line = line + 1
            printer = readline(line, download_list_path)
            log("[DL] " + printer)
        elif read == "comment":
            # Ignore command
            line = line + 1
        elif read == "write":
            log("Writing to file")
            line = line + 1
            name = readline(line, download_list_path)
            log("Path: "+name)
            line = line + 1
            content = readline(line, download_list_path)
            log("Content: "+content)
            with open(name, "w") as file:
                file.write(content)
        elif read == "write-append":
            log("Writing to file")
            line = line + 1
            name = readline(line, download_list_path)
            log("Path: "+name)
            line = line + 1
            content = readline(line, download_list_path)
            log("Content: "+content)
            with open(name, "a") as file:
                file.write(content)
        elif read == "END":
            print("End of list")
            print("Write install conf")
            writeInstallConfig()
            is_end = True
    line = line + 1
os.remove(download_list_path)
print("\033[92mUpdate successfull\033[0m")
print("Rebooting...")
try:
    z=42/0
except Exception as e:
    from io import StringIO
    s=StringIO()
    sys.print_exception(e, s)
    sv = s.getvalue()
    if sv.find("<stdin>") >= 0:
        print("Running from REPL doing Soft Reset")
        machine.soft_reset()
    else:
        print("Running from file")
        machine.reset()

# By Kitki30