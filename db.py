########################################################################
#                                                                      #
#          NAME:  PiERS Chat - Database Functions                      #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 beta                                            #
#                                                                      #
########################################################################

import os
import sqlite3
import time
from pathlib import Path

#this module is not intended for direct execution
if __name__ == '__main__':
    print('ERROR: db.py is not intended for direct execution!')

#create db if it doesn't already exist
if Path('piers.db').is_file() == False:
    db = sqlite3.connect('piers.db')
    db.execute('''
        CREATE TABLE messages (
            message	        TEXT NOT NULL,
            time_sent	    INTEGER,
            air_time	    INTEGER,
            time_received   INTEGER,
            rssi            INTEGER,
            snr             INTEGER
        )''')
    db.commit()
    db.close()

#function: create outgoing message record
# accepts: validated message
def insert_outbound_message(message):
    db = sqlite3.connect('piers.db')
    db.execute('INSERT INTO messages (message) VALUES (?)', (message,))
    db.commit()
    db.close()

#TESTED TO HERE#

#function: get next outbound message
# returns: rowid integer and message string or none
def get_next_outbound_message():
    db = sqlite3.connect('piers.db')
    c = db.cursor()       
    c.execute('''
        SELECT
            rowid,
            message,
            time_sent
        FROM
            messages
        WHERE
            time_sent IS NULL
        ''')
    record = c.fetchone()
    c.close()
    db.close()
    if record:
        return record[0], record[1]
    else:
        return None, None

#function: update database after successful transmit
# accepts: rowid, time_sent and air_time
# returns: boolean
def update_outbound_message(rowid,time_sent,air_time):
    db = sqlite3.connect('piers.db')
    c = db.cursor()
    c.execute('''
        UPDATE
            messages
        SET
            time_sent=?,
            air_time=?
        WHERE
            rowid=?''',
        (time_sent,air_time,rowid))
    db.commit()
    c.close()
    db.close()
    return True

#function: create received message record
# accepts: payload_hex, rssi and snr
def insert_inbound_message(message,rssi,snr):
    db = sqlite3.connect('piers.db')
    c = db.cursor()
    time_received = int(round(time.time()*1000))
    c.execute('''
        INSERT INTO messages (
            message,
            time_received,
            rssi,
            snr)
        VALUES (?, ?, ?, ?)''',
        (message, time_received, rssi, snr))
    db.commit()
    c.close()
    db.close()
