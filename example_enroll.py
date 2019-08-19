#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import time
from pyfingerprint.pyfingerprint import PyFingerprint
import I2C_LCD_driver


## Enrolls new finger
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
    mylcd.lcd_display_string('    Unable to   ', 1)
    mylcd.lcd_display_string('   initialize!  ', 2)
    print('Exception message: ' + str(e))
    exit(1)

## Gets some sensor information
template_count = f.getTemplateCount()
storage_capacity = f.getStorageCapacity()
print('Currently used templates: ' + str(template_count) +'/'+ str(storage_capacity))
mylcd.lcd_clear()
mylcd.lcd_display_string('Used: ' + str(template_count) +'/'+ str(storage_capacity), 1)
time.sleep(1)

## Tries to enroll new finger
try:
    print('Waiting for finger...')
    mylcd.lcd_clear()
    mylcd.lcd_display_string('   Waiting for  ', 1)
    mylcd.lcd_display_string('    finger...   ', 2)

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    ## Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        mylcd.lcd_clear()
        mylcd.lcd_display_string(' Already exists ', 1)
        mylcd.lcd_display_string('     at #' + str(positionNumber), 2)
        exit(0)

    print('Remove finger...')
    mylcd.lcd_clear()
    mylcd.lcd_display_string('Remove finger...', 1)
    time.sleep(2)

    print('Waiting for same finger again...')
    mylcd.lcd_clear()
    mylcd.lcd_display_string('   Waiting for  ', 1)
    mylcd.lcd_display_string('finger again....', 2)
    time.sleep(2)

    ## Wait that finger is read again
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

    ## Compares the charbuffers
    if ( f.compareCharacteristics() == 0 ):
        raise Exception('Fingers do not match')

    ## Creates a template
    f.createTemplate()

    ## Saves template at new position number
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    mylcd.lcd_clear()
    mylcd.lcd_display_string('Enrolled at #' + str(positionNumber), 1)

except Exception as e:
    print('Operation failed!')
    mylcd.lcd_clear()
    mylcd.lcd_display_string('    Operation   ', 1)
    mylcd.lcd_display_string('     Failed!    ', 2)
    time.sleep(1)
    print('Exception message: ' + str(e))
    mylcd.lcd_clear()
    mylcd.lcd_display_string(str(e)[:16], 1)
    mylcd.lcd_display_string(str(e)[16:], 2)
    exit(1)
