# LoRa Chat TDMA

LoRa Chat TDMA edition is an experimental SMS (Short Message Service) application that utilizes the LoRa RF modulation scheme to send and receive undirected plaintext messages of up to 30 or 50 characters.  The TDMA edition features a Time Division Multiple Access algorithm with the intent to eliminate the probability of packet collisions.  The application is 100% scratch built in Python 3 and is cross-platform.  LoRa Chat has been tested on macOS Big Sur, Windows 10 as well as Raspberry Pi OS.  All modules have been tested with Python v3.7.3 and Python v3.9.  LoRa Chat is an extremely light weight console application with a simple and easy to understand user interface.

## Required Hardware

* [Ronoth LoStik](https://ronoth.com/products/lostik)

### Ronoth LoStik

The Ronoth LoStik is a LoRa/LoRaWAN transceiver capable of transmitting up to 70.8mW.  It features an SMA antenna port and a USB 2.0 host interface.  The LoStik presents itself to the host as a simple serial UART via an internal USB to serial (RS-232) bridge.  Communication with the LoStik is performed over a serial connection using simple ASCII commands.

Ronoth ships the LoStik with a 915MHz stubby antenna, the kind you expect to see with a device of this type.  The included antenna is more than adequate for testing aroung the house or even in the yard.  I have invested in and exerimented with two additional antenna types.  One is a simple PCB dipole antenna and the other is a commercial base station antenna.  As we know, the antenna is basically the "other half" of the transciever.  A proper antenna setup can have a dramatic impact on transmit and receive performance.

## Recommended Hardware

* [915MHz Dipole Antenna](https://lowpowerlab.com/shop/product/193)
* [915MHz Base Antenna](https://diamondantenna.net/bc920.html)

## Other Compatible Hardware

* [915MHz Yagi Antenna](https://www.m2inc.com/FG915XBISP)

If I decide to invest more into this project, the high performance M2 yagi antenna is top of list.

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

For this project, I have developed a [TDMA](https://en.wikipedia.org/wiki/Time-division_multiple_access) algorithm taylored for use with LoRa.  My TDMA algorithm is based on the assumption of a LoRa Chat network consisting of 4 nodes.  LoRa Chat incorporates a concept I refer to as the "time scale".  The time scale determines the duration of the transmit window for each node.  Modifying the time scale impacts the packet density/throughput of the "network" over time.  LoRa Chat offers two time scale options, 1 and 2.

The time scale is specified by the -t or --timescale command line argument followed by the desired time scale integer.  This command line argument applies to both lostik_service.py and sms_new.py.  If the argument is not provided, time scale 1 is used by default.

#### Time Scale 1

Time scale 1 (default) specifies a TX window of 5 seconds.  With 4 nodes, this equates to a TX window occurring every 20 seconds (3x per minute) and lasting for a maximum of 5 seconds.  Time scale 1 has a maximum message length of 50 characters.

#### Time Scale 2

Time scale 2 specifies a TX window of 3 seconds.  With 4 nodes, this equates to a TX window occcurring every 12 seconds (5x per minute) and lasting for a maximum of 3 seconds.  Time scale 2 has a maximum message length of 30 characters.

### Accuracy of System Clock

Since we are using TDMA to control the TX/RX windows for each node, it is crucial that all nodes within the network have accurate time.  For best performance, it is recommended that you syncronize your system clock with internet time servers immediately before use of LoRa Chat TDMA.

#### Sync Clock - Windows 10

[How to Force Sync Time with Command in Windows](https://windowsloop.com/windows-time-sync-command/)

Open a command prompt as administrator then enter the following command:
w32tm /resync

#### Sync Clock - macOS

[macOS Date & Time Synchronization](https://superuser.com/questions/155785/mac-os-x-date-time-synchronization)

Open a terminal window and enter the following command:
sudo sntp -sS time.apple.com

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

This module contains all of the logic for interfacing with the Ronoth LoStik.  The LoStik Service accepts two optional command line arguments; time scale and power.  For additional details on usage please execute with the --help argument.

The LoStik Service begins by establishing all of the LoStik settings to be used with LoRa Chat.  Details of these settings can be observed by reviewing the module source code.  Next, the LoStik Service attempts to detect the presence of a LoStik attached to the computer and connect to it if found.  Once a connection is established, settings are written to the LoStik.  Finally, the service enters an infinite loop where the current time is used to determine if it is "safe" to transmit based on the selected time scale.  When a TX windows occurs, the service checks for outgoing messages and transmits one if found.  Otherwise the LoStik enters a receive state listening for messages from other nodes.

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

This module validates a user provided message of up to 30 or 50 characters (depending on selected time scale).  An SMS packet type identifier is appended and the resulting data is inserted into a new row within the sms table of lora_chat.db.  This module can be run interactively or non-interactively by passing the optional --msg command line argument.  If the message is passed via command line, the module will deposit the message into the database, report success/fail and exit.  If run interactively, the module will loop a prompt to provide an outgoing message.

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

## Normal Operation

Simply leave all three programs running in their terminal windows.  Newly received messages will automatically appear within SMS View.  Outgoing messages will not appear in SMS View until they are successfully transmitted.  The application runs in an infinite loop and is considered stable.  Data is saved to the database "on the fly" so even if execution is halted...  The chat history and selected station identifier remain.

To start over, simply delete the lora_chat.db file.  If you only want to clear the chat history, run sms_clear.py (preferably while sms_view.py is not running).

## Developed By

* **Chris Clement (K7CTC)** - [https://qrz.com/db/K7CTC](https://qrz.com/db/K7CTC)
