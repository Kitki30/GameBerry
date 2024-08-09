# Manifest file for Gameberry
# Version 0.8
# By Kitki30

# boot.py is appended to _boot.py and _boot_fat.py file included in micropython rp2 port.
# JSON and non .py files are converted to python file and frozen for faster reading.

# Main files:
freeze(".", "gameberry.py")
freeze(".", "voltage_meter_mode.py")

# Boot config:
freeze(".", "boot_config.py")

# Default files:
freeze("default", "settings_default.py")

# Translations:
freeze("translations", "en.py")
freeze("translations", "pl.py")

# Web Setup:
freeze("webSetup", "webSetup.py")

# Modules:
freeze("modules")