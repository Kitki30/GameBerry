import modules.json as json
import modules.files as files
import modules.customExceptions as exceptions

translation = None

def load(lang):
    global translation
    translationFile = "/system/translations/"+lang+".json"
    if files.exist(translationFile):
        translation = json.read(translationFile)
        print(translation["translation"]["translations"]["translation_loaded"]+lang+" "+translation["info"]["name"])
    else:
        raise exceptions.TranslationNotFound("Translation '"+lang+"' not found!")

def loadExternal(path):
    global translation
    translationFile = path
    if files.exist(translationFile):
        translation = json.read(translationFile)
           

def get(thing1, thing2):
    if translation == None:
        load("en")
        return translation["translation"][thing1][thing2]
    else:
        return translation["translation"][thing1][thing2]