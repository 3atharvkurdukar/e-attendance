#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import time
from pyfingerprint.pyfingerprint import PyFingerprint
import I2C_LCD_driver
import pandas as pd


## Initialize LCD display
try: 
    mylcd = I2C_LCD_driver.lcd()
    mylcd.lcd_clear()
    mylcd.lcd_display_string('Initializing....', 1)

except Exception as e:
    print('The LCD could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Open workbook for reading
xl = pd.ExcelFiles('./database.xlsx')
dfStudent = xl.parse('student')
writer = pd.ExcelWriter('./database.xlsx')

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
        # Take user credentials
        row = len(dfStudent.index)
        dfStudent.iloc[row, 0] = int(input('Enter roll no: '))
        dfStudent.iloc[row, 1] = input('Enter firstname: ')
        dfStudent.iloc[row, 2] = input('Enter lastname: ')

        attempt = 0
        signatures = []
        positions = []

        while attempt < 3 and len(signatures) < 2:
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
                    break
                
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
                positions.append(f.storeTemplate())
                signatures.append(hashlib.sha256(str(f.downloadCharacteristics(0x01)).encode('utf-8')).hexdigest())

            except Exception as e:
                attempt += 1
                mylcd.lcd_clear()
                mylcd.lcd_display_string('     ERROR!     ', 1)
                time.sleep(1)
                print('Exception message: ' + str(e))
                mylcd.lcd_clear()
                mylcd.lcd_display_string(str(e)[:16], 1)
                mylcd.lcd_display_string(str(e)[16:], 2)
                print('Try again...')

        if (len(signatures) == 2):
            dfStudent.iloc[row, 3] = signatures[0]
            dfStudent.iloc[row, 4] = positions[0]
            dfStudent.iloc[row, 5] = signatures[1]
            dfStudent.iloc[row, 6] = positions[1]

            dfStudent.to_excel(writer, 'student', index=False)
            writer.save()
            
            print('Finger enrolled successfully!')
            mylcd.lcd_clear()
            mylcd.lcd_display_string('Enrolled at #' + positions, 1)
        else:
            print('Operation failed!')
            mylcd.lcd_clear()
            mylcd.lcd_display_string('     ERROR!     ', 1)
            time.sleep(1)
            print('Attempts expired')
            mylcd.lcd_clear()
            mylcd.lcd_display_string('Attempts expired', 1)

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

            name = 'Unknown'
            for i in range(len(dfStudent.index)):
                if (positionNumber == dfStudent.loc[i, 4] or positionNumber == dfStudent.loc[i, 6]):
                    name = str(dfStudent.loc[i, 1])
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
            rollno = int(input('Please enter the Roll No. to delete: '))
            for i in range(len(dfStudent.index)):
                if (rollno == dfStudent.loc[i, 0]):
                    positions.append(dfStudent.loc[i, 4])
                    positions.append(dfStudent.loc[i, 6])
                    break
            positionNumber = int(positionNumber)

            if ( f.deleteTemplate(positions[0]) == True  and f.deleteTemplate(positions[1] == True)):
                print('Template deleted!')

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
    
    else:
        mylcd.lcd_display_string('Exiting...',1,3)
        time.sleep(1)
        mylcd.lcd_clear()
        exit(0)
