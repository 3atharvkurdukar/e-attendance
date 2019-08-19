import I2C_LCD_driver
import time

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_clear()
time.sleep(2)
mylcd.lcd_display_string("Hello World!", 1, 2)
time.sleep(2)
mylcd.lcd_clear()
mylcd.lcd_display_string("Jalwa!", 1, 5)
time.sleep(2)

