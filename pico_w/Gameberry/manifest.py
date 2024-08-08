# Manifest file for Gameberry
# Version 0.8
# By Kitki30

# Main files:
freeze(".", "gameberry.py")
freeze(".", "boot.py")
freeze(".", "voltage_meter_mode.py")

# Boot config:
freeze(".", "boot_config.py")

# Default files:
freeze("default", "default/settings_default.py")

# Translations:
freeze("translations", "translations/en.py")
freeze("translations", "translations/pl.py")

# Web Setup:
freeze("webSetup", "webSetup/webSetup.py")

# Modules:
freeze("modules")