import time

def play(lcd, line, text, delay):
    lenght = len(text)
    cursor = 0
    lcd.setCursor(0,line)
    while cursor is not lenght:
        lcd.setCursor(cursor,line)
        lcd.printout(str(text[cursor]))
        cursor = cursor + 1
        time.sleep(delay)