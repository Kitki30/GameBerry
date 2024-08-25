import os

def exist(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False
    
if exist("/system/temp/is_updated"):
    print("Update was alredy done")
else:
    exec(open("/system/temp/update.py").read())