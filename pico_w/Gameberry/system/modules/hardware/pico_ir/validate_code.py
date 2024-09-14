class InvalidCodeException(Exception):
    def __init__(self, message="Invalid IR code"):
        self.message = message
        super().__init__(self.message)


def validate_code(code):
    # Ensure the code is a 32-bit binary string
    code_bin = f"{code:032b}"  # Convert the code to a 32-bit binary string

    # Check if code length is exactly 32 bits
    if len(code_bin) != 32:
        raise InvalidCodeException("Code must be exactly 32 bits long")

    # Check that the second 8 bits are the inverse of the first 8 bits (device address check)
    for i in range(8):
        if code_bin[i] == code_bin[i + 8]:
            raise InvalidCodeException("Device address and its inverse do not match")

    # Check that the fourth 8 bits are the inverse of the third 8 bits (command check)
    for i in range(16, 24):
        if code_bin[i] == code_bin[i + 8]:
            raise InvalidCodeException("Command and its inverse do not match")

    print("Code is valid")
