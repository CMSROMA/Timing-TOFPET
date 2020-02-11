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

usage = "usage: run from Timing-TOFPET: \n python run_DAQ.py -c config_main_bar.txt -o /data/TOFPET/LYSOBARS -n BAR000028_WS1_NW_NC" 
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
#Position scan for pixels
########################

#Reference Bar 
posPixelX = 22.6
posPixelY = 25.0

dict_PosScan = {
    #YSCAN - PIXEL
    0: (round(posPixelX,1),round(posPixelY-8.0,1),"0","0","20"),
    1: (round(posPixelX,1),round(posPixelY-6.0,1),"0","0","20"),
    2: (round(posPixelX,1),round(posPixelY-5.0,1),"0","0","20"),
    3: (round(posPixelX,1),round(posPixelY-4.0,1),"0","0","20"),
    4: (round(posPixelX,1),round(posPixelY-3.0,1),"0","0","20"),
    5: (round(posPixelX,1),round(posPixelY-2.0,1),"0","0","20"),
    6: (round(posPixelX,1),round(posPixelY-1.0,1),"0","0","20"),
    7: (round(posPixelX,1),round(posPixelY,1),"0","0","20"),
    8: (round(posPixelX,1),round(posPixelY+1.0,1),"0","0","20"),
    9: (round(posPixelX,1),round(posPixelY+2.0,1),"0","0","20"),
    10: (round(posPixelX,1),round(posPixelY+3.0,1),"0","0","20"),
    11: (round(posPixelX,1),round(posPixelY+4.0,1),"0","0","20"),
    12: (round(posPixelX,1),round(posPixelY+5.0,1),"0","0","20"),
    13: (round(posPixelX,1),round(posPixelY+6.0,1),"0","0","20"),
    14: (round(posPixelX,1),round(posPixelY+8.0,1),"0","0","20"),

    #XSCAN - PIXEL
    15: (round(posPixelX-8.0,1),round(posPixelY,1),"0","0","20"),
    16: (round(posPixelX-6.0,1),round(posPixelY,1),"0","0","20"),
    17: (round(posPixelX-5.0,1),round(posPixelY,1),"0","0","20"),
    18: (round(posPixelX-4.0,1),round(posPixelY,1),"0","0","20"),
    19: (round(posPixelX-3.0,1),round(posPixelY,1),"0","0","20"),
    20: (round(posPixelX-2.0,1),round(posPixelY,1),"0","0","20"),
    21: (round(posPixelX-1.0,1),round(posPixelY,1),"0","0","20"),
    22: (round(posPixelX,1),round(posPixelY,1),"0","0","20"),
    23: (round(posPixelX+1.0,1),round(posPixelY,1),"0","0","20"),
    24: (round(posPixelX+2.0,1),round(posPixelY,1),"0","0","20"),
    25: (round(posPixelX+3.0,1),round(posPixelY,1),"0","0","20"),
    26: (round(posPixelX+4.0,1),round(posPixelY,1),"0","0","20"),
    27: (round(posPixelX+5.0,1),round(posPixelY,1),"0","0","20"),
    28: (round(posPixelX+6.0,1),round(posPixelY,1),"0","0","20"),
    29: (round(posPixelX+8.0,1),round(posPixelY,1),"0","0","20")
}

print "Position scan" , dict_PosScan

###################################################################
########################### Run DAQ ############################### 
###################################################################

aMover=XYMover(8821) # 8821 = motor_1 = pixel
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

