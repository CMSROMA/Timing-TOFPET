#! /usr/bin/env python

import os
import sys
import optparse
import datetime
import subprocess
from glob import glob
from collections import defaultdict
from collections import OrderedDict
from array import array

from ROOT import *

usage = "usage: run from Timing-TOFPET: python analysis/find_coincidences.py -c config_main.txt -i xxx_singles.root -o xxx_coincidences.root -n 3"

parser = optparse.OptionParser(usage)

parser.add_option("-c", "--config", dest="configFile",
                  help="config file")

parser.add_option("-i", "--input", dest="inputRootFile",
                  help="input root file with singles")

parser.add_option("-o", "--output", dest="outputRootFile",
                  help="output root file with coincidences")

parser.add_option("-n", "--nch", dest="nch",
                  help="number of active channels")

parser.add_option("-p", "--prescale", dest="prescale",
                  default=1,
                  help="prescale of singles")

(opt, args) = parser.parse_args()

if not opt.configFile:   
    parser.error('config file not provided')

if not opt.inputRootFile:   
    parser.error('input root file not provided')

if not opt.outputRootFile:   
    parser.error('output root file not provided')

if not opt.nch:   
    parser.error('number of active channels not provided')

################################################

gROOT.SetBatch(True)

###############################
### 0) Read config file
###############################
cfg = open(opt.configFile, "r")

channel_map = {}
channels = []

for line in cfg:

    #skip commented out lines or empty lines
    if (line.startswith("#")):
        continue
    if line in ['\n','\r\n']:
        continue

    line = line.rstrip('\n')
    splitline = line.split()
    linetype = splitline[0]
    linesize = len(splitline)

    if (linetype == "CH" and linesize==16):
        #read channel settings
        chId = splitline[1]
        channels.append(chId)        

        NCHIP = splitline[5]
        NCH = splitline[6]
        ABS_CHID = int(64 * int(NCHIP) + int(NCH))

        channel_map[ABS_CHID]=chId

print "Channel Map: key=absolute Ch. in hardware ; element=Channel Idx from config file"
print channel_map

###############################
### 1) Create root file
###############################
tfileinput = TFile.Open(opt.inputRootFile)
treeInput = tfileinput.Get("data")
nEntries = treeInput.GetEntries()

tfileoutput = TFile( opt.outputRootFile, 'recreate' )
treeOutput = TTree( 'data', 'tree with coincidences' )

maxn = int(opt.nch)
unixTime = array( 'l' , [0])
temp1 = array( 'd' , [-999.])
temp2 = array( 'd' , [-999.])
temp3 = array( 'd' , [-999.])
n_channels = array( 'i', [ -9 ] )
n_coincidences = array( 'i', [ -9 ] )
a_chId = array( 'd', maxn*[ -9. ] )
a_energy = array( 'd', maxn*[ -9. ] )
a_time = array( 'd', maxn*[ -9. ] )

for absChId in channel_map:
    a_chId[ int(channel_map[int(absChId)]) ] = absChId

treeOutput.Branch( 'nch', n_channels, 'nch/I' )
treeOutput.Branch( 'ncoinc', n_coincidences, 'ncoinc/I' )
treeOutput.Branch( 'chId', a_chId, 'chId[nch]/D' )
treeOutput.Branch( 'energy', a_energy, 'energy[nch]/D' )
treeOutput.Branch( 'time', a_time, 'time[nch]/D' )
treeOutput.Branch( 'unixTime', unixTime, 'unixTime/L' )
treeOutput.Branch( 'temp1', temp1, 'temp1/D' )
treeOutput.Branch( 'temp2', temp2, 'temp2/D' )
treeOutput.Branch( 'temp3', temp3, 'temp3/D' )

i_singles=0
while i_singles<nEntries:

    if i_singles == nEntries-1:
        break

    if int(i_singles)%int(opt.prescale) != 0:
        i_singles += 1
        continue

    if int(i_singles)%100000 == 0:
        print i_singles

    #if i_singles>1000:
    #    break

    #print "===> i_singles= ", i_singles
    treeInput.GetEntry(i_singles)

    n_channels[0] = int(opt.nch)
    unixTime[0] = long(treeInput.unixTime)
    temp1[0] = treeInput.temp1
    temp2[0] = treeInput.temp2
    temp3[0] = treeInput.temp3

    #ref (first in the list) channel
    t_ref = treeInput.time

    #print str(treeInput.channelID)+ " --> "+ str(channel_map[int(treeInput.channelID)])
    if treeInput.channelID not in channel_map.keys():
        i_singles += 1
        continue

    a_chId[ int(channel_map[int(treeInput.channelID)]) ] = treeInput.channelID
    a_energy[ int(channel_map[int(treeInput.channelID)]) ] = treeInput.energy
    a_time[ int(channel_map[int(treeInput.channelID)]) ] = treeInput.time

    n_coinc=0
    nch_check_coinc = (int(opt.nch)-1)

    for k in range(i_singles+1, i_singles+1+nch_check_coinc):

        #print "k= ", k
        treeInput.GetEntry(k)

        if treeInput.channelID not in channel_map.keys():
            i_singles = k
            break

        #time coincidence
        time_coinc = 0
        t_current = treeInput.time
        t_diff = t_current - t_ref
        if abs(t_diff) < 20000: #ps -> 20ns
            time_coinc = 1

        if not time_coinc: #no time coincidence found
            #print "no coincidence found between ref "+str(i_singles)+" and current "+str(k)
            i_singles = k
            break
        else: #time coincidence found
            #channelIdx = k - i_singles
            a_chId[ int(channel_map[int(treeInput.channelID)]) ] = treeInput.channelID
            a_energy[ int(channel_map[int(treeInput.channelID)]) ] = treeInput.energy
            a_time[ int(channel_map[int(treeInput.channelID)]) ] = treeInput.time
            n_coinc=n_coinc+1 
            #print "===> i_singles= ", i_singles
            #print "k= ", k
            #print "t_current="+str(t_current)+" t_ref="+str(t_ref)+" t_diff="+str(t_diff)
            #print "coincidence found between "+str(i_singles)+" and "+str(k)
            #print a_time[channelIdx]

            if k==i_singles+1+nch_check_coinc-1:
                i_singles = k+1
                #print "End"
                break
            else:
                continue

    #print n_coinc
    n_coincidences[0] = int(n_coinc)

    if n_coinc>0:
        treeOutput.Fill()

tfileoutput.cd()
tfileoutput.Write()
tfileoutput.Close()
print opt.outputRootFile+" created."

tfileinput.cd()
tfileinput.Close()
