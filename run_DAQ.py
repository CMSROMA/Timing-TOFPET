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
    #outputFileName = opt.outputFolder+"/RunNumbers.txt"
    outputFileName = "/media/cmsdaq/ext/data/RunNumbers.txt"
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
    tags=newlabel.split('_')
    print(tags)
    posX=float(tags[4].replace('X',''))
    posY=float(tags[5].replace('Y',''))
    dbCommand = ". ~/AutoProcess/setup.sh; python3 ~/AutoProcess/insertRun.py --id=%s --type=%s --tag=%s --ov=%1.f --posx=%.1f --posy=%.1f "%(tags[0],runtype,newlabel,ov,posX,posY)
    if (runtype == 'PHYS'):
        dbCommand += ' --xtal=%s'%tags[2]
    print(dbCommand)
    insertDBStatus=os.WEXITSTATUS(os.system(dbCommand))
    if (not insertDBStatus==0):
        print('Error writing %s to runDB. Giving up'%tags[0])
        return

#    commandRun='sleep 5'
    exitStatus=os.WEXITSTATUS(os.system(commandRun))

    if (exitStatus==0):
        dbCommandCompleted = ". ~/AutoProcess/setup.sh; python3 ~/AutoProcess/updateRun.py --id=%s --status='%s'"%(tags[0],'DAQ COMPLETED')
        print(dbCommandCompleted)
        os.system(dbCommandCompleted)
        if (not insertDBStatus==0):
            print('Error writing %s to runDB. Giving up'%tags[0])
            return
        else:
            print('%s successfully inserted into RunDB'%tags[0])
        
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
t_ped = 0.3 #s
t_phys = 300 #s
t_tot = 320 #s this is approximate (it is 20-30% less of true value due to cpu processing time to make root files)
#ov_values = [-1] #V
ov_values = [7] #V
ovref_values = [7] #V
gate_values = [15] # DeltaT[ns]/20: gate=15 -> DeltaT=300 ns 
name = opt.nameLabel
'''

'''
#Main sequence (pixel+bar)
n_ch = 3 #number of channels in config file (2 for 2 pixels, 3 for 1 pixel and 1 bar, ..)
n_chip = 2 #number of active TOFPET2 chips
t_ped = 0.3 #s
t_phys = 300 #s
t_tot = 320  #s this is approximate (it is 20-30% less of true value due to cpu processing time to make root files)
#t_tot = 7200  #s this is approximate (it is 20-30% less of true value due to cpu processing time to make root files)
ov_values = [7] #V
#ov_values = [3,5,6,7]
ovref_values = [7] #V
#ov_values = [4,5,7] #V
gate_values = [15] # DeltaT[ns]/20: gate=15 -> DeltaT=300 ns 
#gate_values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25] 
#name = "TEST_WS1_NW_NC"
#name = "PEDESTAL_WS1_NW_NC_GATESCAN_1"
#name = "BAR000028_WS1_NW_NC"
name = opt.nameLabel
'''


#Main sequence (pixel+array)
n_ch = 33 #number of channels in config file (2 for 2 pixels, 3 for 1 pixel and 1 bar, ..)
n_chip = 2 #number of active TOFPET2 chips
t_ped = 0.3 #s
t_phys = 300#s
t_tot = 300  #s this is approximate (it is 20-30% less of true value due to cpu processing time to make root files)
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


#--------------------------------------------------------------------

if int(opt.pedAllChannels)==1:
    n_ch = n_chip*64

nseq = 1
#nseq = int( t_tot / ( (2*t_ped*n_ch+t_phys)*len(ov_values)*len(gate_values) ) )
#print "Number of sequences in "+str(t_tot)+" seconds = "+ str(nseq)
#if nseq==0:
#    print "==> Please increase total time of the run (t_tot)"

#--------------------------------------------------------------------

'''
########################
#Scan for bar
########################

#Reference Bar 
posFirstBarX = 24.9
posFirstBarY = 24.4
posPixelX = 22.5
posPixelY = 24.8

dict_PosScan = {
    #DEFAULT
    0: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_10_10"),

    #SCAN THRESHOLD T1 - BAR 
    #0: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_10_10"),
    #1: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_20_20"),
    #2: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_40_40")

    #0: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_5_5"),
    #1: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_10_10"),
    #2: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_15_15"),
    #3: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_20_20"),
    #4: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_25_25"),
    #5: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_30_30"),
    #6: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_35_35"),
    #7: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_40_40"),
    #8: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_45_45"),
    #9: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_50_50"),
    #10: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_55_55"),
    #11: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2","0_0_0","20_60_60")

    #SCAN THRESHOLD T1 - BAR in ARRAY (using BAR2 X=X40.1_Y23.0)
    #0: (round(40.1,1),round(23.0,1),"0_1_2","0_0_0","20_5_5"),
    #1: (round(40.1,1),round(23.0,1),"0_1_2","0_0_0","20_10_10"),
    #2: (round(40.1,1),round(23.0,1),"0_1_2","0_0_0","20_15_15"),
    #3: (round(40.1,1),round(23.0,1),"0_1_2","0_0_0","20_20_20"),
    #4: (round(40.1,1),round(23.0,1),"0_1_2","0_0_0","20_25_25"),
    #5: (round(40.1,1),round(23.0,1),"0_1_2","0_0_0","20_30_30")

}
print "Position scan" , dict_PosScan
'''


########################
#Scan for array
########################

#Reference Bar 
refBar = 5 #REF BAR N. = 5 (start counting from 0) so it's the sixth bar
posRefX = 31.6 
posRefY = 22.5
stepX = 3.2 #3.2mm step from one crystal center to another in X direction
posFirstBarX = posRefX + stepX*refBar 
posFirstBarY = posRefY

dict_PosScan = {

    ## BAD BARS (at least one channel with no signal): 8, 10, 13
    #0: (round(posFirstBarX,1),round(posFirstBarY,1),"0_1_2_17_18","0_0_10_0_10","20_10_10_10_10"),
    1: (round(posFirstBarX-1*stepX,1),round(posFirstBarY,1),"0_1_2_3_17_18_19","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    2: (round(posFirstBarX-2*stepX,1),round(posFirstBarY,1),"0_2_3_4_18_19_20","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    3: (round(posFirstBarX-3*stepX,1),round(posFirstBarY,1),"0_3_4_5_19_20_21","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    4: (round(posFirstBarX-4*stepX,1),round(posFirstBarY,1),"0_4_5_6_20_21_22","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    5: (round(posFirstBarX-5*stepX,1),round(posFirstBarY,1),"0_5_6_7_21_22_23","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    #6: (round(posFirstBarX-6*stepX,1),round(posFirstBarY,1),"0_6_7_8_22_23_24","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    #7: (round(posFirstBarX-7*stepX,1),round(posFirstBarY,1),"0_7_8_9_23_24_25","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
##    8: (round(posFirstBarX-8*stepX,1),round(posFirstBarY,1),"0_8_9_10_24_25_26","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    #9: (round(posFirstBarX-9*stepX,1),round(posFirstBarY,1),"0_9_10_11_25_26_27","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
##    10: (round(posFirstBarX-10*stepX,1),round(posFirstBarY,1),"0_10_11_12_26_27_28","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    #11: (round(posFirstBarX-11*stepX,1),round(posFirstBarY,1),"0_11_12_13_27_28_29","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    #12: (round(posFirstBarX-12*stepX,1),round(posFirstBarY,1),"0_12_13_14_28_29_30","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
##    13: (round(posFirstBarX-13*stepX,1),round(posFirstBarY,1),"0_13_14_15_29_30_31","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
    #14: (round(posFirstBarX-14*stepX,1),round(posFirstBarY,1),"0_14_15_16_30_31_32","0_10_0_10_10_0_10","20_10_10_10_10_10_10"),
##    15: (round(posFirstBarX-15*stepX,1),round(posFirstBarY,1),"0_15_16_31_32","0_10_0_10_0","20_10_10_10_10_10_10")

}
print "Position scan" , dict_PosScan


###################################################################
########################### Run DAQ ############################### 
###################################################################

#
aMover=XYMover(8820)
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
                    print(thisname)
                    #============================================
                    RUN("PED",t_ped,ov,ovref,gate,thisname,posInfo[2],"","")
                    RUN("PHYS",t_phys,ov,ovref,gate,thisname,posInfo[2],posInfo[3],posInfo[4]) 
                    RUN("PED",t_ped,ov,ovref,gate,thisname,posInfo[2],"","")
                    #============================================

    #time.sleep(3600)
                    
                    ##RUN("PHYS",t_phys,ov,ovref,gate,thisname,"0_6_7_8_22_23_24","0_10_0_10_10_0_10") #trigger on a subset of channels
                    #RUN("PHYS",t_phys,ov,ovref,gate,thisname,"","") #trigger on all channels
                    
