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
import re
import time

def message_is_valid(message):
    #only contain A-Z a-z 0-9 . ? ! and between 1 and 50 chars in length
    if re.fullmatch('^[a-zA-Z0-9!?. ]{1,50}$', message):
        return True
    else:
        return False

while True:
    try:
        console.clear()
        console.print('┌─┤PiERS Chat - New Message├───────────────────────────────────────┐')
        console.print('│ Type a message between 1 and 50 characters then press enter.     │')
        console.print('│ Your message may only contain A-Z a-Z 0-9 and the following      │')
        console.print('│ special characters: period, question mark and exclamation mark   │')
        console.print('└──────────────────────────────────────────────────────────────────┘')
        console.print('Press CTRL+C to quit.')
        console.print()
        message = input('Outbound Message: ')
        if message_is_valid(message):
            db.insert_outbound_message(message)
        else:
            console.print()
            console.print('[bright_red][ERROR][/] Your message contained invalid characters or is of invalid length!')
            time.sleep(5)
    except KeyboardInterrupt:
        print()
        break
