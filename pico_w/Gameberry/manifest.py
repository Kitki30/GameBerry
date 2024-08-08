# Manifest file for Gameberry
# Version 0.8
# By Kitki30

# Main files:
freeze(".", "gameberry.py")
freeze(".", "boot.py")
freeze(".", "voltage_meter_mode.py")

# Boot config:
include(".", "boot_config.json")

# Default files:
include("default", "default/settings_default.json")

# Translations:
include("translations", "translations/en.json")
include("translations", "translations/pl.json")

# Web Setup:
freeze("webSetup", "webSetup/webSetup.py")

# Modules:
freeze("modules")