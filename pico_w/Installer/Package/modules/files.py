import os
import uos

def exist(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

def copy(source, target):
    try: 
        if os.stat(target)[0] & 0x4000:  # is directory
            target = target.rstrip("/") + "/" + source
    except OSError:
        pass
    with open(source, "rb") as source:
        with open(target, "wb") as target:
            while True:
                l = source.read(512)
                if not l: break
                target.write(l)

def create_folder(name):
    uos.mkdir(name)