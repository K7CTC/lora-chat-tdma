########################################################################
#                                                                      #
#          NAME:  LoRa Chat - LoStik Service                           #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v1.0                                                 #
#                                                                      #
########################################################################

#import from required 3rd party libraries
import serial
import serial.tools.list_ports

#import from project library
import lcdb

#import from standard library
import argparse
import atexit
import datetime
import logging
import os
import sqlite3
import sys
import time

#establish logging
logging.basicConfig(filename='lostik.log',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p',
                    level=logging.INFO)

#establish command line arguments
parser = argparse.ArgumentParser(description='LoRa Chat - LoStik Service',
                                 epilog='Created by K7CTC.')
parser.add_argument('--pwr',
                    choices=['low','medium','high'],
                    help='LoStik transmit power - default: low',
                    default='low')
parser.add_argument('--cr',
                    type=int,
                    choices=range(5, 9),
                    help='LoStik coding rate - default: 8',
                    default='8')
parser.add_argument('--wdt',
                    type=int,
                    choices=range(5,31),
                    help='LoStik watchdog timer time-out in seconds - default: 8',
                    default='8')

#parse command line arguments
args = parser.parse_args()

#convert pwr to actual power setting expected by LoStik before proceeding
if args.pwr == 'low':
    args.pwr = 6
elif args.pwr =='medium':
    args.pwr = 12
elif args.pwr == 'high':
    args.pwr = 20

#convert wdt from seconds to milliseconds before proceeding
args.wdt = args.wdt * 1000

#global variables
version = 'v1.0'

#start logger
logging.info('----------------------------------------------------------------------')
logging.info('lostik.py %s started', version)

#verify existence of lora_chat.db before proceeding
if lcdb.exists() == False:
    print('ERROR: File not found - lora_chat.db')
    logging.error('File not found - lora_chat.db')
    sys.exit(1)
else:
    logging.info('File found - lora_chat.db') 
    
#establish database connection
db = None
c = None
try:     
    db = sqlite3.connect('lora_chat.db')
    c = db.cursor()
    c.execute('PRAGMA foreign_keys = ON')
except:
    print('ERROR: Unable to connect to lora_chat.db!')
    logging.error('Unable to connect to lora_chat.db!')
    sys.exit(1)
else:
    logging.info('Connected to lora_chat.db')

#lostik PiERS network variables (all nodes must share the same settings)
#Frequency (hardware default=923300000)
#value range: 902000000 to 928000000
set_freq = b'923300000'
#Modulation Mode (hardware default=lora)
#this exists just in case the radio was somehow mistakenly set to FSK
set_mod = b'lora'
#CRC Header (hardware default=on)
#values: on, off (not sure what this does, best to use default value)
set_crc = b'on'
#IQ Inversion (hardware default=off)
#values: on, off (not sure what this does, best to use default value)
set_iqi = b'off'
#Sync Word (hardware default=34)
#value: one hexadecimal byte
set_sync = b'34'
#Spreading Factor (hardware default=sf12)
#values: sf7, sf8, sf9, sf10, sf11, sf12
set_sf = b'sf12'
#Radio Bandwidth (hardware default=125)
#values: 125, 250, 500
set_bw = b'125'

#lostik PiERS node variables (can vary from one node to the next based on operating conditions)
#Transmit Power (hardware default=2)
#value range: 2 to 20
set_pwr = bytes(str(args.pwr), 'ASCII')
#Coding Rate (hardware default=4/5, script default=4/8)
#values: 4/5, 4/6, 4/7, 4/8
set_cr = b''.join([b'4/', bytes(str(args.cr), 'ASCII')])
#Watchdog Timer Time-Out (hardware default=15000, script default=8000)
#value range: 0 to 4294967295 (0 disables wdt functionality)
set_wdt = bytes(str(args.wdt), 'ASCII')

########################################################################
# LoStik Notes:  The Ronoth LoStik USB to serial device has a VID:PID  #
#                equal to 1A86:7523. Using pySerial we are able to     #
#                query the system (Windows/Linux/macOS) to see if a    #
#                device matching this VID:PID is attached via USB. If  #
#                a LoStik is detected, we can then assign its port     #
#                programmatically.  This eliminates the need to guess  #
#                the port or obtain it as a command line argument.     #
#                This only took several months to figure out.          #
########################################################################

#attempt LoStik detection, port assignment and connection.  exit on error
lostik = None
lostik_port = None
ports = serial.tools.list_ports.grep('1A86:7523')
for port in ports:
    lostik_port = port.device
    logging.info('LoStik detected on port: ' + lostik_port)
del(ports)
if lostik_port == None:
    print('ERROR: LoStik not detected!')
    logging.error('LoStik not detected!')
    print('HELP: Check serial port descriptor and/or device connection.')
    logging.info('Check serial port descriptor and/or device connection.')
    sys.exit(1)
try:
    lostik = serial.Serial(lostik_port, baudrate=57600, timeout=1)
except:
    print('ERROR: Unable to connect to LoStik!')
    logging.error('Unable to connect to LoStik!')
    print('HELP: Check port permissions. Current user must be member of "dialout" group.')
    logging.info('Check port permissions. Current user must be member of "dialout" group.')
    sys.exit(1)
else:
    logging.info('LoStik port opened, device is connected.')    
del(lostik_port)

#check LoStik firmware version
lostik.write(b'sys get ver\r\n')
lostik_version = lostik.readline().decode('ASCII').rstrip()
if lostik_version == 'RN2903 1.0.5 Nov 06 2018 10:45:27':
    logging.info('LoStik firmware version: ' + lostik_version)
else:
    print('ERROR: LoStik failed to return expected firmware version!')
    logging.error('LoStik failed to return expected firmware version!')
    sys.exit(1)

#attempt to pause mac (LoRaWAN) as required to issue commands directly to the radio
lostik.write(b'mac pause\r\n')
if lostik.readline().decode('ASCII').rstrip() == '4294967245':
    logging.info('LoStik LoRaWAN successfully paused.')
else:
    print('ERROR: Unable to pause LoRaWAN!')
    logging.error('Unable to pause LoRaWAN!')
    sys.exit(1)

#function: control lostik LEDs
# accepts: led and state with values of 'rx' or 'tx' and 'on' or 'off' respectively
# returns: boolean
def lostik_led_control(led, state): #values are rx/tx and on/off
    if led == 'rx':
        if state == 'off':
            lostik.write(b'sys set pindig GPIO10 0\r\n') #GPIO10 = blue rx led
            if lostik.readline().decode('ASCII').rstrip() == 'ok':
                return True
            else:
                return False
        elif state == 'on':
            lostik.write(b'sys set pindig GPIO10 1\r\n') #GPIO10 = blue rx led
            if lostik.readline().decode('ASCII').rstrip() == 'ok':
                return True
            else:
                return False
    elif led == 'tx':
        if state == 'off':
            lostik.write(b'sys set pindig GPIO11 0\r\n') #GPIO11 = red tx led
            if lostik.readline().decode('ASCII').rstrip() == 'ok':
                return True
            else:
                return False
        elif state == 'on':
            lostik.write(b'sys set pindig GPIO11 1\r\n') #GPIO11 = red tx led
            if lostik.readline().decode('ASCII').rstrip() == 'ok':
                return True
            else:
                return False
    else:
        return False

#initialize lostik for PiERS operation
#turn on both LEDs to indicate we are entering "initialization" mode
lostik_led_control('rx', 'on')
lostik_led_control('tx', 'on')

logging.info('Begin LoStik initialization.')

#write "network" settings to LoStik
#set frequency
lostik.write(b''.join([b'radio set freq ', set_freq, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik frequency set to ' + set_freq.decode('UTF-8') + '.')
else:
    print('ERROR: Failed to set LoStik frequency to ' + set_freq.decode('UTF-8') + '!')
    logging.error('Failed to set LoStik frequency to ' + set_freq.decode('UTF-8') + '!')
    sys.exit(1)
#set mode
lostik.write(b''.join([b'radio set mod ', set_mod, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik modulation mode set to LoRa.')
else:
    print('ERROR: Failed to set LoStik modulation mode to LoRa!')
    logging.error('Failed to set LoStik modulation mode to LoRa!')
    sys.exit(1)
#set CRC header usage
lostik.write(b''.join([b'radio set crc ', set_crc, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik CRC header enabled.')
else:
    print('ERROR: Failed to enable LoStik CRC header setting!')
    logging.error('Failed to enable LoStik CRC header setting!')
    sys.exit(1)
#set IQ inversion
lostik.write(b''.join([b'radio set iqi ', set_iqi, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik IQ inversion disabled.')
else:
    print('ERROR: Failed to disable LoStik IQ inversion setting!')
    logging.error('Failed to disable LoStik IQ inversion setting!')
    sys.exit(1)
#set sync word
lostik.write(b''.join([b'radio set sync ', set_sync, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik sync word set to ' + set_sync.decode('UTF-8') + '.')
else:
    print('ERROR: Failed to set LoStik sync word to ' + set_sync.decode('UTF-8') + '!')
    logging.error('Failed to set LoStik sync word to ' + set_sync.decode('UTF-8') + '!')
    sys.exit(1)
#set spreading factor
lostik.write(b''.join([b'radio set sf ', set_sf, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik spreading factor set to ' + set_sf.decode('UTF-8') + '.')
else:
    print('ERROR: Failed to set LoStik spreading factor to ' + set_sf.decode('UTF-8') + '!')
    logging.error('Failed to set LoStik spreading factor to ' + set_sf.decode('UTF-8') + '!')
    sys.exit(1)
#set radio bandwidth
lostik.write(b''.join([b'radio set bw ', set_bw, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik radio bandwidth set to ' + set_bw.decode('UTF-8') + '.')
else:
    print('ERROR: Failed to set LoStik radio bandwidth to ' + set_bw.decode('UTF-8') + '!')
    logging.error('Failed to set LoStik radio bandwidth to ' + set_bw.decode('UTF-8') + '!')
    sys.exit(1)
    
#write "node" settings to LoStik
#set power
lostik.write(b''.join([b'radio set pwr ', set_pwr, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik transmit power set to ' + set_pwr.decode('UTF-8') + '.')
else:
    print('ERROR: Failed to set LoStik transmit power to ' + set_pwr.decode('UTF-8') + '!')
    logging.error('Failed to set LoStik transmit power to ' + set_pwr.decode('UTF-8') + '!')
    sys.exit(1)
#set coding rate
lostik.write(b''.join([b'radio set cr ', set_cr, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik coding rate set to ' + set_cr.decode('UTF-8') + '.')
else:
    print('ERROR: Failed to set LoStik coding rate to ' + set_cr.decode('UTF-8') + '!')
    logging.error('Failed to set LoStik coding rate to ' + set_cr.decode('UTF-8') + '!')
    sys.exit(1)
#set watchdog timer time-out
lostik.write(b''.join([b'radio set wdt ', set_wdt, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() == 'ok':
    logging.info('LoStik watchdog time time-out ' + set_wdt.decode('UTF-8') + '.')
else:
    print('ERROR: Failed to set LoStik watchdog timer time-out to ' + set_wdt.decode('UTF-8') + '!')
    logging.error('Failed to set LoStik watchdog timer time-out to ' + set_wdt.decode('UTF-8') + '!')
    sys.exit(1)

#pause three quarters of a second for effect
time.sleep(.75)

#turn off both LEDs to indicate we have exited "initialization" mode
lostik_led_control('rx', 'off')
lostik_led_control('tx', 'off')

logging.info('LoStik initialization complete.')

#function: control lostik receive state
# accepts: state with values of 'on' or 'off'
# retruns: boolean
def lostik_rx_control(state): #state values are 'on' or 'off'
    if state == 'on':
        #place LoStik in continuous receive mode
        lostik.write(b'radio rx 0\r\n')
        if lostik.readline().decode('ASCII').rstrip() == 'ok':
            return True
            # if lostik_led_control('rx', 'on'):
            #     return True
            # else:
            #     return False
        else:
            return False
    elif state == 'off':
        #halt LoStik continuous receive mode
        lostik.write(b'radio rxstop\r\n')
        if lostik.readline().decode('ASCII').rstrip() == 'ok':
            return True
            # if lostik_led_control('rx', 'off'):
            #     return True
            # else:
            #     return False
        else:
            return False

#function: obtain rssi of last received packet
# returns: rssi
def lostik_get_rssi():
    lostik.write(b'radio get rssi\r\n')
    rssi = lostik.readline().decode('ASCII').rstrip()
    return rssi

#function: obtain snr of last received packet
# returns: snr
def lostik_get_snr():
    lostik.write(b'radio get snr\r\n')
    snr = lostik.readline().decode('ASCII').rstrip()
    return snr

#function: force receive state and attempt to transmit hex payload
# accepts: payload_hex (value to be transmitted)
# retruns: boolean
#    note: terminates script on error
def lostik_tx_cycle(payload_hex):
    if lostik_rx_control('off'):
        tx_command_elements = 'radio tx ' + payload_hex + '\r\n'
        tx_command = tx_command_elements.encode('ASCII')
        lostik.write(tx_command)
        if lostik.readline().decode('ASCII').rstrip() == 'ok':
            lostik_led_control('tx', 'on')
        else:
            print('ERROR: Transmit failure!')
            logging.error('Transmit failure!')
            sys.exit(1)
        response = ''
        while response == '':
            response = lostik.readline().decode('ASCII').rstrip()
        else:
            if response == 'radio_tx_ok':
                lostik_led_control('tx', 'off')
                return True
            elif response == 'radio_err':
                lostik_led_control('tx', 'off')
                print('WARNING: Transmit failure! Radio error!')
                logging.warning('Transmit failure! Radio error!')
                return False
    else:
        print('WARNING: Transmit failure! Unable to halt LoStik continuous receive mode.')
        logging.warning('Transmit failure! Unable to halt LoStik continuous receive mode.')
        return False

#function: get next tx payload from lora_chat.db 
# returns: rowid and payload_hex
#    note: terminates script on error
def get_next_tx_payload():
    try:    
        c.execute('''
            SELECT
                rowid,
                payload_hex,
                time_queued,
                time_sent
            FROM
                sms
            WHERE
                time_queued IS NOT NULL AND time_sent IS NULL;''')
        record = c.fetchone()
        if record:
            return record[0], record[1]
        else:
            return None, None
    except:
        print('ERROR: Unable to get next TX payload from database!')
        logging.error('Unable to get next TX payload!')
        sys.exit(1)

#function: drop received payload into database, returns boolean
# accepts: payload_hex, rssi and snr
#    note: terminates script on error
def insert_rx_record(payload_hex,rssi,snr):
    payload_raw = bytes.fromhex(payload_hex).decode('ASCII')
    payload_list = payload_raw.split(',')
    node_id = payload_list[1]
    message = payload_list[2]
    time_received = int(round(time.time()*1000))
    try:
        c.execute('''
            INSERT INTO sms (
                node_id,
                message,
                payload_raw,
                payload_hex,
                time_received,
                rssi,
                snr)
            VALUES (?, ?, ?, ?, ?, ?, ?);''',
            (node_id, message, payload_raw, payload_hex, time_received, rssi, snr))
        db.commit()
    except:
        print('ERROR: Unable to insert RX record into database!')
        logging.error('Unable to insert RX record into database!')
        sys.exit(1)

#function: update database after successful transmit
# accepts: rowid, time_sent and air_time
#    note: terminates script on error
def update_db_record(rowid,time_sent,air_time):
    try:
        c.execute('''
            UPDATE
                sms
            SET
                time_sent=?,
                air_time=?
            WHERE
                rowid=?;''',
            (time_sent,air_time,rowid))
        db.commit()
    except:
        print('ERROR: Unable to update database record of transmitted message!')
        logging.error('Unable to update database record of transmitted message!')
        sys.exit(1)

#function: bypass the print() buffer so we can write to the console direct
# accepts: text (to be written to the console)
def incremental_print(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()

########################################################################
# LoStik Notes:  The Ronoth LoStik rx/tx state is manually controlled  #
#                which means that we must juggle inbound and outbound  #
#                packets while juggling the state of the LoStik radio  #
#                at the same time.  To complicate things further, this #
#                must also work reliably as a loop.  I will try to     #
#                distill this into a simple flow but it still likely   #
#                to be a kludge.                                       #
########################################################################

#function: converts LoStik TX power setting to TX output in mW
# accepts: LoStik TX power setting
# returns: LoStik TX power in mw
def pwr_to_mw(pwr):
    pwr_lookup_dict = {
        '6':'5.0',
        '12':'20.0',
        '20':'70.8'
    }
    return pwr_lookup_dict[pwr]

#create "friendly" string versions for all settings that were written to LoStik
freq = set_freq.decode('ASCII')
freq = freq[0:3] + '.' + freq[3:6] + ' MHz'
mod = 'LoRa'
crc = set_crc.decode('ASCII')
if len(crc) == 2:
    crc = crc + ' '
iqi = set_iqi.decode('ASCII')
if len(iqi) == 2:
    iqi = iqi + ' '
sync = set_sync.decode('ASCII')
sf = set_sf.decode('ASCII')
sf = sf[2:]
if len(sf) == 1:
    sf = sf + ' '
bw = set_bw.decode('ASCII') + ' KHz'
pwr = pwr_to_mw(set_pwr.decode('ASCII')) + ' mW'
if len(pwr) == 6:
    pwr = pwr + ' '
cr = set_cr.decode('ASCII')

wdt = args.wdt / 1000
wdt = int(wdt)
wdt = str(wdt) + ' seconds'
if len(wdt) == 9:
    wdt = wdt + ' '

#function: compose LoStik status interface
def lostik_static_ui(status):      
    now = datetime.datetime.now()
    time = now.strftime('%I:%M:%S %p')
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'╔══════════════════╡LoRa Chat LoStik Service {version}╞═════════════════╗')
    print(f'║ Frequency: {freq} │ Bandwidth: {bw} │ TX Power: {pwr}  ║')
    print(f'╟────────────────────────┴────────────────────┴────────────────────╢')
    print(f'║ Spreading Factor: {sf}   │ Coding Rate: {cr}   │ Sync Word: {sync}      ║')
    print(f'╟────────────────────────┴────────────────────┴────────────────────╢')
    print(f'║ Modulation Mode: {mod}  │ Watchdog Timer Time-Out: {wdt}     ║')
    print(f'╟────────────────────────┴─────────────────────────────────────────╢')
    print(f'║ CRC Header: {crc} │ IQ Inversion: {iqi} │ Last Activity: {time} ║')
    print(f'╟─────────────────┴───────────────────┴────────────────────────────╢')
    print(f'║ Last LoStik Status: {status}                                 ║')                    
    print(f'╚══════════════════════════════════════════════════════════════════╝')
    print(f'Press CTRL+C to quit.')

#the loop
while True:
    if lostik_rx_control('on'):
        lostik_static_ui('Listening   ')
        rx_payload = ''
        while rx_payload == '':
            rx_payload = lostik.readline().decode('ASCII').rstrip()
        else:
            if rx_payload == 'radio_err':
                #watchdog timer time-out
                rowid, payload_hex = get_next_tx_payload()
                if rowid != None and payload_hex != None:
                    if lostik_rx_control('off'):
                        lostik_static_ui('Transmitting')
                        tx_start_time = int(round(time.time()*1000))
                        if lostik_tx_cycle(payload_hex):
                            tx_end_time = int(round(time.time()*1000))
                            time_sent = int(round(time.time()*1000))
                            air_time = tx_end_time - tx_start_time
                            update_db_record(rowid,time_sent,air_time)
            else:
                rx_payload_list = rx_payload.split()
                payload_hex = rx_payload_list[1]
                rssi = lostik_get_rssi()
                snr = lostik_get_snr()
                insert_rx_record(payload_hex,rssi,snr)