import modules.json as json
import modules.files as files
import modules.customExceptions as exceptions
import network
import modules.requests as requests
import gc
import translations.pl
import translations.en

translation = None

def load(lang):
    global translation
    if lang == "pl":
        translation = json.read_from_string(translations.pl.data())
    elif lang == "en":
        translation = json.read_from_string(translations.en.data())

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