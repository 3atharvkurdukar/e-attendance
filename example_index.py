#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

from pyfingerprint.pyfingerprint import PyFingerprint
import I2C_LCD_driver


## Shows the template index table
##

## Initialize LCD display
mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_clear()
mylcd.lcd_display_string('Initializing....', 1)

## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    mylcd.lcd_clear()
    mylcd.lcd_display_string('Unable to initialize!')
    print('Exception message: ' + str(e))
    exit(1)

## Gets some sensor information
template_count = f.getTemplateCount()
storage_capacity = f.getStorageCapacity()
print('Currently used templates: ' + str(template_count) +'/'+ str(storage_capacity))
mylcd.lcd_clear()
mylcd.lcd_display_string('Used: ' + str(template_count) +'/'+ str(storage_capacity))

## Tries to show a template index table page
try:
    page = input('Please enter the index page (0, 1, 2, 3) you want to see: ')
    page = int(page)

    tableIndex = f.getTemplateIndex(page)

    for i in range(0, len(tableIndex)):
        print('Template at position :' + str(i) + ' is used: ' + str(tableIndex[i]))

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
