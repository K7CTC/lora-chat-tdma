########################################################################
#                                                                      #
#          NAME:  PiERS Chat - UI Functions                            #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 beta                                            #
#                                                                      #
########################################################################

#import from project library
from console import console
import lostik_settings

def move_cursor(row, column):
    print(f'\033[{row};{column}H', end='')

def lostik_service_static_content():
    console.clear()
    console.print('PiERS Chat - TDMA LoStik Service')
    console.print('        Frequency:')
    console.print('        Bandwidth:')
    console.print('         TX Power:')
    console.print(' Spreading Factor:')
    console.print('      Coding Rate:')
    console.print('     LoStik State:')
    console.print('Current Time Slot:')
    console.print(' Firmware Version:')

def lostik_service_insert_firmware_version():
    move_cursor(9,20)
    console.print(lostik_settings.FIRMWARE_VERSION)