import math
import string
import ROOT
import csv
import sys
from array import *
import re
from ROOT import *

## Inputs
#f = open("temperature_TestCoolingWithElectronics_06_06_2019.txt", "r")
#f = open("temperature_TestCoolingWithElectronics_19_06_2019.txt", "r")
f = open("temperature_calibration_DS18B20_21_06_2019_good.txt", "r")

nSensors = 6

## Create root file
outfile = TFile( 'TempTree.root', 'recreate' )

## Create Tree
outTree = TTree( 'tree', 'ROOT tree' )
nSens = array( 'i', [ 0 ] )
time = array( 'd', [ 0. ] )
temp = array( 'f', nSensors*[ 0. ] )
outTree.Branch( 'nSens', nSens, 'nSens/I' )
outTree.Branch( 'time', time, 'time/D' )
outTree.Branch( 'temp', temp, 'temp[nSens]/F' )

## Read temperature file
lines = f.readlines()
#print lines
counter = -1
for line in lines:
    line = line.rstrip('\n')
    line = line.rstrip('\r')
    #print line
    splittedline = line.split(' ')
    #print len(splittedline)
    if (len(splittedline) == int(nSensors+1)):
        counter = counter+1        

        #dateTimeElements = splittedline[0].split('-')
        #currentyear = "20" + str(dateTimeElements[0])
        #datetime = ROOT.TDatime(int(currentyear),int(dateTimeElements[1]),int(dateTimeElements[2]),int(dateTimeElements[3]),int(dateTimeElements[4]),int(dateTimeElements[5]))
        #timevalue = datetime.Convert()
        #time[0] = float(timevalue)

        time[0] = float(splittedline[0])

        #print time[0]
        for sens in xrange(0,nSensors):
            #print splittedline[0]
            temp[sens] = float(splittedline[sens+1])
            #print temp[sens]
        
        nSens[0]=nSensors            

        ## Fill tree for this event
        outTree.Fill() 

outfile.Write()
outfile.Close()
