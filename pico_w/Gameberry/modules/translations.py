import modules.json as json
import modules.files as files
import modules.customExceptions as exceptions
import network
import modules.requests as requests
import modules.files as files

translation = None
updatePath = "https://raw.githubusercontent.com/Kitki30/GameBerry/main/pico_w/Gameberry/translations/"

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
        request = requests.GET(updatePath+lang+".json")
        if request.status_code == 200:
            if files.exist("/translations/"+lang+".json"):
                translation_json = json.read("/translations/"+lang+".json")
                request_json = request.json()
                if translation_json["info"]["version"] < request_json["info"]["version"]:
                    print("Updating translation...")
                else:
                    return True
            else:
                with open('/translations/'+lang+".json", 'wb') as file:
                    file.write(request.content)

    else:
        raise exceptions.WifiNotConnected("Wi-Fi is not connected, cannot update Translations!")