import modules.json as json
import modules.files as files
import modules.customExceptions as exceptions
import network

translation = None

def load(lang = "en"):
    global translation
    translationFile = "/translations/"+lang+".json"
    if files.exist(translationFile):
        translation = json.read(translationFile)
        print("Translation loaded: "+lang+" "+translation["info"]["name"])
    else:
        raise exceptions.TranslationNotFound("Translation '"+lang+"' not found!")
        

def get(thing):
    if translation == None:
        load("en")
        return translation["translation"][thing]
    else:
        return translation["translation"][thing]
    
def update(lang = "en"):
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected() == True:
        # Do update logic
        return True
    else:
        raise exceptions.WifiNotConnected("Wi-Fi is not connected, cannot update Translations!")