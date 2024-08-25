import time

# INA219 default address
INA219_ADDRESS = 0x40

# Registers
REG_CONFIG = 0x00
REG_SHUNTVOLTAGE = 0x01
REG_BUSVOLTAGE = 0x02
REG_POWER = 0x03
REG_CURRENT = 0x04
REG_CALIBRATION = 0x05

# Config register bits
CONFIG_RESET = 0x8000
CONFIG_BVOLTAGERANGE_32V = 0x2000
CONFIG_GAIN_8_320MV = 0x1800
CONFIG_BADCRES_12BIT = 0x0180
CONFIG_SADCRES_12BIT_1S_532US = 0x0078
CONFIG_MODE_SANDBVOLT_CONTINUOUS = 0x0007

# Calibration value for a 0.1 ohm shunt resistor and max current of 3.2A
CALIBRATION_VALUE = 4096

# Constants
SHUNT_RESISTANCE = 0.1  # Ohms
CURRENT_LSB = 0.1       # mA per bit

class INA219:
    def __init__(self, shunt_ohms, i2c, addr=INA219_ADDRESS):
        self.i2c = i2c
        self.addr = addr
        self.shunt_ohms = shunt_ohms
        self.calibration_value = CALIBRATION_VALUE
        self.configure()

    def write_register(self, reg, value):
        data = [(value >> 8) & 0xFF, value & 0xFF]
        self.i2c.writeto_mem(self.addr, reg, bytes(data))

    def read_register(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        return (data[0] << 8) | data[1]

    def configure(self):
        # Reset the INA219
        self.write_register(REG_CONFIG, CONFIG_RESET)
        time.sleep(0.1)
        
        config = (CONFIG_BVOLTAGERANGE_32V | CONFIG_GAIN_8_320MV |
                  CONFIG_BADCRES_12BIT | CONFIG_SADCRES_12BIT_1S_532US |
                  CONFIG_MODE_SANDBVOLT_CONTINUOUS)
        self.write_register(REG_CONFIG, config)
        
        # Set calibration
        self.write_register(REG_CALIBRATION, self.calibration_value)

    def shunt_voltage(self):
        value = self.read_register(REG_SHUNTVOLTAGE)
        if value > 32767:
            value -= 65536
        return value * 0.01  # mV

    def bus_voltage(self):
        value = self.read_register(REG_BUSVOLTAGE)
        return (value >> 3) * 0.004  # V
  # V

    def current(self):
        self.write_register(REG_CALIBRATION, self.calibration_value)
        value = self.read_register(REG_CURRENT)
        if value > 32767:
            value -= 65536
        return value * CURRENT_LSB  # mA

    def power(self):
        value = self.read_register(REG_POWER)
        return value * 20  # mW
