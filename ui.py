########################################################################
#                                                                      #
#          NAME:  PiERS Chat - UI Functions                            #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 beta                                            #
#                                                                      #
########################################################################

from console import console

def move_cursor(row, column):
    print(f'\033[{row};{column}H', end='')

