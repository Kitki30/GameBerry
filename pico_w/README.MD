# Gameberry for Raspberry Pi Pico W

## Installation Guide

### Required hardware:
- Waveshare RGB1602 LCD Display
- 3 buttons (tact switch), 1 - Home Button and 2 button in other color than Home button
- Raspberry Pi Pico W
- Buzzer

This hardware is required for basic functions of Gameberry

### Optional hardware:
- SD / micro SD card breakout (Used for saving games (Save data can also be saved on internal storage), Booting Gameberry from SD card, Saving settings and more)
- Battery (For powering your Pico without cable, needs charger)
- INA219 (Used for checking battery voltage, current and power (not required even when you have battery))

### Installation:
1. Download latest micropython [here]()
2. If you have installed some other micropython firmware later on your Pico download flash_nuke.uf2 [here]() then hold BOOTSEL on your Pico and connect it to your PC then copy the file to RPI-RP2 volume
> [!WARNING]
> flash_nuke.uf2 file deletes all files on Pico storage, check if theres something important on it before flashing it!
3. Hold BOOTSEL button and connect your Pico to PC then copy micropython uf2 file to RPI-RP2 volume
4. Download and install thonny on your pc
5. Download install.py file from Github Releases and open it in thonny
> [!NOTE]
> install.py file is not available i will make the installer as fast as possible!
6. Set wifi password and ssid in the script
7. Run script

If installation completed without errors Pico should reboot by it self and 