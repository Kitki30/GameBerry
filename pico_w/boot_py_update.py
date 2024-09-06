import os

def exist(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False
    
if exist("/system/temp/list.txt"):
    print("Update was alredy done")
else:
    if exist("/system/temp/update.py"):
        exec(open("/system/temp/update.py").read())