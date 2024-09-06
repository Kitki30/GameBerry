# Factory reset script
# By Kitki30

import modules.files as files ; import os ; import machine
print("Begin factory reset...")
print("Don't turn off the device!")
print("Deleting user data...")
if files.exist("/system/user"):
    os.remove("/system/user")
    print("Creating new user folder")
    os.mkdir("/system/user")
    os.mkdir("/system/user/savedata")
    print("Copying default settings")
    files.copy("/system/default/settings_default.json", "/system/user/settings.json")
print("Deleting temp files")
if files.exist("/system/temp"):
    os.remove("/system/temp")
    print("Creating new temp folder")
if files.exist("/system/configs/first_start.txt"):
    os.remove("/system/configs/first_start")
print("Data was reset!")
print("Rebooting...")
machine.soft_reset()