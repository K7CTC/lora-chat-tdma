# LoRa Chat TDMA

LoRa Chat TDMA edition is an experimental SMS (Short Message Service) application that utilizes the LoRa RF modulation scheme to send and receive undirected plaintext messages of 50 characters or less.  The application is 100% scratch built in Python 3 and is cross-platform.  LoRa Chat has been tested on macOS Big Sur, Windows 10 as well as Raspberry Pi OS.  All modules have been tested with Python v3.7.3 and Python v3.9.  LoRa Chat is an extremely light weight console application with a simple and easy to understand user interface.

## Required Hardware

* [Ronoth LoStik](https://ronoth.com/products/lostik)

### Ronoth LoStik

The Ronoth LoStik is a LoRa/LoRaWAN transceiver capable of transmitting up to 70.8mW.  It features an SMA antenna port and a USB 2.0 host interface.  The LoStik presents itself to the host as a simple serial UART via an internal USB to serial (RS-232) bridge.  Communication with the LoStik is performed over a serial connection using simple ASCII commands.

Ronoth ships the LoStik with a 915MHz stubby antenna, the kind you expect to see with a device of this type.  The included antenna is more than adequate for testing aroung the house or even in the yard.  I have invested in and exerimented with two additional antenna types.  One is a simple PCB dipole antenna and the other is a commercial base station antenna.  As we know, the antenna is basically the "other half" of the transciever.  A proper antenna setup can have a dramatic impact on transmit and receive performance.

## Recommended Hardware

* [915MHz Dipole Antenna](https://lowpowerlab.com/shop/product/193)
* [915MHz Base Antenna](https://diamondantenna.net/bc920.html)

## Software Dependencies

* [Python 3](https://www.python.org/downloads/)
* [pySerial](https://pyserial.readthedocs.io/en/latest/pyserial.html#installation)

## Compatibility

LoRa Chat has been tested with Python v3.7.3 as well as Python v3.9.  At the time of this writing Python v3.9 is the current stable release and Python v3.7.3 is shipped with Raspberry Pi OS v2020-12-02.  The lostik-service module requires pySerial v3.5 (current version).  Previous versions of pySerial do not support macOS Big Sur.  A US variant (915MHz) Ronoth LoStik is also required and can be acquired directly from Ronoth or via Amazon for less than $50 each.  LoRa Chat has been tested with macOS Big Sur v11.0.1, Windows 10 20H2 and Raspberry Pi OS v2020-12-02.

## Concepts

### Node ID

The node identifier is an integer between 1 and 99 that serves as the primary form of identification for sent and received messages.  A more friendly node name is paired with the node identifier within the user interface.

### Ronoth LoStik "Plug-n-Play"

As we have learned, the LoStik is a "USB to Serial" device.  As such, the device is already plug-n-play with most modern operating systems.  However, the LoRa Chat application still needs to connect and communicate with the hardware device once attached to the host.  This means we must know the details of the serial (COM) port to which the LoStik is attached.

LoRa Chat accomplishes this by detecting the host operating system.  Then it enumerates the serial ports of the host system.  Next a query of the hardware identifier for connected devices is performed.  If a LoStik match is found, LoRa Chat will attempt a connection.  Once a connection is established, for additional guarantee, the firmware version of the LoStik is read and compared against a check.

This concept was likely the most difficult to implement and took four code iterations.  The benefit from all of this work is that the user need not concern themselves with which USB port the LoStik is attached to.  The user also does not need to manually specify a port identifier, baud rate, etc.  All of this happens transparently for the user.  It just works (or doesn't if the LoStik isn't attached).

### TDMA (Time Division Multiple Access)

For this project, I have developed a custom [TDMA](https://en.wikipedia.org/wiki/Time-division_multiple_access) algorythm taylored for use with LoRa.  My TDMA algorythm is based on the assumption of a LoRa Chat network consisting of 4 nodes.  LoRa Chat incorporates a concept I refer to as the "time scale".  The time scale determines the duration of the transmit window for each node 



### Ronoth LoStik Watchdog Timer Time-Out

One of the features of LoStik is referred to as the "Watchdog Timer Time-Out" (WDT).  When enabled, this prevents the device from getting stuck in a transmit or a receive state for longer than the duration specified.  In LoRa Chat, the default state of the LoStik is "idle", neither transmitting or receiving.  When the LoStik is placed in a transmit or receive state, the WDT kicks in.  When the allotted time is reached (in milliseconds) the device will drop back to an idle state while raising an error.

### TX/RX "Cycle"

LoRa Chat utilizes the aforementioned WDT as the timing mechanism for a TX/RX cycle or "loop".  The default WDT value for this project is 8 seconds but this can be configuraed for anywhere between 5 and 30 seconds.  The longest message transmit time is roughly 3.5 seconds so we are not concerned with the WDT on transmit, only on receive.  If a message is received or if the WDT is triggered, LoRa chat processes it accordingly then checks for outgoing messages.  Should an outgoing message exist, it is sent and the process repeats.

## Known Limitations

Since we rely on the WDT or received packets to control the timing of the TX/RX cycle it is possible that a "collision" can occur.  This can happen when multiple nodes transmit at the same time or if a node drops out of its receive state while a message is in the process of being transmitted by another node.  LoRa Chat is experimental and not indended for reliable message delivery.  In testing, a WDT value of eight seconds seemed to strike the right balance of reliability and speed.  Just know that even in ideal RF conditions, it is possible for a message to get clobbered.

## Project File Descriptions

### lcdb.py

This module contains functions for interacting with lora_chat.db, the database that stores all application data.  It is not intended for direct execution but rather import into other application modules.  The functions of lcdb.py provide the following utility to other modules in the application:

* Check to see if lora_chat.db exists and create a new lora_chat.db if it doesn't.
  * Upon database creation, the user is prompted to select a node identifier.
* Obtain the number of nodes recognized by te application.
* Obtain the node identifer of the current (your) node.
* Obtain the node name of the current (your) node.
* Store outbound messages.
* Clear the chat history.

### lostik-service.py

This module contains all of the logic for interfacing with the Ronoth LoStik.  The LoStik Service accepts three optional command line arguments; transmit power, coding rate and watchdog timer time-out.  For additional details on usage please execute with the --help argument.

#### Regarding Transmit Power

I have simplified the transmit power settings for the LoStik by only exposing three options; low, medium and high.  Under normal operation, the LoStik power setting is an integer between 2 and 20 (while omitting a few).  The settings translate to a minimum power of 3dBm (2mW) when set to "2" and a maximum power of 18.5dBm (70.8mW) when set to 20.  The transmit power, in milliwatts for low, medium and high are 5mW, 20mW and 70.8mW respectively.  As always, actual effective radiated power largely depends on your antenna and feedline configuration.

### nodes.csv

This comma separated values file contains a header row specifying the field names for the node table of the LoRa Chat database.  Remaining rows list the node identifier (integer between 1 and 99) along with the node name.  This file is read by the lcdb.py function when called and lora_chat.db is not found prompting the application to create a new database.  The contents of nodes.csv are populated into a database table named "nodes" for use elsewhere within the application.

This file is intended to be edited directly in any suitable plaintext editor.  The version provided by this project is simply a template.  Feel free to provide your own friendly node names.

### requirements.txt

This file is used by the pip package manager to install application dependencies.  Currently the only dependency is pySerial v3.5 or above.

### sms_clear.py

This module simply drops and recreates the sms table from lora_chat.db thus purging chat history.

### sms_new.py

This module validates a user provided message of up to 50 characters.  An SMS packet type identifier is appended and the resulting data is inserted into a new row within the sms table of lora_chat.db.  This module can be run interactively or non-interactively by passing the optional --msg command line argument.  If the message is passed via command line, the module will deposit the message into the database, report success/fail and exit.  If run interactively, the module will loop a prompt to provide an outgoing message.

### sms_view.py

This module reads the sms table from lora_chat.db and prints the output to the console.

### lostik.log

This file is created (and subsequently appended) by the lostik-service.py Python module.  As one would guess, it contains an event log for the service.

### lora_chat.db

This SQLite 3 database file is created automatically if not found during application execution and contains all application data.  The database contains two tables; nodes and sms.  The nodes table contains node_id (as the primary key) as well as node_name and my_node.  My_node serves to hold a boolean of true on one row to indicate your chosen node identifier.  The sms table contains; node_id (foreign key), message, payload_raw, payload_hex, time_queued, time_sent, air_time, time_received, rssi, snr.  These fields provide all that is needed to accurately record all incoming and outgoing messages.

## Quick Start

You will want to open three separate terminal windows.  Start by running sms_new.py which will trigger the creation of lora_chat.db.  On first launch, you will be prompted to select your node identififier from a list.  Please choose carefully as this setting is permanent.  If you choose incorrectly, you will need to delete lora_chat.db and start over.  In separate terminal windows, run sms_view.py and lostik-service.py.  It doesn't matter what order any of these three modules are executed as they operate asynchronously.

To send a message, simply type a message in SMS New.  Your message will be queued for transmission.  On the next transmit cycle of the LoStik, the LoStik Service checks for outgoing message(s) and transmits it.  Only one message is sent per transmit cycle using FIFO (first in, first out).  After an outgoing message has been transmitted, the database record is updated to reflect the time sent as well as the time spend "on air".  

SMS View checks for changes in the database once per second.  When an outgoing message had been sent or an incoming message has been received, it is formatted and displayed in a "chat" style interface with all pertinent details.

The LoStik Service runs in an infinite loop based on the hardware Watchdog Timer Time-Out on the LoStik or receipt of a message from another node.  The default is 8 seconds, meaning that if nothing is received within 8 seconds, the device drops out of its receive state and returns to idle.  The same is true for transmit.  A transmission longer than 8 seconds will cause the device to drop out of the transmit state and return to idle (with an error).  Upon successful message receipt the application will store the message in the database and check for the next outgoing message.  If a message is found it is sent.

## Normal Operation

Simply leave all three programs running in their terminal windows.  Newly received messages will automatically appear within SMS View.  Outgoing messages will not appear in SMS View until they are successfully transmitted.  The application runs in an infinite loop and is considered stable.  Data is saved to the database "on the fly" so even if execution is halted...  The chat history and selected station identifier remain.

To start over, simply delete the lora_chat.db file.  If you only want to clear the chat history, run sms_clear.py (preferably while sms_view.py is not running).

## Final Thoughts

I have successfully tested round trip message transmission over a signal path of 13.5mi with both nodes running at high power.  In the future, I plan additional tests to see if I can exceed a 16mi signal path.  LoRa is an incredible modulation scheme when you consider this is accomplished with less than 100mW.

## Developed By

* **Chris Clement (K7CTC)** - [https://qrz.com/db/K7CTC](https://qrz.com/db/K7CTC)
