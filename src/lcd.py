from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from time import sleep
import datetime


def setup_LCD():

    PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
    PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
    # Create PCF8574 GPIO adapter.
    try:
        mcp = PCF8574_GPIO(PCF8574_address)
    except:
        try:
            mcp = PCF8574_GPIO(PCF8574A_address)
        except:
            print('I2C Address Error !')
            exit(1)
    # Create LCD, passing in MCP GPIO adapter.
    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)

    mcp.output(3, 1)  # turn on LCD backlight
    lcd.begin(16, 2)  # set number of LCD lines and columns

    return mcp, lcd


def LCD_display(message, cursor_pointer, mcp, lcd):
    message = message.strip() + ' '
    if len(message) < 17:
        lcd.setCursor(0, cursor_pointer)
        lcd.message(message)
    else:
        while True:
            lcd.setCursor(0,cursor_pointer)
            lcd.message(message[:16])
            sleep(0.5)
            message = message[1:] + message[0]


def destroy_LCD(lcd):
    lcd.clear()


if __name__ == '__main__':
    mcp, lcd = setup_LCD()
    try:
            LCD_display("Hello PI", 1, mcp, lcd)
    except KeyboardInterrupt:
        destroy_LCD(lcd)
