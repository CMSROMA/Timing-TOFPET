##############################################################################
#
#    grblServer - copyright (c) by giovanni.organtini@uniroma1.it (2018)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

import serial
import socket
import argparse
import logging
import re
import sys
from time import sleep

from curses import ascii

# Version
def version():
    print("grblServer.py v 1.0")
    print("copyright (c) by giovanni.organtini@uniroma1.it 2018")
    print("")
    print("This program acts as a server to which commands are sent for a CNC Arduino shield")
    print("Accepted commands are in the following regexp format:")
    print("[+-][0-9]+ [+-][0-9]+  (e.g. +82 -56) performs a relative movement w.r.t. the current position")
    print("[0-9]+ [0-9]+          (e.g. 180 290) moves to the given coordinates")
    print("home                   perform a home search")
    print("reset                  perform a reset - be careful: reset may be needed after limits are reached")
    print("position               returns the current absolute position of the table")
    print("status                 returns the curent status")
    print("quit                   exit")
    exit(0)

def help():
    version()
    return ret

# Gcommand
def Gcommand(Gstring, arduino):
    logging.debug(Gstring)
    ret = ''
    demo = None

    if (arduino == 'DEMO'):
        demo = True

    if (not demo and not arduino):
        ret = 'Arduino not connected'
    data = ''
    if (len(Gstring) > 0) and (arduino != ""):
        Gstring += '\n'
        if (not demo):
            arduino.reset_input_buffer()
            arduino.reset_output_buffer()
            arduino.write(Gstring.encode('utf-8'))
#            while not (data.startswith('ok') or data.startswith('error')):
            sleep(0.1)
            data = arduino.readline().decode("utf-8").strip() #the last bit gets rid of the new-line chars
        else:
            data = 'ok'
        ret += data + '\n'
        logging.debug(data)
    return ret

##############################################################################

# argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int, default=8820,
                    help="The port to which the server listen")
parser.add_argument("-u", "--usb", default="/dev/cu.usbmodem14201",
                    help="The USB port to which Arduino is attached")
parser.add_argument("-l", "--log", default="/var/log/grblServer.log",
                    help="The server logfile")
parser.add_argument("-d", "--demo", action='store_true',
                    help="Demo mode (no actual connection to usb port)")
parser.add_argument("-v", action="store_true", help="Prints a brief help and version information")
args = parser.parse_args()

if (args.v):
    version()

logging.basicConfig(filename=args.log,level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
logstr = '%s %d' % ("Starting grblServer on port", args.port)
logging.info("==========================================================================")
logging.info(logstr)
logging.info("==========================================================================")

arduino = None

# connect to Arduino
try:
    logging.info("Connecting to Arduino via " + args.usb)
    if (not args.demo):
        arduino = serial.Serial(args.usb, 9600)
    else:
        arduino = 'DEMO'
except:
    print("[ERROR] Cannot connect to Arduino")
    logging.warning("Cannot connect to Arduino")
    logging.warning(sys.exc_info())
    exit(-1)

if (not args.demo):
    arduino.write(b'\x18')
    data = arduino.readline().decode("utf-8") 
else:
    data = 'ok'
logging.info(data)

logging.info("Ready. Waiting for clients")
# open the server on the given port on the local host
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', args.port))
server_socket.listen(1)
(client_socket, client_address) = server_socket.accept()
logging.info("Client connected from " + client_address[0])

# initialize
Gcommand('$X', arduino)         #unlock
Gcommand('$0=266.667', arduino) #(x, step/mm)
Gcommand('$1=266.667', arduino) #(y, step/mm)
Gcommand('$2=755.906', arduino) #(z, step/mm)
Gcommand('$3=10', arduino)      #(step pulse, usec)
Gcommand('$4=250.000', arduino) #(default feed, mm/min)
Gcommand('$5=125.000', arduino) #(default seek, mm/min)
Gcommand('$6=28', arduino)      #(step port invert mask, int:00011100)
Gcommand('$7=25', arduino)      #(step idle delay, msec)
Gcommand('$8=50.000', arduino)  #(acceleration, mm/sec^2)
Gcommand('$9=0.050', arduino)   #(junction deviation, mm)
Gcommand('$10=0.100', arduino)  #(arc, mm/segment)
Gcommand('$11=25', arduino)     #(n-arc correction, int)
Gcommand('$12=3', arduino)      #(n-decimals, int)
Gcommand('$13=0', arduino)      #(report inches, bool)
Gcommand('$14=1', arduino)      #(auto start, bool)
Gcommand('$15=0', arduino)      #(invert step enable, bool)
Gcommand('$16=1', arduino)      #(hard limits, bool)
Gcommand('$17=1', arduino)      #(homing cycle, bool)
Gcommand('$18=0', arduino)      #(homing dir invert mask, int:00000000)
Gcommand('$19=250.000', arduino)#(homing feed, mm/min)
Gcommand('$20=125.000', arduino)#(homing seek, mm/min)
Gcommand('$21=100', arduino)    #(homing debounce, msec)
Gcommand('$22=1.000', arduino)  #(homing pull-off, mm)
Gcommand('G21', arduino)        # use metric units (mm)
Gcommand('$H', arduino)         # go home

# loop

x = 0
y = 0

while (True):
    ret = "invalid command"

    client_data = client_socket.recv(1024)        

    if not client_data:
        client_socket.close()
        logging.info("Client disconnected")
        logging.info("==========================================================================")
        (client_socket, client_address) = server_socket.accept()
        logging.info("Client connected from " + client_address[0])
        client_data = client_socket.recv(1024)        

    client_data = client_data.decode('utf-8').strip() # trim the input string
    client_data = re.sub(" +", " ", client_data)
    xy = client_data.split(" ")
    logging.debug("Received: %s" % client_data)

    absolute = re.match("[0-9]*\.?[0-9]+ [0-9]*\.?[0-9]+", client_data)
    relative = re.match("[\+-][0-9]*\.?[0-9]+ [\+-][0-9]*\.?[0-9]+", client_data)

#   About the sign of the coordinates
#
#   Motors move in the negative direction
#   To simplify the protocol we accept positive coordinates whose sign
#   is inverted prior to be used, then, to estimate the current position,
#   inverted again 

    xold = x
    yold = y

    if (absolute):
        x = -1.*float(xy[0])
        y = -1.*float(xy[1])
        if ((x <= -1) and (x >= -48) and (y <= -1) and (y >= -48)):
            ret = Gcommand("G90 G01 X%3.1f Y%3.1f"%(x,y), arduino)
        else:
            ret = "Invalid coordinates"
            x = xold
            y = yold

    if (relative):
        dx = -1.*float(xy[0])
        dy = -1.*float(xy[1])
        x += dx
        y += dy
        if ((x <= -1) and (x >= -48) and (y <= -1) and (y >= -48)):
            ret = Gcommand("G91 G01 X%3.1f Y%3.1f"%(dx,dy), arduino)
        else:
            ret = "Invalid coordinates"
            x = xold
            y = yold

    if re.match("home", client_data):
        Gcommand("$H", arduino)
        x = -1
        y = -1
        ret = "ok"

    if re.match("status", client_data):
        ret = Gcommand("?", arduino)
       
    if re.match("reset", client_data):
        if (not args.demo):
            arduino.write(b'\x18')
            data = arduino.readline().decode("utf-8") 
        else:
            data = 'ok'
        logging.info("Reset: " + data)
        ret = "ok"

    if re.match("position", client_data):
        ret = "%3.1f %3.1f%"%(-x,-y)

#    if re.match("help", client_data):
#        help()

#    if (client_data=='quit'):
#        ret = 'Quit. Bye' 

    client_socket.send(bytes(ret,'utf-8'))

    logging.info("Estimated position: (%3.1f,%3.1f)"%(-x,-y))

    sleep(0.001)
#    if (client_data == "quit"):
#        client_socket.close()
#        server_socket.close()
#        logging.info("Quit")
#        logging.info("==========================================================================")
#        exit(0)


