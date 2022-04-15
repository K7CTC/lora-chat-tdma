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
    console.print()
    console.print(' Firmware Version:')
    console.print('          EUI-64™:')
    console.print('        Frequency:')
    console.print('        Bandwidth:')
    console.print('         TX Power:')
    console.print(' Spreading Factor:')
    console.print('      Coding Rate:')
    console.print('     My Time Slot:')
    console.print('Current Time Slot:')
    console.print('     LoStik State:')

def lostik_service_insert_firmware_version():
    move_cursor(3,20)
    console.print(lostik_settings.FIRMWARE_VERSION)

def lostik_service_insert_hweui(hweui):
    move_cursor(4,20)
    console.print(hweui)

def lostik_service_insert_frequency():
    move_cursor(5,20)
    console.print(lostik_settings.FREQ_LABEL)

def lostik_service_insert_bandwidth():
    move_cursor(6,20)
    console.print(lostik_settings.BW_LABEL)

def lostik_service_insert_power(pwr):
    move_cursor(7,20)
    console.print(pwr)

def lostik_service_insert_spreading_factor():
    move_cursor(8,20)
    console.print(lostik_settings.SF_LABEL)

def lostik_service_insert_coding_rate():
    move_cursor(9,20)
    console.print(lostik_settings.CR_LABEL)

def lostik_service_insert_my_time_slot(my_time_slot):
    move_cursor(10,20)
    console.print(my_time_slot)

def lostik_service_update_current_time_slot(current_time_slot):
    move_cursor(11,20)
    console.print(current_time_slot)

def lostik_service_update_lostik_state(state):
    move_cursor(12,20)
    console.print(state)
