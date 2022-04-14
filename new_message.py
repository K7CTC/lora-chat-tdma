########################################################################
#                                                                      #
#          NAME:  PiERS Chat - New Message                             #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 (beta)                                          #
#                                                                      #
########################################################################

#import from project
from console import console
import db

#import from standard library
from time import sleep
import re

def message_is_valid(message):
    #only contain A-Z a-z 0-9 . ? ! and between 1 and 50 chars in length
    if re.fullmatch('^[a-zA-Z0-9!?. ]{1,50}$', message):
        return True
    else:
        return False

while True:
    try:
        console.clear()
        console.print('┌─┤ PiERS Chat - New Message ├─────────────────────────────────────────────────┐')
        console.print('│ Type a message between 1 and 50 characters then press enter. Your message    │')
        console.print('│ may only contain A-Z a-Z 0-9 and the following special characters:           │')
        console.print('│ period, question mark and exclamation mark                                   │')
        console.print('└──────────────────────────────────────────────────────────────────────────────┘')
        console.print('Press CTRL+C to quit.')
        console.print()
        message = input('New Outbound Message: ')
        if message_is_valid(message):
            db.insert_outbound_message(message)
        else:
            console.print()
            console.print('[bright_red][ERROR][/] Your message contained invalid characters or is of invalid length!')
            sleep(5)
    except KeyboardInterrupt:
        print()
        break
