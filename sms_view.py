########################################################################
#                                                                      #
#          NAME:  LoRa Chat - View SMS                                 #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v1.0                                                 #
#   DESCRIPTION:  This module reads the sms table from lora_chat.db    #
#                 then prints the output to the console.               #
#                                                                      #
########################################################################

#import from project
import lcdb

#import from standard library
import datetime
import os
import sqlite3
import sys
import time

if lcdb.exists() == False:
    print('ERROR: File not found - lora_chat.db')
    sys.exit(1)

my_node_id = lcdb.my_node_id()
if my_node_id == None:
    print('ERROR: Unable to set node ID for this node!')
    sys.exit(1)

my_node_name = lcdb.my_node_name(my_node_id)

rowid_marker = 0

os.system('cls' if os.name == 'nt' else 'clear')

db = sqlite3.connect('lora_chat.db')
c = db.cursor()
c.execute('PRAGMA foreign_keys = ON')
while True:
    try:    
        #get all rows with rowid greater than rowid_marker
        c.execute('''
            SELECT
                sms.rowid,
                sms.node_id,
                nodes.node_name,
                sms.message,
                sms.time_sent,
                sms.air_time,
                sms.time_received,
                sms.rssi,
                sms.snr
            FROM
                sms
            NATURAL JOIN
                nodes
            WHERE
                sms.rowid>?;''',
                (rowid_marker,))
        for record in c.fetchall():
            #if record is lacks time_sent and time_received update rowid_marker and break
            if record[4] == None and record[6] == None:
                rowid_marker = int(record[0]) - 1
                break             
            print()
            if record[1] == my_node_id:
                unix_time_sent = int(record[4]) / 1000
                time_sent = datetime.datetime.fromtimestamp(unix_time_sent).strftime('%I:%M:%S %p')
                message_length = len(record[3])
                airtime_length = len(str(record[5]))
                right_align_air_time_whitespace = ' ' * (54 - airtime_length)
                if message_length <= 11:
                    right_align_whitespace = ' ' * 53
                    message_padding = ' ' * (11 - message_length)
                    print(f'{right_align_whitespace}┌─────────────┐')
                    print(f'{right_align_whitespace}│ {message_padding}{record[3]} │')
                    print(f'{right_align_whitespace}└┤{time_sent}├┘')
                    print(f'{right_align_air_time_whitespace}(Air Time: {record[5]}ms)')
                else:
                    right_align_length = 64 - message_length
                    right_align_whitespace = ' ' * right_align_length
                    border_top = '─' * message_length
                    border_bottom = '─' * (message_length - 12)
                    print(f'{right_align_whitespace}┌─{border_top}─┐')
                    print(f'{right_align_whitespace}│ {record[3]} │')
                    print(f'{right_align_whitespace}└─{border_bottom}┤{time_sent}├┘')
                    print(f'{right_align_air_time_whitespace}(Air Time: {record[5]}ms)')
            else:
                unix_time_received = int(record[6]) / 1000
                time_received = datetime.datetime.fromtimestamp(unix_time_received).strftime('%I:%M:%S %p')
                message_length = len(record[3])
                if message_length <= 11:
                    message_padding = ' ' * (11 - message_length)
                    print(f'┌─────────────┐')
                    print(f'│ {record[3]}{message_padding} │')
                    print(f'└┤{time_received}├┘')
                    print(f'{record[2]} (RSSI: {str(record[7])}   SNR: {str(record[8])})')
                else:
                    border_top = '─' * message_length
                    border_bottom = '─' * (message_length - 12)
                    print(f'┌─{border_top}─┐')
                    print(f'│ {record[3]} │')
                    print(f'└┤{time_received}├{border_bottom}─┘')
                    print(f'{record[2]} (RSSI: {str(record[7])}   SNR: {str(record[8])})')
            rowid_marker = record[0]
        time.sleep(1)
    except KeyboardInterrupt:
        print()
        break
c.close()
db.close()
sys.exit(0)