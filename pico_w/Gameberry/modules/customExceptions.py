# Files
class FileCopyError(Exception):
    pass
class FileReadError(Exception):
    pass

# Data
class DataVerificationError(Exception):
    pass

# Translations
class TranslationNotFound(Exception):
    pass

# Defaults
class DefaultsNotFound(Exception):
    pass


# Wifi
class WifiNotConnected(Exception):
    pass

# Error screen
def ShowErrorScreen(lcd):
    lcd.setRGB(255,0,0)
    lcd.setCursor(0,0)
    lcd.printout("Cannot boot!")
    lcd.setCursor(0,1)
    lcd.printout("Connect debugger")