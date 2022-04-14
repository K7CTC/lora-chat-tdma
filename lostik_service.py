########################################################################
#                                                                      #
#          NAME:  PiERS Chat - TDMA LoStik Service                     #
#  DEVELOPED BY:  Chris Clement (K7CTC)                                #
#       VERSION:  v2.0 (beta)                                          #
#                                                                      #
########################################################################

#import from required 3rd party libraries
import serial
import serial.tools.list_ports

#import from project library
from console import console
import lostik_settings
import db
import ui

#import from standard library
import argparse
import datetime
import sys
import time

console.clear()

#establish and parse command line arguments
parser = argparse.ArgumentParser(description='PiERS Chat - TDMA LoStik Service',
                                 epilog='Created by K7CTC.')
parser.add_argument('-p', '--power',
                    choices=['low','medium','high'],
                    help='LoStik transmit power - default: low',
                    default='low')
args = parser.parse_args()
if args.power == 'low':
    SET_PWR = b'6'
    PWR_LABEL = 'LOW'
    PWR_LABEL_DBM = '7.0 dBm'
    PWR_LABEL_MW = '5.0 mW'
elif args.power =='medium':
    SET_PWR = b'12'
    PWR_LABEL = 'MEDIUM'
    PWR_LABEL_DBM = '13.0 dBm'
    PWR_LABEL_MW = '20.0 mW'
elif args.power == 'high':
    SET_PWR = b'20'
    pwr_label = 'HIGH'
    PWR_LABEL_DBM = '18.5 dBm'
    PWR_LABEL_MW = '70.8 mW'

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

#attempt LoStik detection, port assignment and connection.
lostik = None
lostik_port = None
ports = serial.tools.list_ports.grep('1A86:7523')
for port in ports:
    lostik_port = port.device
del(ports)
if lostik_port == None:
    console.print('[bright_red][ERROR][/] LoStik not detected!')
    console.print('HELP: Check serial port descriptor and/or device connection.')
    sys.exit(1)
try:
    lostik = serial.Serial(lostik_port, baudrate=57600, timeout=1)
except:
    console.print('[bright_red][ERROR][/] Unable to connect to LoStik!')
    console.print('HELP: Check port permissions. User must be member of "dialout" group on Linux.')
    sys.exit(1)
del(lostik_port)

#check LoStik firmware version before proceeding
lostik.write(b'sys get ver\r\n')
if lostik.readline().decode('ASCII').rstrip() != lostik_settings.FIRMWARE_VERSION:
    console.print('[bright_red][ERROR][/] LoStik failed to return expected firmware version!')
    sys.exit(1)

# #check LoStik firmware version before proceeding
# lostik.write(b'sys get ver\r\n')
# FIRMWARE_VERSION = lostik.readline().decode('ASCII').rstrip()
# if FIRMWARE_VERSION != 'RN2903 1.0.5 Nov 06 2018 10:45:27':
#     console.print('[bright_red][ERROR][/] LoStik failed to return expected firmware version!')
#     sys.exit(1)

#attempt to pause mac (LoRaWAN) as required to issue commands directly to the radio
lostik.write(b'mac pause\r\n')
if lostik.readline().decode('ASCII').rstrip() != '4294967245':
    console.print('[bright_red][ERROR][/] Failed to disable LoRaWAN!')
    sys.exit(1)

#initialize lostik for PiERS operation   
lostik.write(b''.join([b'radio set pwr ', SET_PWR, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() != 'ok':
    console.print('[bright_red][ERROR][/] Failed to set LoStik transmit power!')
    sys.exit(1)
lostik.write(b''.join([b'radio set freq ', lostik_settings.SET_FREQ, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() != 'ok':
    console.print('[bright_red][ERROR][/] Failed to set LoStik frequency!')
    sys.exit(1)
lostik.write(b''.join([b'radio set sf ', lostik_settings.SET_SF, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() != 'ok':
    console.print('[bright_red][ERROR][/] Failed to set LoStik spreading factor!')
    sys.exit(1)
lostik.write(b''.join([b'radio set bw ', lostik_settings.SET_BW, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() != 'ok':
    console.print('[bright_red][ERROR][/] Failed to set LoStik radio bandwidth!')
    sys.exit(1)
lostik.write(b''.join([b'radio set cr ', lostik_settings.SET_CR, b'\r\n']))
if lostik.readline().decode('ASCII').rstrip() != 'ok':
    console.print('[bright_red][ERROR][/] Failed to set LoStik coding rate!')
    sys.exit(1)

#function: obtain rssi of last received packet
# returns: rssi
def get_rssi():
    lostik.write(b'radio get rssi\r\n')
    rssi = lostik.readline().decode('ASCII').rstrip()
    return rssi

#function: obtain snr of last received packet
# returns: snr
def get_snr():
    lostik.write(b'radio get snr\r\n')
    snr = lostik.readline().decode('ASCII').rstrip()
    return snr

#function: control blue led
# accepts: boolean
def blue_led(state):
    if state == True:
        lostik.write(b'sys set pindig GPIO10 1\r\n') #GPIO10 1 = blue tx led on
    else:
        lostik.write(b'sys set pindig GPIO10 0\r\n') #GPIO10 0 = blue tx led off
    response = lostik.readline()

#function: control red led
# accepts: boolean
def red_led(state):
    if state == True:
        lostik.write(b'sys set pindig GPIO11 1\r\n') #GPIO11 1 = red tx led on
    else:
        lostik.write(b'sys set pindig GPIO11 0\r\n') #GPIO11 0 = red tx led off
    response = lostik.readline()



#NEEDS WORK
#function: render UI
def refresh_ui(lostik_state):
    console.clear()
    console.print(f'╔═╡ LoRa Chat TDMA LoStik Service ╞════════╤════════════════════╗')
    console.print(f'║ Frequency: {lostik_settings.FREQ_LABEL} │ Bandwidth: {lostik_settings.BW_LABEL} │ TX Power: {PWR_LABEL}  ║')
    console.print(f'╟────────────────────────┼────────────────────┼────────────────────╢')
    console.print(f'║ Spreading Factor: {lostik_settings.SF_LABEL}   │ Coding Rate: {lostik_settings.CR_LABEL}         ║')
    console.print(f'╟────────────────────────┼────────────────────┴────────────────────╢')
    console.print(f'╟────────────────────────┼─────────────────────────────────────────╢')
    if lostik_state == 'idle':
        console.print(f'╚════════════════════════╧════════════════════════════════TX═══RX══╝')
    if lostik_state == 'tx':
        console.print(f'╚════════════════════════╧═══════════════════════════════▌TX▐══RX══╝')
    if lostik_state == 'rx':
        console.print(f'╚════════════════════════╧════════════════════════════════TX══▌RX▐═╝')
    console.print(f'Press CTRL+C to quit.')
    console.print()

#function: control lostik receive state
# accepts: boolean
#    note: exit on error
def rx(state):
    if state == True:
        #place LoStik in continuous receive mode
        lostik.write(b'radio rx 0\r\n')
        if lostik.readline().decode('ASCII').rstrip() == 'ok':
            refresh_ui('rx')
        else:
            console.print('[bright_red][ERROR][/] Serial interface is busy, unable to communicate with LoStik!')
            console.print('HELP: Disconnect and reconnect LoStik device, then try again.')
            sys.exit(1)
    else:
        #halt LoStik continuous receive mode
        lostik.write(b'radio rxstop\r\n')
        if lostik.readline().decode('ASCII').rstrip() == 'ok':
            refresh_ui('idle')
        else:
            console.print('[bright_red][ERROR][/] Serial interface is busy, unable to communicate with LoStik!')
            console.print('HELP: Disconnect and reconnect LoStik device, then try again.')
            sys.exit(1)

#function: attempt to transmit hex payload
# accepts: message
# retruns: time_sent and air_time
#    note: terminates script on error
def tx(message):
    tx_start_time = 0
    tx_end_time = 0
    time_sent = 0
    air_time = 0
    message_hex = message.encode('UTF-8').hex()
    tx_command_elements = 'radio tx ' + message_hex + '\r\n'
    tx_command = tx_command_elements.encode('ASCII')
    lostik.write(tx_command)
    if lostik.readline().decode('ASCII').rstrip() == 'ok':
        tx_start_time = int(round(time.time()*1000))
        refresh_ui('tx')
        red_led(True)
    else:
        console.print('[bright_red][ERROR][/] Transmit failure!')
        console.show_cursor(True)
        sys.exit(1)
    response = ''
    while response == '':
        response = lostik.readline().decode('ASCII').rstrip()
    else:
        if response == 'radio_tx_ok':
            tx_end_time = int(round(time.time()*1000))
            refresh_ui('idle')
            red_led(False)
            time_sent = tx_end_time
            air_time = tx_end_time - tx_start_time
            return time_sent, air_time
        elif response == 'radio_err':
            refresh_ui('idle')
            red_led(False)
            console.print('WARNING: Transmit failure! Radio error!')
            return time_sent, air_time


my_time_slot = None

#time slots are 5 seconds in duration...  however the tx window is only the first second
TS1_LIST = [0,1,2,3,4,10,11,12,13,14,20,21,22,23,24,30,31,32,33,34,40,41,42,43,44,50,51,52,53,54]
TS2_LIST = [5,6,7,8,9,15,16,17,18,19,25,26,27,28,29,35,36,37,38,39,45,46,47,48,49,55,56,57,58,59]
TS1_TX_LIST = [0,10,20,30,40,50]
TS2_TX_LIST = [5,15,25,35,45,55]

current_time_slot = None
current_time_slot_tx_window_open = False

#function: refresh current time slot values
# accepts: current second
def refresh_time_slot(current_second):
    global current_time_slot, current_time_slot_tx_window_open
    if current_second in TS1_LIST:
        current_time_slot = 1
        if current_second in TS1_TX_LIST:
            current_time_slot_tx_window_open = True
        else:
            current_time_slot_tx_window_open = False
    if current_second in TS2_LIST:
        current_time_slot = 2
        if current_second in TS2_TX_LIST:
            current_time_slot_tx_window_open = True
        else:
            current_time_slot_tx_window_open = False
         




console.show_cursor(False)

ui.lostik_service_static_content()
ui.lostik_service_insert_firmware_version()

#the loop!!!
while True:
    try:
        current_second = datetime.datetime.now().second
        refresh_time_slot(current_second)
        if my_time_slot == None or my_time_slot == current_time_slot:
            if current_time_slot_tx_window_open:
                rowid, message = db.get_next_outbound_message()
                if rowid != None and message != None:
                    rx(False)
                    time_sent, air_time = tx(message)
                    if time_sent != 0 and air_time != 0:
                        db.update_outbound_message(rowid,time_sent,air_time)
                        if my_time_slot == None:
                            my_time_slot = current_time_slot
                else:
                    #sleep to prevent unnecessary database access within the loop
                    time.sleep(2)
        else:
            rx(True)
            rx_payload = ''
            while rx_payload == '':
                current_second = datetime.datetime.now().second
                if my_time_slot == current_time_slot:
                    rx(False)
                    rx_payload = 'tx_window' #fake payload to break from the loop
                else:
                    rx_payload = lostik.readline().decode('ASCII').rstrip()
            else:
                if rx_payload == 'busy':
                    console.print('[bright_red][ERROR][/] LoStik busy!')
                    sys.exit(1)
                elif rx_payload != 'radio_err' and rx_payload != 'tx_window':
                    rx_payload_list = rx_payload.split()
                    payload_hex = rx_payload_list[1]
                    message = bytes.fromhex(payload_hex).decode('ASCII')
                    rssi = get_rssi()
                    snr = get_snr()
                    db.insert_inbound_message(message,rssi,snr)
    except KeyboardInterrupt:
        console.print()
        break

lostik.close()
console.clear()
console.show_cursor(True)
sys.exit(0)
