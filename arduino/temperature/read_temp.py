import serial
import time
import datetime
import optparse

usage = "usage: python3 read_temp.py [-o temperature.txt -p /dev/ttyACM1 -r 9600]"

parser = optparse.OptionParser(usage)

parser.add_option("-o", "--output", dest="outputFile",
                  default="temperature.txt",
                  help="output file")

parser.add_option("-p", "--port", dest="serialPort",
                  default="/dev/ttyACM1",
                  help="serial port")

parser.add_option("-r", "--rate", dest="rate",
                  default="9600",
                  help="baud rate")

(opt, args) = parser.parse_args()

#Check
#list serial ports: ls /dev/{tty,cu}.* 
#screen -L /dev/tty.usbXXXXX 9600
#screen -X -A /dev/tty.usbXXXXX quit (to kill a detached version)
ser = serial.Serial(opt.serialPort, opt.rate) 

#To avoid weird characters appearing at the beginning of the output file
ser.readline()
ser.readline()
ser.readline()

while True:
    outputfile = open(opt.outputFile,"a")  
    #output = str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")) + " " + str(ser.readline())
    line = ser.readline().decode("utf-8")
    output = str(int(time.time())) + " " + str(line)
    outputfile.write(output)
    outputfile.close()
