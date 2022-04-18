########################################################################
#                                                                      #
#          NAME:  PiERS Chat - UI Functions                            #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 (beta)                                          #
#                                                                      #
########################################################################

#import from project library
from console import console
import lostik_settings

#import from standard library
from time import sleep

total_air_time = 0

def move_cursor(row, column):
    print(f'\033[{row};{column}H', end='')

def lostik_service_static_content():
    console.clear()
    console.print('[white on deep_sky_blue4] ⣿ PiERS Chat v2.0 (beta)  ❭❭❭  TDMA LoStik Service                             [/]')
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
    console.print('   Total Air Time:')
    console.print()
    console.print('[grey30]Press CTRL+C to quit.[/]')

def new_message_static_content():
    console.clear()
    console.print('[white on deep_sky_blue4] ⣿ PiERS Chat v2.0 (beta)  ❭❭❭  New Message                                     [/]')
    console.print('Type a message between 1 and 50 characters then press enter. Your message may   ')
    console.print('only contain A-Z a-Z 0-9 and the following special characters:                  ')
    console.print('period, question mark and exclamation mark                                      ')
    console.print('[deep_sky_blue4]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]')
    console.print('Outbound Message:')
    console.print()
    console.print('[grey30]Press CTRL+C to quit.[/]')

def new_message_invalid():
    console.show_cursor(False)
    move_cursor(6,1)
    console.print('[bright_red][ERROR][/] Your message contained invalid characters or is of invalid length!      ')
    sleep(5)
    move_cursor(6,1)
    console.print('Outbound Message:                                                               ')
    console.show_cursor(True)
    
def lostik_service_insert_firmware_version():
    move_cursor(2,20)
    console.print(lostik_settings.FIRMWARE_VERSION)

def lostik_service_insert_hweui(hweui):
    move_cursor(3,20)
    console.print(hweui)

def lostik_service_insert_frequency():
    move_cursor(4,20)
    console.print(lostik_settings.FREQ_LABEL)

def lostik_service_insert_bandwidth():
    move_cursor(5,20)
    console.print(lostik_settings.BW_LABEL)

def lostik_service_insert_power(pwr):
    move_cursor(6,20)
    console.print(pwr)

def lostik_service_insert_spreading_factor():
    move_cursor(7,20)
    console.print(lostik_settings.SF_LABEL)

def lostik_service_insert_coding_rate():
    move_cursor(8,20)
    console.print(lostik_settings.CR_LABEL)

def lostik_service_insert_my_time_slot(my_time_slot):
    move_cursor(9,20)
    if my_time_slot == 1:
        console.print('TS1')
    elif my_time_slot == 2:
        console.print('TS2')

def lostik_service_update_current_time_slot(current_time_slot):
    move_cursor(10,20)
    if current_time_slot == 1:
        console.print('TS1', style='r', end='')
        console.print(' TS2')
    elif current_time_slot == 2:
        console.print('TS1 ', end='')
        console.print('TS2', style='r')
 
def lostik_service_update_lostik_state(state):
    move_cursor(11,20)
    if state == 'tx':
        console.print('[bright_red]●[/]')
    elif state == 'rx':
        console.print('[bright_blue]●[/]')
    elif state == 'idle':
        console.print('[bright_black]◌[/]')

def lostik_service_update_total_air_time(last_tx_air_time):
    move_cursor(12,20)
    global total_air_time
    total_air_time += last_tx_air_time
    total_air_time_seconds = total_air_time / 1000
    console.print(f'{total_air_time_seconds} seconds')
   
def splash():
    move_cursor(15,27)
    console.print('[grey70]C h r i s    C l e m e n t[/]') 
    
    callsign_elements = [
        '▰▰   ▰▰',
        '▰▰  ▰▰ ',
        '▰▰▰▰▰',
        '▰▰▰▰▰▰▰',
        '▰    ▰▰',
        '    ▰▰',
        '   ▰▰',
        ' ▰▰▰▰▰▰',
        '▰▰',
        '▰▰▰▰▰▰▰▰',
        '   ▰▰'
    ]
    
    frame_delay = .03

    #K
    move_cursor(9, 16)
    console.print(callsign_elements[0], style='color(26)')
    sleep(frame_delay)
    move_cursor(10, 16)
    console.print(callsign_elements[1], style='color(32)')
    sleep(frame_delay)
    move_cursor(11, 16)
    console.print(callsign_elements[2], style='color(38)')
    sleep(frame_delay)
    move_cursor(12, 16)
    console.print(callsign_elements[1], style='color(32)')
    sleep(frame_delay)
    move_cursor(13, 16)
    console.print(callsign_elements[0], style='color(26)')
    sleep(frame_delay)
    
    #7
    move_cursor(13, 26)
    console.print(callsign_elements[6], style='color(26)')
    sleep(frame_delay)
    move_cursor(12, 26)
    console.print(callsign_elements[6], style='color(32)')
    sleep(frame_delay)
    move_cursor(11, 26)
    console.print(callsign_elements[5], style='color(38)')
    sleep(frame_delay)
    move_cursor(10, 26)
    console.print(callsign_elements[4], style='color(32)')
    sleep(frame_delay)
    move_cursor(9, 26)
    console.print(callsign_elements[3], style='color(26)')
    sleep(frame_delay)
    
    #C
    move_cursor(9, 36)
    console.print(callsign_elements[7], style='color(26)')
    sleep(frame_delay)
    move_cursor(10, 36)
    console.print(callsign_elements[8], style='color(32)')
    sleep(frame_delay)
    move_cursor(11, 36)
    console.print(callsign_elements[8], style='color(38)')
    sleep(frame_delay)
    move_cursor(12, 36)
    console.print(callsign_elements[8], style='color(32)')
    sleep(frame_delay)
    move_cursor(13, 36)
    console.print(callsign_elements[7], style='color(26)')
    sleep(frame_delay)
    
    #T
    move_cursor(13, 46)
    console.print(callsign_elements[10], style='color(26)')
    sleep(frame_delay)
    move_cursor(12, 46)
    console.print(callsign_elements[10], style='color(32)')
    sleep(frame_delay)
    move_cursor(11, 46)
    console.print(callsign_elements[10], style='color(38)')
    sleep(frame_delay)
    move_cursor(10, 46)
    console.print(callsign_elements[10], style='color(32)')
    sleep(frame_delay)
    move_cursor(9, 46)
    console.print(callsign_elements[9], style='color(26)')
    sleep(frame_delay)
    
    #C
    move_cursor(9, 57)
    console.print(callsign_elements[7], style='color(26)')
    sleep(frame_delay)
    move_cursor(10, 57)
    console.print(callsign_elements[8], style='color(32)')
    sleep(frame_delay)
    move_cursor(11, 57)
    console.print(callsign_elements[8], style='color(38)')
    sleep(frame_delay)
    move_cursor(12, 57)
    console.print(callsign_elements[8], style='color(32)')
    sleep(frame_delay)
    move_cursor(13, 57)
    console.print(callsign_elements[7], style='color(26)')
    sleep(frame_delay)
    
    sleep(.5)

    move_cursor(19,30)
    console.print('[grey70]Proudly presents...[/]')

    sleep(1.5)
    console.clear()
    sleep(1)

    def logo_print_line(line, color):
        lines = [
            '╭─────────╮  ╭─╮  ╭─────────╮  ╭─────────╮  ╭─────────╮',
            '╰──────╮  │  ╰─╯  ╰─────────╯  ╰──────╮  │  │ ╭───────╯',
            '╭──────╯  │  ╭─╮  ╭───────╮    ╭──────╯  │  │ ╰───────╮',
            '│ ╭───────╯  │ │  │ ╭─────╯    │ ╭────╮  ⎨  ╰──────╮  │',
            '│ │          │ │  │ ╰───────╮  │ │    │  │  ╭──────╯  │',
            '╰─╯          ╰─╯  ╰─────────╯  ╰─╯    ╰──╯  ╰─────────╯'
        ]
        style = f'color({color})'
        if color == 0:
            lines[line] = '                                                       '
        row = line + 8
        column = 14
        move_cursor(row, column)
        console.print(lines[line], style=style)

    frame_delay = .06

    move_cursor(24,20)
    console.print('[grey30]Copyright © 2017-2022 Chris Clement (K7CTC)[/]')

    logo_print_line(0, 235)
    sleep(frame_delay)

    logo_print_line(1, 235)
    logo_print_line(0, 231)
    sleep(frame_delay)

    logo_print_line(2, 235)
    logo_print_line(1, 231)
    logo_print_line(0, 249)
    sleep(frame_delay)

    logo_print_line(3, 235)
    logo_print_line(2, 231)
    logo_print_line(1, 249)
    logo_print_line(0, 244)
    sleep(frame_delay)

    logo_print_line(4, 235)
    logo_print_line(3, 231)
    logo_print_line(2, 249)
    logo_print_line(1, 244)
    logo_print_line(0, 239)
    sleep(frame_delay)

    logo_print_line(5, 235)
    logo_print_line(4, 231)
    logo_print_line(3, 249)
    logo_print_line(2, 244)
    logo_print_line(1, 239)
    logo_print_line(0, 235)
    sleep(frame_delay)

    logo_print_line(5, 231)
    logo_print_line(4, 249)
    logo_print_line(3, 244)
    logo_print_line(2, 239)
    logo_print_line(1, 235)
    logo_print_line(0, 0)
    sleep(frame_delay)

    logo_print_line(5, 249)
    logo_print_line(4, 244)
    logo_print_line(3, 239)
    logo_print_line(2, 235)
    logo_print_line(1, 0)
    sleep(frame_delay)

    logo_print_line(5, 244)
    logo_print_line(4, 239)
    logo_print_line(3, 235)
    logo_print_line(2, 0)
    sleep(frame_delay)

    logo_print_line(5, 239)
    logo_print_line(4, 235)
    logo_print_line(3, 0)
    sleep(frame_delay)

    logo_print_line(5, 235)
    logo_print_line(4, 0)
    sleep(frame_delay)

    logo_print_line(5, 0)

    sleep(.25)

    frame_delay = .12

    logo_print_line(0, 235)
    logo_print_line(1, 235)
    logo_print_line(2, 235)
    logo_print_line(3, 235)
    logo_print_line(4, 235)
    logo_print_line(5, 235)
    sleep(frame_delay)

    logo_print_line(0, 231)
    logo_print_line(1, 231)
    logo_print_line(2, 231)
    logo_print_line(3, 231)
    logo_print_line(4, 231)
    logo_print_line(5, 231)
    sleep(frame_delay)

    logo_print_line(0, 253)
    logo_print_line(1, 253)
    logo_print_line(2, 253)
    logo_print_line(3, 253)
    logo_print_line(4, 253)
    logo_print_line(5, 253)
    sleep(frame_delay)

    logo_print_line(0, 249)
    logo_print_line(1, 249)
    logo_print_line(2, 249)
    logo_print_line(3, 249)
    logo_print_line(4, 249)
    logo_print_line(5, 249)

    sleep(.25)

    def title_print_line(color):
        style = f'color({color})'
        row = 15
        column = 22
        move_cursor(row, column)
        console.print('The Raspberry Pi Event Reporting System', style=style)

    title_print_line(235)
    sleep(frame_delay)

    title_print_line(231)
    sleep(frame_delay)

    title_print_line(253)
    sleep(frame_delay)

    title_print_line(249)

    sleep(3)
