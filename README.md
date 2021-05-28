# Raspberry Pi Python library for LCD5110 display module
This repository is a Raspberry Pi Python library for LCD 5110 (a.k.a. Nokia 5110 or PCD8544) display module.

There is also a related repository [Arduino library for LCD5110 display module](https://github.com/e-tinkers/LCD-5110-Arduino-library), both this and the Arduino library share common APIs.

## Hardware interface

This library utilises Raspberry Pi SPI0 interfaces together with other GPIO pins. The LCD module is connected with Raspbery Pi P1 header pins as follow:

| **LCD Pin** | **P1 header pin (BCM port)** |
|:-------:|:--------------------------:|  
|CLK |P1-23 (SPI0 - SCLK) |
|DN  |P1-19 (SPI0 - MOSI) |
|DC  |P1-26 (BCM 7) |
|RST |P1-21 (BCM 9) |
|SCE |P1-24 (BCM 8, SPI0 - CE0) |
|LED |P1-18 (BCM 24) |
|GND |P1-20 or P1-1 (GND) |
|VCC |P1-17 or P1-6 (3v3) |

* On some boards, P1-15 connects to LED pin via a 220-ohm resistor to restrict the LED current.
You need to try connecting LED to Vcc via ammeter -- if the current is less than 5mA, there 
is no need for the resistor. If the current is greater, you do need one.

## API for LCD5110 library


**lcd = LCD5110()**:

- Create an instance called lcd of class LCD5110\. The class __init__() construct will:

    1. initialise GPIO and SPI ports;
    2. clear the screen and internal display memory
    3. set cursor to row 1, col 1
    4. set LCD backlight = Off
    5. set LCD display mode = Normal


**LCD5110.clear()**
- Clear LCD screen and set cursor to row 1, col 1


**LCD5110.cursor(row, col)**
- Set LCD cursor to row (from 1 to 6), col (from 1 to 14)


**LCD5110.backlight(boolean true|false)**
- Set LCD backlight on (true) or off (false)


**LCD5110.lcdInverse(boolean true/false)**
- Set display mode to Inverse (true) or Normal (false)


**LCD5110.lcdprintStr(dataStr)**
- Print dataStr array on screen


**LCD5110.lcdprintImage(image)**
- Print image, image is an array[504] of pixels data

## More information

- [How to use LCD 5110 (PCD 8544) with Arduino](https://www.e-tinkers.com/2017/11/how-to-use-lcd-5110-pcd-8544-with-arduino/)
- [How to create Arduino Library from Arduino sketch](https://www.e-tinkers.com/2017/12/how-to-create-arduino-library-from-arduino-sketch/)
- [How to use LCD 5110 (PCD 8544) with Raspberry Pi](https://www.e-tinkers.com/2017/11/how-to-use-lcd-5110-pcd-8544-with-raspberry-pi/)
