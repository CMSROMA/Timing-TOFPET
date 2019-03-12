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
(opt, args) = parser.parse_args()
if not opt.configFile:   
    parser.error('config file not provided')
if not opt.outputFolder:   
    parser.error('output folder not provided')

#############################

commandOutputDir = "mkdir -p "+opt.outputFolder
print commandOutputDir
os.system(commandOutputDir)

#############################
## Daq setup
#############################
def RUN(runtype,time,ov,gate,label):

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
        commandRun = "python run_TOFPET.py -c "+ opt.configFile+" --runType PED -d acquire_pedestal_data " + "-t "+ str(time)+" -v "+str(ov)+" -l "+str(newlabel)+" -g "+str(gate)+" -o "+opt.outputFolder

    if(runtype == "PHYS"):
        commandRun = "python run_TOFPET.py -c "+ opt.configFile+" --runType PHYS -d acquire_sipm_data " + "-t "+ str(time)+" -v "+str(ov)+" -l "+str(newlabel)+" -g "+str(gate)+" -o "+opt.outputFolder

    print commandRun
    #os.system(commandRun)

    return;

###################
## Run daq sequence
###################

#Main sequence
t_ped = 10 #s
t_phys = 300 #s
t_tot = 400 #s
ov_values = [3,5,7] #V
gate_values = [10,15] # DeltaT[ns]/20: gate=15 -> DeltaT=300 ns 
name = "Na22"
nseq = int( t_tot / ( (2*t_ped+t_phys)*len(ov_values)*len(gate_values) ) )
print "Number of sequences in "+str(t_tot)+" seconds = "+ str(nseq)
if nseq==0:
    print "==> Please increase total time of the run (t_tot)"

for seq in range(0,nseq):
    for ov in ov_values:
        for gate in gate_values:
            RUN("PED",t_ped,ov,gate,name)
            RUN("PHYS",t_phys,ov,gate,name)
            RUN("PED",t_ped,ov,gate,name)

