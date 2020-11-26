########################################################################
#                                                                      #
#          NAME:  LoRa Chat - Database Functions                       #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v1.0                                                 #
#   DESCRIPTION:  This module contains database functions for LoRa     #
#                 Chat and is only intended for import into other      #
#                 project modules. Not to be executed directly!        #
#                                                                      #
########################################################################

#import from standard library
import csv
import os
import sqlite3
import time
from pathlib import Path

#this module is not intended for direct execution
if __name__ == '__main__':
    print('ERROR: lcdb.py is not intended for direct execution!')

#function: check for LoRa Chat database or create if it doesn't already exist
# returns: boolean
def exists():
    if Path('lora_chat.db').is_file():
        return True
    if Path('nodes.csv').is_file() == False:
        print('ERROR: File not found - nodes.csv')
        print('HELP: nodes.csv is required for database creation.')
        return False
    try:
        db = sqlite3.connect('lora_chat.db')
        db.execute('PRAGMA foreign_keys = ON')
        db.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id	                        INTEGER NOT NULL UNIQUE,
                node_name	                    TEXT NOT NULL,
                my_node                         TEXT UNIQUE,
                PRIMARY KEY(node_id));''')
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
        with open('nodes.csv') as csvfile:
            nodes = csv.DictReader(csvfile)
            to_db = [(i['node_id'],
                    i['node_name'])
                    for i in nodes]
        db.executemany('''
            INSERT INTO nodes (
                node_id,
                node_name)
            VALUES (?, ?);''', to_db)
        db.commit()
        db.close()
    except:
        if os.path.exists('lora_chat.db'):
            os.remove('lora_chat.db')
        print('ERROR: Unable to create lora_chat.db!')
        return False
    else:
        return True
    return False

#function: obtain number of rows in nodes table
# returns: row count as integer
def nodes_row_count():
    db = sqlite3.connect('lora_chat.db')
    db.execute('PRAGMA foreign_keys = ON')
    row_count = db.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
    db.close()
    return row_count    

#function: logic to obtain and set the my_node boolean value
# returns: my_node_id integer or None
def my_node_id():
    #grab the maximum node id integer value before continuing
    max_node_id = nodes_row_count()
    db = sqlite3.connect('lora_chat.db')
    c = db.cursor()
    c.execute('PRAGMA foreign_keys = ON')
    c.execute('SELECT node_id FROM nodes WHERE my_node = "True"')
    my_node_id = c.fetchone()
    if my_node_id:
        c.close()
        db.close()
        return my_node_id[0]
    os.system('cls' if os.name == 'nt' else 'clear')
    print('┌─┤LoRa Chat - Set My Node ID├─────────────────────────────────────┐')
    print('│ Please select node identifier from the following list:           │')
    c.execute('''
        SELECT
            node_id,
            node_name
        FROM
            nodes;''')
    for record in c.fetchall():
        node_id = record[0]
        node_name = record[1]
        left_margin = '│     '
        if len(str(node_id)) > 1:
            left_margin = '│    '
        right_margin = ' ' * (57 - len(node_name))
        right_margin = right_margin + '│'
        print(f'{left_margin}{node_id} - {node_name}{right_margin}')
    print('└──────────────────────────────────────────────────────────────────┘')
    print(f'Press CTRL+C to quit.')
    print()
    my_node_id = input('My Node ID (1-' + str(max_node_id) + '): ')
    try:
        my_node_id = int(my_node_id)
    except:
        print(f'HELP: Node identifier must be an integer between 1 and {str(max_node_id)}!')
        c.close()
        db.close()
        return None
    if my_node_id < 1 or my_node_id > max_node_id:
        print(f'HELP: Node identifier must be an integer between 1 and {str(max_node_id)}!')
        c.close()
        db.close()
        return None
    try:    
        c.execute('''
            UPDATE
                nodes
            SET
                my_node=?
            WHERE
                node_id=?;''',
            ("True", my_node_id))
    except:
        c.close()
        db.close()
        print('ERROR: Unable to update my_node value in lora_chat.db!')
        return None
    else:
        db.commit()
    c.execute('SELECT node_id FROM nodes WHERE my_node = "True"')
    my_node_id = c.fetchone()
    c.close()
    db.close()
    if my_node_id:
        return my_node_id[0]
    return None      

#function: obtain node name based on corresponding node identifier
# accepts: my_node_id as integer
# returns: node_name
def my_node_name(my_node_id):
    db = sqlite3.connect('lora_chat.db')
    c = db.cursor()
    c.execute('PRAGMA foreign_keys = ON')
    c.execute('SELECT node_name FROM nodes WHERE node_id=?',(my_node_id,))
    my_node_name = c.fetchone()
    c.close()
    db.close()
    return my_node_name[0]

#function: insert outgoing message record into database
# accepts: my_node_id and validated message
# returns: boolean  
def outbound_message(my_node_id,message):
    #compose raw packet to be sent over the air
    payload_raw = str(1) + ',' + str(my_node_id) + ',' + message
    #compose hex encoded version of raw packet to be sent over the air
    payload_hex = payload_raw.encode('UTF-8').hex()
    try:
        db = sqlite3.connect('lora_chat.db')
        c = db.cursor()
        c.execute('PRAGMA foreign_keys = ON')
        time_queued = int(round(time.time()*1000))
        c.execute('''
            INSERT INTO sms (
                node_id,
                message,
                payload_raw,
                payload_hex,
                time_queued)
            VALUES (?, ?, ?, ?, ?);''',
            (my_node_id, message, payload_raw, payload_hex, time_queued))
    except:
        c.close()
        db.close()
        return False
    else:
        db.commit()
        c.close()
        db.close()
        return True
    return False

#function: clear sms table
# returns: boolean
def clear_sms():
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
        db.close()
        return False
    else:
        return True