import RPi.GPIO as GPIO
import spidev

class LCD5110:

    LCD_WIDTH = 84
    LCD_HEIGHT = 48

    def __init__(self):
        # Define each P1 header pin
        self.RST = 21
        self.DC = 26
        self.LED = 18
        self.MOSI = 19  # DN on LCD module
        self.SCLK = 23
        # Note: when letting SPI controller manage CE, make sure the CE0 pin is in ALT0 mode
        # check: gpio readall
        # fix: gpio -g mode 8 alt1
        #self.CE0 = None  # Let SPI controller manage CE
        self.CE0 = 24   # SCE on LCD module

	# Backlight polarity. Red board are often active low, blue ones active high.
        self.LED_ACTIVE_LOW = True
        # Contrast (a.k.a. Vop), 0..127. 50 is a good default
        self.CONTRAST = 50

        self._inverse = False
        self._backlight = False
        self.spi = None
        self.reinit()

    def reinit(self):
        """Reinit and clear display"""
        assert 0 <= self.CONTRAST <= 127
        if self.spi:
           self.spi.close()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup([self.RST, self.DC, self.LED] + ([self.CE0] if self.CE0 is not None else []),
                   GPIO.OUT, initial=GPIO.LOW)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # open SPI0, use CE0 on GPIO as chip enable
        self.spi.max_speed_hz = 500*1000

        self.backlight(self._backlight)
        if self.CE0 is not None:
            GPIO.output(self.CE0, GPIO.HIGH)

        GPIO.output(self.RST, GPIO.HIGH)
        self._write(0, [0x21])  # Set Extended Command set
        self._write(0, [0x80 | self.CONTRAST])  # Set Vlcd (LCD Contrast)
        self._write(0, [0x13])  # Set voltage bias system 1: 48(Viewing Angle)
        self._write(0, [0x20])  # Set Normal Command set
        self.clear()         # Clear all display memory and set cursor to 1, 1
        self._write(0, [0x09])  # Set all pixels ON
        self._write(0, [0x0c])  # Set display mode to Normal

    def clear(self):
        self.cursor(0, 0)
        max_pixels = int(LCD5110.LCD_WIDTH * LCD5110.LCD_HEIGHT / 8)
        self._write(1, [0x00] * max_pixels)

    def cursor(self, row, col):
        if row not in range(1, int(LCD5110.LCD_HEIGHT / 8) + 1):
            return None
        if col not in range(1, int(LCD5110.LCD_WIDTH / 6) + 1):
            return None
        self._write(0, [0x40 | (row - 1),
                        0x80 | (col - 1) * 6])

    def _write(self, mode, data):
        if self.CE0 is not None:
            GPIO.output(self.CE0, GPIO.LOW)
        GPIO.output(self.DC, mode) # Data: mode = 0, Command: mode = 1
        if mode and self._inverse:
            data = [~x for x in data]
        self.spi.xfer(data)
        if self.CE0 is not None:
            GPIO.output(self.CE0, GPIO.HIGH)

    def backlight(self, state):
        self._backlight = state
        GPIO.output(self.LED, GPIO.HIGH if bool(state) != self.LED_ACTIVE_LOW else GPIO.LOW)

    def inverse(self, inv):
        self._inverse = inv

    def printStr(self, datastr):
        for ch in datastr:
            self._write(1,
               [FONT_TABLE[ord(ch) - 0x20][i] for i in range(5)] + [0])

    def printImage(self, image):
        self.cursor(1, 1)
        pixels = int(LCD5110.LCD_WIDTH * LCD5110.LCD_HEIGHT / 8)
        assert len(image) == pixels, 'Need %d elements in image, got %d' % (
           pixels, len(image))
        self._write(1, image)

FONT_TABLE = [
    [0x00, 0x00, 0x00, 0x00, 0x00],   # 0x20, space
    [0x00, 0x00, 0x5f, 0x00, 0x00],   # 0x21, !
    [0x00, 0x07, 0x00, 0x07, 0x00],   # 0x22, "
    [0x14, 0x7f, 0x14, 0x7f, 0x14],   # 0x23,   #
    [0x24, 0x2a, 0x7f, 0x2a, 0x12],   # 0x24, $
    [0x23, 0x12, 0x08, 0x64, 0x62],   # 0x25, %
    [0x36, 0x49, 0x55, 0x22, 0x50],   # 0x26, &
    [0x00, 0x05, 0x03, 0x00, 0x00],   # 0x27, '
    [0x00, 0x1c, 0x22, 0x41, 0x00],   # 0x28, (
    [0x00, 0x41, 0x22, 0x1c, 0x00],   # 0x29, )
    [0x14, 0x08, 0x3E, 0x08, 0x14],   # 0x2a, *
    [0x08, 0x08, 0x3E, 0x08, 0x08],   # 0x2b, +
    [0x00, 0x50, 0x30, 0x00, 0x00],   # 0x2c,,
    [0x08, 0x08, 0x08, 0x08, 0x08],   # 0x2d, -
    [0x00, 0x60, 0x60, 0x00, 0x00],   # 0x2e,.
    [0x20, 0x10, 0x08, 0x04, 0x02],   # 0x2f, /
    [0x3E, 0x51, 0x49, 0x45, 0x3E],   # 0x30, 0
    [0x00, 0x42, 0x7F, 0x40, 0x00],   # 0x31, 1
    [0x42, 0x61, 0x51, 0x49, 0x46],   # 0x32, 2
    [0x21, 0x41, 0x45, 0x4B, 0x31],   # 0x33, 3
    [0x18, 0x14, 0x12, 0x7F, 0x10],   # 0x34, 4
    [0x27, 0x45, 0x45, 0x45, 0x39],   # 0x35, 5
    [0x3C, 0x4A, 0x49, 0x49, 0x30],   # 0x36, 6
    [0x01, 0x71, 0x09, 0x05, 0x03],   # 0x37, 7
    [0x36, 0x49, 0x49, 0x49, 0x36],   # 0x38, 8
    [0x06, 0x49, 0x49, 0x29, 0x1E],   # 0x39, 9
    [0x00, 0x36, 0x36, 0x00, 0x00],   # 0x3a,:
    [0x00, 0x56, 0x36, 0x00, 0x00],   # 0x3b,;
    [0x08, 0x14, 0x22, 0x41, 0x00],   # 0x3c, <
    [0x14, 0x14, 0x14, 0x14, 0x14],   # 0x3d, =
    [0x00, 0x41, 0x22, 0x14, 0x08],   # 0x3e, >
    [0x02, 0x01, 0x51, 0x09, 0x06],   # 0x3f, ?
    [0x32, 0x49, 0x59, 0x51, 0x3E],   # 0x40, @
    [0x7E, 0x11, 0x11, 0x11, 0x7E],   # 0x41, A
    [0x7F, 0x49, 0x49, 0x49, 0x36],   # 0x42, B
    [0x3E, 0x41, 0x41, 0x41, 0x22],   # 0x43, C
    [0x7F, 0x41, 0x41, 0x22, 0x1C],   # 0x44, D
    [0x7F, 0x49, 0x49, 0x49, 0x41],   # 0x45, E
    [0x7F, 0x09, 0x09, 0x09, 0x01],   # 0x46, F
    [0x3E, 0x41, 0x49, 0x49, 0x7A],   # 0x47, G
    [0x7F, 0x08, 0x08, 0x08, 0x7F],   # 0x48, H
    [0x00, 0x41, 0x7F, 0x41, 0x00],   # 0x49, I
    [0x20, 0x40, 0x41, 0x3F, 0x01],   # 0x4a, J
    [0x7F, 0x08, 0x14, 0x22, 0x41],   # 0x4b, K
    [0x7F, 0x40, 0x40, 0x40, 0x40],   # 0x4c, L
    [0x7F, 0x02, 0x0C, 0x02, 0x7F],   # 0x4d, M
    [0x7F, 0x04, 0x08, 0x10, 0x7F],   # 0x4e, N
    [0x3E, 0x41, 0x41, 0x41, 0x3E],   # 0x4f, O
    [0x7F, 0x09, 0x09, 0x09, 0x06],   # 0x50, P
    [0x3E, 0x41, 0x51, 0x21, 0x5E],   # 0x51, Q
    [0x7F, 0x09, 0x19, 0x29, 0x46],   # 0x52, R
    [0x46, 0x49, 0x49, 0x49, 0x31],   # 0x53, S
    [0x01, 0x01, 0x7F, 0x01, 0x01],   # 0x54, T
    [0x3F, 0x40, 0x40, 0x40, 0x3F],   # 0x55, U
    [0x1F, 0x20, 0x40, 0x20, 0x1F],   # 0x56, V
    [0x3F, 0x40, 0x38, 0x40, 0x3F],   # 0x57, W
    [0x63, 0x14, 0x08, 0x14, 0x63],   # 0x58, X
    [0x07, 0x08, 0x70, 0x08, 0x07],   # 0x59, Y
    [0x61, 0x51, 0x49, 0x45, 0x43],   # 0x5a, Z
    [0x00, 0x7F, 0x41, 0x41, 0x00],   # 0x5b, [
    [0x55, 0x2A, 0x55, 0x2A, 0x55],   # 0x5c, back slash
    [0x00, 0x41, 0x41, 0x7F, 0x00],   # 0x5d,]
    [0x04, 0x02, 0x01, 0x02, 0x04],   # 0x5e, ^
    [0x40, 0x40, 0x40, 0x40, 0x40],   # 0x5f, _
    [0x00, 0x01, 0x02, 0x04, 0x00],   # 0x60, `
    [0x20, 0x54, 0x54, 0x54, 0x78],   # 0x61, a
    [0x7F, 0x48, 0x44, 0x44, 0x38],   # 0x62, b
    [0x38, 0x44, 0x44, 0x44, 0x20],   # 0x63, c
    [0x38, 0x44, 0x44, 0x48, 0x7F],   # 0x64, d
    [0x38, 0x54, 0x54, 0x54, 0x18],   # 0x65, e
    [0x08, 0x7E, 0x09, 0x01, 0x02],   # 0x66, f
    [0x0C, 0x52, 0x52, 0x52, 0x3E],   # 0x67, g
    [0x7F, 0x08, 0x04, 0x04, 0x78],   # 0x68, h
    [0x00, 0x44, 0x7D, 0x40, 0x00],   # 0x69, i
    [0x20, 0x40, 0x44, 0x3D, 0x00],   # 0x6a, j
    [0x7F, 0x10, 0x28, 0x44, 0x00],   # 0x6b, k
    [0x00, 0x41, 0x7F, 0x40, 0x00],   # 0x6c, l
    [0x7C, 0x04, 0x18, 0x04, 0x78],   # 0x6d, m
    [0x7C, 0x08, 0x04, 0x04, 0x78],   # 0x6e, n
    [0x38, 0x44, 0x44, 0x44, 0x38],   # 0x6f, o
    [0x7C, 0x14, 0x14, 0x14, 0x08],   # 0x70, p
    [0x08, 0x14, 0x14, 0x18, 0x7C],   # 0x71, q
    [0x7C, 0x08, 0x04, 0x04, 0x08],   # 0x72, r
    [0x48, 0x54, 0x54, 0x54, 0x20],   # 0x73, s
    [0x04, 0x3F, 0x44, 0x40, 0x20],   # 0x74, t
    [0x3C, 0x40, 0x40, 0x20, 0x7C],   # 0x75, u
    [0x1C, 0x20, 0x40, 0x20, 0x1C],   # 0x76, v
    [0x3C, 0x40, 0x30, 0x40, 0x3C],   # 0x77, w
    [0x44, 0x28, 0x10, 0x28, 0x44],   # 0x78, x
    [0x0C, 0x50, 0x50, 0x50, 0x3C],   # 0x79, y
    [0x44, 0x64, 0x54, 0x4C, 0x44],   # 0x7a, z
    [0x00, 0x08, 0x36, 0x41, 0x00],   # 0x7b, {
    [0x00, 0x00, 0x7f, 0x00, 0x00],   # 0x7c, |
    [0x00, 0x41, 0x36, 0x08, 0x00],   # 0x7d,}
    [0x10, 0x08, 0x08, 0x10, 0x08],   # 0x7e, ~
    [0x78, 0x46, 0x41, 0x46, 0x78]    # 0x7f, DEL
]
