#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
import I2C_LCD_driver
import time

## Search for a finger
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

## Tries to search the finger and calculate hash
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

    ## Searchs template
    result = f.searchTemplate()

    positionNumber = result[0]
    accuracyScore = result[1]

    if ( positionNumber == -1 ):
        print('No match found!')
        mylcd.lcd_clear()
        mylcd.lcd_display_string('No match found!', 1)
        exit(0)
    else:
        print('Found template at position #' + str(positionNumber))
        print('The accuracy score is: ' + str(accuracyScore))
        mylcd.lcd_clear()
        mylcd.lcd_display_string('  Found at #' + str(positionNumber), 1)

    ## OPTIONAL stuff
    ##

    ## Loads the found template to charbuffer 1
    f.loadTemplate(positionNumber, 0x01)

    ## Downloads the characteristics of template loaded in charbuffer 1
    characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')

    ## Hashes characteristics of template
    print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
