import modules.json as json
import modules.files as files
import modules.customExceptions as exceptions
import network
import modules.requests as requests
import gc

translation = None
updatePath = "https://raw.githubusercontent.com/Kitki30/GameBerry/main/pico_w/Gameberry/translations/"

def load(lang):
    global translation
    translationFile = "/translations/"+lang+".json"
    if files.exist(translationFile):
        translation = json.read(translationFile)
        print("Translation loaded: "+lang+" "+translation["info"]["name"])
    else:
        raise exceptions.TranslationNotFound("Translation '"+lang+"' not found!")
        

def get(thing1, thing2):
    if translation == None:
        load("en")
        return translation["translation"][thing1][thing2]
    else:
        return translation["translation"][thing1][thing2]
    
def update(lang):
    gc.collect()
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected() == True:
        request = requests.GET(updatePath+lang+".json")
        if request.status_code == 200:
            if files.exist("/translations/"+lang+".json"):
                translation_json = json.read("/translations/"+lang+".json")
                request_json = request.json()
                print(request_json["info"]["version"])
                if request_json["info"]["version"] > translation_json["info"]["version"]:
                    print("Updating translation...")
                    with open('/translations/'+lang+".json", 'wb') as file:
                        file.write(request.content)
                    print("Done")
                    return True
                else:
                    return True
            else:
                print("Updating translation...")
                with open('/translations/'+lang+".json", 'wb') as file:
                    file.write(request.content)
                print("Done")
                return True

    else:
        raise exceptions.WifiNotConnected("Wi-Fi is not connected, cannot update Translations!")