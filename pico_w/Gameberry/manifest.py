# Manifest file for Gameberry
# Version 0.8
# By Kitki30

# Main files:
freeze(".", "gameberry.py")
freeze(".", "boot.py")
freeze(".", "voltage_meter_mode.py")

# Boot config:
freeze(".", "boot_config.json")

# Default files:
freeze("default")

# Translations:
freeze("translations")

# Web Setup:
freeze("webSetup")

# Modules:
freeze("modules")