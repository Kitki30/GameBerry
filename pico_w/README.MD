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
1. Download latest micropython [here](https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2)
3. Hold BOOTSEL button and connect your Pico to PC then copy micropython uf2 file to RPI-RP2 volume
4. Download and install thonny on your pc
5. Download install.py file from Github
6. Set wifi password and ssid in the script
7. Run script
> [!WARNING]
> Install.py script will delete every file on the flash of device!

If installation completed without errors Pico should reboot by it self and 