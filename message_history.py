########################################################################
#                                                                      #
#          NAME:  PiERS Chat - Message History                         #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 (beta)                                          #
#                                                                      #
########################################################################

#import from project
from console import console
import db

#import from standard library
from datetime import datetime
from time import sleep
import sqlite3

console.clear()
console.show_cursor(False)

rowid_marker = 0

piers_db = sqlite3.connect('piers.db')
c = piers_db.cursor()

while True:
    try:    
        #get all rows with rowid greater than rowid_marker
        c.execute('''
            SELECT
                rowid,
                message,
                time_sent,
                air_time,
                time_received,
                rssi,
                snr
            FROM
                messages
            WHERE
                rowid>?''',
            (rowid_marker,))
        for record in c.fetchall():
            
            if record[2] == None and record[4] == None:
                rowid_marker = int(record[0]) - 1
                break                        
            
            message_length = len(record[1])
            if message_length <= 11:
                border_top = '─' * 13
                border_bottom = '─'
                message_padding = ' ' * (11 - message_length)
            else:
                border_top = '─' * (message_length + 2)
                border_bottom = '─' * (message_length - 10)
                message_padding = ''
            if record[2] != None: #outbound message - align right
                unix_time_sent = int(record[2]) / 1000
                time_sent = datetime.fromtimestamp(unix_time_sent).strftime('%I:%M:%S %p')
                airtime_length = len(str(record[3]))
                console.print(f'[dodger_blue1]╭{border_top}╮[/]', justify='right')
                console.print(f'[dodger_blue1]│[/] {message_padding}{record[1]} [dodger_blue1]│[/]', justify='right')
                console.print(f'[dodger_blue1]╰{border_bottom}[/]{time_sent}[dodger_blue1]─┘[/]', justify='right')
                console.print(f'[bright_black](Air Time: {record[3]}ms)[/]', justify='right')
            else: #inbound message - align blue
                unix_time_received = int(record[4]) / 1000
                time_received = datetime.fromtimestamp(unix_time_received).strftime('%I:%M:%S %p')
                console.print(f'[green3]╭{border_top}╮[/]')
                console.print(f'[green3]│[/] {record[1]}{message_padding} [green3]│[/]')
                console.print(f'[green3]└─[/]{time_received}[green3]{border_bottom}╯[/]')
                console.print(f'[bright_black](RSSI: {str(record[5])}   SNR: {str(record[6])})[/]')
            rowid_marker = record[0]
        sleep(1)
    except KeyboardInterrupt:
        console.print()
        total_air_time = db.get_total_air_time()
        total_air_time = total_air_time / 1000
        console.print(f'Total Air Time: {total_air_time} seconds')
        break

c.close()
piers_db.close()
console.show_cursor(True)
