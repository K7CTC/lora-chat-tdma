########################################################################
#                                                                      #
#          NAME:  PiERS Chat - Rich Console Setup                      #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 (beta)                                          #
#                                                                      #
########################################################################

#import from required 3rd party libraries
from rich.console import Console
from rich.theme import Theme

#establish singular console instance to be used throughout project
console = Console(theme=Theme(inherit=False))
