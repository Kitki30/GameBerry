# Manifest file for Gameberry
# Version 0.8
# By Kitki30

# Main files:
freeze(".", "gameberry.py")
freeze("_boot.py")
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