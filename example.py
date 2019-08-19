#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import time
from pyfingerprint.pyfingerprint import PyFingerprint
import I2C_LCD_driver
import xlrd


## Initialize LCD display
try: 
    mylcd = I2C_LCD_driver.lcd()
    mylcd.lcd_clear()
    mylcd.lcd_display_string('Initializing....', 1)

except Exception as e:
    print('The LCD could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Open workbook
loc = ('./sample.xlsx')
workbook = xlrd.open_workbook(loc)
sheet = workbook.sheet_by_index(0)

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

## Provide menu for menu-driven program
print('+-----------+')
print('| 1. Enroll |')
print('| 2. Search |')
print('| 3. Delete |')
print('| 4. Exit   |')
print('+-----------+')

mylcd.lcd_clear()
mylcd.lcd_display_string('1.Enroll ',1,2)
mylcd.lcd_display_string('2.Search ',2,2)
time.sleep(1)
mylcd.lcd_clear()
mylcd.lcd_display_string('3.Delete ',1,2)
mylcd.lcd_display_string('4.Exit ',2,2)
time.sleep(1)
mylcd.lcd_clear()

## Infinite menu-driven program
while True:
    mylcd.lcd_clear()
    mylcd.lcd_display_string('   Enter your   ',1)
    mylcd.lcd_display_string('     choice:    ',2)
    i = int(input('\nEnter your choice : '))
    mylcd.lcd_clear()
    
    if i == 1:      ## Enrolls new finger
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
                time.sleep(1)
                mylcd.clear()
                continue
            
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
            time.sleep(2)
            mylcd.lcd_clear()

        except Exception as e:
            print('Operation failed!')
            mylcd.lcd_clear()
            mylcd.lcd_display_string('     ERROR!     ', 1)
            time.sleep(1)
            print('Exception message: ' + str(e))
            mylcd.lcd_clear()
            mylcd.lcd_display_string(str(e)[:16], 1)
            mylcd.lcd_display_string(str(e)[16:], 2)
	    
        time.sleep(2)
        mylcd.lcd_clear()

    elif i == 2:    ## Searches for finger
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
                mylcd.lcd_display_string('No match found!')
                time.sleep(1)
                mylcd.lcd_clear()
                continue

            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))

            position = -1
            name = 'Unknown'
            for i in range(sheet.nrows):
                position = int(sheet.cell_value(i, 0))
                if (position == positionNumber):
                    name = str(sheet.cell_value(i, 1))
                    break
            print('Name: ' + name)

            mylcd.lcd_clear()
            mylcd.lcd_display_string(name[:16], 1)
            mylcd.lcd_display_string(name[16:], 2)
            time.sleep(2)
            mylcd.lcd_clear()
            mylcd.lcd_display_string('  Found at #' + str(positionNumber), 1)
            time.sleep(1)
            mylcd.lcd_clear()

            ## Loads the found template to charbuffer 1
            # f.loadTemplate(positionNumber, 0x01)

            ## Downloads the characteristics of template loaded in charbuffer 1
            # characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')

            ## Hashes characteristics of template
            # print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))

    elif i == 3:    ## Deletes a finger
        ## Gets some sensor information
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

        ## Tries to delete the template of the finger
        try:
            positionNumber = input('Please enter the template position you want to delete: ')
            positionNumber = int(positionNumber)

            if ( f.deleteTemplate(positionNumber) == True ):
                print('Template deleted!')

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
    
    else:
        mylcd.lcd_display_string('Exiting...',1,3)
        time.sleep(1)
        mylcd.lcd_clear()
        exit(0)
