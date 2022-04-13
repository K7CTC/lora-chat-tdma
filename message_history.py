########################################################################
#                                                                      #
#          NAME:  PiERS Chat - Message History                         #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 (beta)                                          #
#                                                                      #
########################################################################

#import from project
from console import console, move_cursor
import db

#import from standard library
import datetime
import sqlite3
import time

console.clear()
console.show_cursor(False)

rowid_marker = 0

db = sqlite3.connect('piers.db')
c = db.cursor()

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

            #if record is lacks time_sent and time_received update rowid_marker and break
            if record[2] == None and record[4] == None:
                rowid_marker = int(record[0]) - 1
                break             
            
            print()
            if record[2] != None:
                unix_time_sent = int(record[2]) / 1000
                time_sent = datetime.datetime.fromtimestamp(unix_time_sent).strftime('%I:%M:%S %p')
                message_length = len(record[1])
                airtime_length = len(str(record[3]))
                right_align_air_time_whitespace = ' ' * (54 - airtime_length)
                if message_length <= 11:
                    right_align_whitespace = ' ' * 53
                    message_padding = ' ' * (11 - message_length)
                    print(f'{right_align_whitespace}┌─────────────┐')
                    print(f'{right_align_whitespace}│ {message_padding}{record[1]} │')
                    print(f'{right_align_whitespace}└┤{time_sent}├┘')
                    print(f'{right_align_air_time_whitespace}(Air Time: {record[3]}ms)')
                else:
                    right_align_length = 64 - message_length
                    right_align_whitespace = ' ' * right_align_length
                    border_top = '─' * message_length
                    border_bottom = '─' * (message_length - 12)
                    print(f'{right_align_whitespace}┌─{border_top}─┐')
                    print(f'{right_align_whitespace}│ {record[1]} │')
                    print(f'{right_align_whitespace}└─{border_bottom}┤{time_sent}├┘')
                    print(f'{right_align_air_time_whitespace}(Air Time: {record[3]}ms)')
            else:
                unix_time_received = int(record[4]) / 1000
                time_received = datetime.datetime.fromtimestamp(unix_time_received).strftime('%I:%M:%S %p')
                message_length = len(record[1])
                if message_length <= 11:
                    message_padding = ' ' * (11 - message_length)
                    print(f'┌─────────────┐')
                    print(f'│ {record[1]}{message_padding} │')
                    print(f'└┤{time_received}├┘')
                    print(f'(RSSI: {str(record[7])}   SNR: {str(record[8])})')
                else:
                    border_top = '─' * message_length
                    border_bottom = '─' * (message_length - 12)
                    print(f'┌─{border_top}─┐')
                    print(f'│ {record[1]} │')
                    print(f'└┤{time_received}├{border_bottom}─┘')
                    print(f'(RSSI: {str(record[7])}   SNR: {str(record[8])})')
            rowid_marker = record[0]
        time.sleep(1)
    except KeyboardInterrupt:
        print()
        break

c.close()
db.close()
console.show_cursor(True)
