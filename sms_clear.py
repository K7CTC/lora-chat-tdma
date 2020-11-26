########################################################################
#                                                                      #
#          NAME:  LoRa Chat - Clear SMS Table                          #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v1.0                                                 #
#   DESCRIPTION:  This module drops and recreates the sms table from   #
#                 lora_chat.db thus purging chat history.              #
#                                                                      #
########################################################################

#import from standard library
import sqlite3
import sys
from pathlib import Path

if Path('lora_chat.db').is_file():
    try:
        db = sqlite3.connect('lora_chat.db')
        db.execute('PRAGMA foreign_keys = ON')
        db.execute('DROP TABLE IF EXISTS sms')
        db.commit()
        db.execute('''
            CREATE TABLE IF NOT EXISTS sms (
                node_id                         INTEGER NOT NULL,
                message	                        TEXT NOT NULL,
                payload_raw                     TEXT NOT NULL,
                payload_hex                     TEXT NOT NULL,
                time_queued	                    INTEGER,
                time_sent	                    INTEGER,
                air_time	                    INTEGER,
                time_received	                INTEGER,
                rssi                            INTEGER,
                snr                             INTEGER,
                FOREIGN KEY (node_id) REFERENCES nodes (node_id));''')
        db.commit()
        db.close()
    except:
        print('FAIL!')
        sys.exit(1)
    else:
        print('PASS!')
        sys.exit(0)
else:
    print('ERROR: File not found - lora_chat.db')
    sys.exit(1)