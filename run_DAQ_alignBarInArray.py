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

sys.path.insert(1, os.path.join(sys.path[0], './arduino/tablexy'))
from xyMover import XYMover

usage = "usage: run from Timing-TOFPET: \n python run_DAQ_alignBarInArray.py -c config_main_array.txt -o /media/cmsdaq/ext/data/ALIGNMENT/ALIGNARRAY_11_02_2020 -n ALIGNARRAY" 
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
def RUN(runtype,time,ov,ovref,gate,label,enabledCh="",thresholds="",thresholdsT1=""):

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
        if (enabledCh!=""):
            commandRun = commandRun +" --enabledChannels " + str(enabledCh) 

    if(runtype == "PHYS"):
        commandRun = "python run_TOFPET.py -c "+ opt.configFile+" --runType PHYS -d my_acquire_sipm_data " + "-t "+ str(time)+" -v "+str(ov)+" --ovref "+str(ovref)+" -l "+str(newlabel)+" -g "+str(gate)+" -o "+opt.outputFolder
        if (enabledCh!=""):
            commandRun = commandRun +" --enabledChannels " + str(enabledCh) 
            if (thresholds!=""):
                commandRun = commandRun + " --energyThr " + str(thresholds)
            if (thresholdsT1!=""):
                commandRun = commandRun + " --energyThrT1 " + str(thresholdsT1)

    print commandRun
    os.system(commandRun)

    return;

###################
## Run daq sequence
###################
t_ped = 0.3 #s
t_phys = 10 #s
ov_values = [7] #V
ovref_values = [7] #V
gate_values = [15] # DeltaT[ns]/20: gate=15 -> DeltaT=300 ns 
name = opt.nameLabel

nseq = 1

#--------------------------------------------------------------------

########################
#Position scan for bar in array
########################

#Reference Bar 
refBar = 5 #REF BAR N. = 5 (start counting from 0) so it's the sixth bar
posRefX = 32.7 
posRefY = 20.3

dict_PosScan = {

    ##ALIGN BAR X
    0: (round(posRefX-12.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    1: (round(posRefX-8.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    2: (round(posRefX-4.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    3: (round(posRefX-3.5,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    4: (round(posRefX-3.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    5: (round(posRefX-2.5,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    6: (round(posRefX-2.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    7: (round(posRefX-1.5,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    8: (round(posRefX-1.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    9: (round(posRefX-0.5,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    10: (round(posRefX,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    11: (round(posRefX+0.5,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    12: (round(posRefX+1.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    13: (round(posRefX+1.5,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    14: (round(posRefX+2.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    15: (round(posRefX+2.5,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    16: (round(posRefX+3.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    17: (round(posRefX+3.5,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    18: (round(posRefX+4.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    19: (round(posRefX+8.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    20: (round(posRefX+12.0,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),

    ##ALIGN BAR Y
    21: (round(posRefX,1),round(posRefY-15.0,1),"0_6_22","0_0_0","20_10_10"),
    22: (round(posRefX,1),round(posRefY-12.0,1),"0_6_22","0_0_0","20_10_10"),
    23: (round(posRefX,1),round(posRefY-9.0,1),"0_6_22","0_0_0","20_10_10"),
    24: (round(posRefX,1),round(posRefY-6.0,1),"0_6_22","0_0_0","20_10_10"),
    25: (round(posRefX,1),round(posRefY-4.0,1),"0_6_22","0_0_0","20_10_10"),
    26: (round(posRefX,1),round(posRefY-2.0,1),"0_6_22","0_0_0","20_10_10"),
    27: (round(posRefX,1),round(posRefY,1),"0_6_22","0_0_0","20_10_10"),
    28: (round(posRefX,1),round(posRefY+2.0,1),"0_6_22","0_0_0","20_10_10"),
    29: (round(posRefX,1),round(posRefY+4.0,1),"0_6_22","0_0_0","20_10_10"),
    30: (round(posRefX,1),round(posRefY+6.0,1),"0_6_22","0_0_0","20_10_10"),
    31: (round(posRefX,1),round(posRefY+9.0,1),"0_6_22","0_0_0","20_10_10"),
    32: (round(posRefX,1),round(posRefY+12.0,1),"0_6_22","0_0_0","20_10_10"),
    33: (round(posRefX,1),round(posRefY+15.0,1),"0_6_22","0_0_0","20_10_10")

}

print "Position scan" , dict_PosScan

###################################################################
########################### Run DAQ ############################### 
###################################################################

aMover=XYMover(8820) # 8820 = motor_0 = bar or array or second pixel
print (aMover.estimatedPosition())

for seq in range(0,nseq):
    for ov in ov_values:
        for ovref in ovref_values:
            for gate in gate_values:
                for posStep, posInfo in dict_PosScan.items():

                    print "++++ Centering Bar: "+str(posStep)+": X="+str(posInfo[0])+" Y="+str(posInfo[1])+" Channels="+str(posInfo[2])+" +++++"
                    print aMover.moveAbsoluteXY(posInfo[0],posInfo[1])
                    if (aMover.moveAbsoluteXY(posInfo[0],posInfo[1]) is "error"):
                        print "== Out of range: skipping this position =="
                        continue
                    print aMover.estimatedPosition()
                    print "++++ Done +++++"                    

                    thisname = name+"_POS"+str(posStep)+"_X"+str(posInfo[0])+"_Y"+str(posInfo[1])+"_CH"+str(posInfo[2]).replace("_","-")+"_ETHR"+str(posInfo[3]).replace("_","-")+"_T1THR"+str(posInfo[4]).replace("_","-")

                    #============================================
                    #RUN("PED",t_ped,ov,ovref,gate,thisname,posInfo[2],"","")
                    RUN("PHYS",t_phys,ov,ovref,gate,thisname,posInfo[2],posInfo[3],posInfo[4]) 
                    #RUN("PED",t_ped,ov,ovref,gate,thisname,posInfo[2],"","")
                    #============================================

