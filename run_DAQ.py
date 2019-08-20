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
import time
import re

usage = "usage: run from Timing-TOFPET: \n python run_DAQ.py -c config_main.txt -o output/ScanTest"
parser = optparse.OptionParser(usage)
parser.add_option("-c", "--config", dest="configFile",
                  help="config file")
parser.add_option("-o", "--outFolder", dest="outputFolder",
                  help="output directory")
parser.add_option("--pedAllChannels", dest="pedAllChannels", default=0, 
                  help="Set to 1 to collect pedestals for all channels (default is 0)")
parser.add_option("-n", "--name", dest="nameLabel",
                  help="label for output files")
(opt, args) = parser.parse_args()
if not opt.configFile:   
    parser.error('config file not provided')
if not opt.outputFolder:   
    parser.error('output folder not provided')
if not opt.nameLabel:   
    parser.error('label for output files not provided')

#############################

commandOutputDir = "mkdir -p "+opt.outputFolder
print commandOutputDir
os.system(commandOutputDir)

#############################
## Daq setup
#############################
def RUN(runtype,time,ov,ovref,gate,label):

    ###############
    ## Current time
    ###############
    current_time = datetime.datetime.now()
    simpletimeMarker = "%04d-%02d-%02d-%02d-%02d-%02d" % (current_time.year,current_time.month,current_time.day,current_time.hour,current_time.minute,current_time.second)
    print simpletimeMarker

    ####################
    ## Update run number
    ####################
    currentRun = 0
    outputFileName = opt.outputFolder+"/RunNumbers.txt"
    file_runs = open(outputFileName, 'a+')
    
    lastRun = subprocess.check_output(['tail', '-1', outputFileName])
    lastRun = lastRun.rstrip('\n')
    
    if not lastRun:
        currentRun = 1
    else:
        currentRun = int(lastRun) + 1
    file_runs.write(str(currentRun)+'\n')    
    file_runs.close()

    #################
    ## Write commands
    #################
    newlabel = "Run"+str(currentRun).zfill(6)+"_"+simpletimeMarker+"_"+label

    if(runtype == "PED"):
        commandRun = "python run_TOFPET.py -c "+ opt.configFile+" --runType PED -d acquire_pedestal_data " + "-t "+ str(time)+" -v "+str(ov)+" --ovref "+str(ovref)+" -l "+str(newlabel)+" -g "+str(gate)+" -o "+opt.outputFolder+" --pedAllChannels " + str(opt.pedAllChannels)

    if(runtype == "PHYS"):
        commandRun = "python run_TOFPET.py -c "+ opt.configFile+" --runType PHYS -d acquire_sipm_data " + "-t "+ str(time)+" -v "+str(ov)+" --ovref "+str(ovref)+" -l "+str(newlabel)+" -g "+str(gate)+" -o "+opt.outputFolder

    print commandRun
    os.system(commandRun)

    return;

###################
## Run daq sequence
###################

#Test sequence
#RUN("PED",0.1,-1,15,"PedestalTestAllCh10kHz")

'''
#Main sequence (2 pixels)
n_ch = 2 #number of channels in config file (2 for 2 pixels, 3 for 1 pixel and 1 bar, ..)
n_chip = 2 #number of active TOFPET2 chips
t_ped = 0.1 #s
t_phys = 300 #s
t_tot = 10800 #s this is approximate (it is 20-30% less of true value due to cpu processing time to make root files)
#ov_values = [-1] #V
ov_values = [4,5,7] #V
gate_values = [15] # DeltaT[ns]/20: gate=15 -> DeltaT=300 ns 
name = "Na22PedAllChannels"
'''

#Main sequence (pixel+bar)
n_ch = 3 #number of channels in config file (2 for 2 pixels, 3 for 1 pixel and 1 bar, ..)
n_chip = 2 #number of active TOFPET2 chips
t_ped = 1 #s
t_phys = 300 #s
t_tot = 320  #s this is approximate (it is 20-30% less of true value due to cpu processing time to make root files)
#t_tot = 7200  #s this is approximate (it is 20-30% less of true value due to cpu processing time to make root files)
ov_values = [7] #V
ovref_values = [7] #V
#ov_values = [4,5,7] #V
gate_values = [15] # DeltaT[ns]/20: gate=15 -> DeltaT=300 ns 
#gate_values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25] 
#name = "TEST_WS1_NW_NC"
#name = "PEDESTAL_WS1_NW_NC_GATESCAN_1"
#name = "BAR000028_WS1_NW_NC"
name = opt.nameLabel

if int(opt.pedAllChannels)==1:
    n_ch = n_chip*64

nseq = 1
#nseq = int( t_tot / ( (2*t_ped*n_ch+t_phys)*len(ov_values)*len(gate_values) ) )
#print "Number of sequences in "+str(t_tot)+" seconds = "+ str(nseq)
if nseq==0:
    print "==> Please increase total time of the run (t_tot)"

for seq in range(0,nseq):
    for ov in ov_values:
        for ovref in ovref_values:
            for gate in gate_values:
                RUN("PED",t_ped,ov,ovref,gate,name)
                RUN("PHYS",t_phys,ov,ovref,gate,name)
                RUN("PED",t_ped,ov,ovref,gate,name)

