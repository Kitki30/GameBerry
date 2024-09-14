def default(lcd):
    degree_char = [
      0b00111,
      0b00101,
      0b00111,
      0b00000,
      0b00000,
      0b00000,
      0b00000,
      0b00000
    ]
    heart_char = [
      0b00000,
      0b01010,
      0b11111,
      0b11111,
      0b01110,
      0b00100,
      0b00000,
      0b00000
    ]
    sadFace_char = [
      0b00000,
      0b01010,
      0b00000,
      0b01110,
      0b10001,
      0b00000,
      0b00000,
      0b00000
    ]
    happyFace_char = [
      0b00000,
      0b01010,
      0b00000,
      0b10001,
      0b01110,
      0b00000,
      0b00000,
      0b00000
    ]
    checkmark_char = [
      0b00000,
      0b00001,
      0b00010,
      0b10100,
      0b01000,
      0b00000,
      0b00000,
      0b00000
    ]
    x_char = [
      0b00000,
	    0b00000,
	    0b01010,
	    0b00100,
	    0b01010,
	    0b00000,
	    0b00000,
	    0b00000
    ]
    onff = [
      0b00000,
      0b00000,
      0b00100, 
      0b10101, 
      0b10101, 
      0b10001, 
      0b01110, 
      0b00000 
    ]
    full_char = [
        0b11111,
	    0b11111,
	    0b11111,
	    0b11111,
	    0b11111,
	    0b11111,
	    0b11111,
	    0b11111
    ]
    lcd.create_custom_char(0,degree_char)
    lcd.create_custom_char(1,heart_char)
    lcd.create_custom_char(2,sadFace_char)
    lcd.create_custom_char(3,happyFace_char)
    lcd.create_custom_char(4,checkmark_char)
    lcd.create_custom_char(5,x_char)
    lcd.create_custom_char(6,onff)
    lcd.create_custom_char(7,full_char)