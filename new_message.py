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
import ui

#import from standard library
import re

def message_is_valid(message):
    #only contain A-Z a-z 0-9 . ? ! and between 1 and 50 chars in length
    if re.fullmatch('^[a-zA-Z0-9!?. ]{1,50}$', message):
        return True
    else:
        return False

console.clear()
console.show_cursor(False)
ui.splash()
ui.new_message_static_content()
console.show_cursor(True)

while True:
    try:
        ui.move_cursor(6,19)
        message = input()
        ui.move_cursor(6,19)
        console.print('                                                              ')
        if message_is_valid(message):
            db.insert_outbound_message(message)
        else:
            ui.new_message_invalid()
    except KeyboardInterrupt:
        break

console.clear()
