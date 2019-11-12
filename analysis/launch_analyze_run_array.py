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

usage = "usage: python analysis/launch_analyze_run_array.py --firstRun 1 -i /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/output/TestArray -o /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/output/TestArray/RESULTS --arrayCode 0"

parser = optparse.OptionParser(usage)

parser.add_option("-r", "--firstRun", dest="firstRun",
                  help="first run number of the position scan")

parser.add_option("-i", "--input", dest="inputDir",default="/data/TOFPET/LYSOARRAYS",
                  help="input directory")

parser.add_option("-o", "--output", dest="outputDir",default="/data/TOFPET/LYSOARRAYS/RESULTS",
                  help="output directory")

parser.add_option("-b", "--arrayCode", dest="arrayCode", default=-99,
                  help="code of the crystal array")

(opt, args) = parser.parse_args()

if not opt.firstRun:   
    parser.error('first run number not provided')

if not opt.inputDir:   
    parser.error('input directory not provided')

if not opt.outputDir:   
    parser.error('output directory not provided')

#------------------------------------------------

nFilesInScan = 12

commandMerge = "hadd -f "+str(opt.outputDir)+"/"+"tree_"+"FirstRun" + str(opt.firstRun.zfill(6)) + "_LastRun" + str((int(opt.firstRun)+(nFilesInScan-1)*3)).zfill(6) + "_ARRAY" + str(opt.arrayCode.zfill(6))+".root"
print commandMerge

for step in range(0,nFilesInScan):

    #    #Inactive bars (disconnected or not working)
    #    if (step==8 or step==10 or step==13):
    #        continue

    #Launch analysis for each step of the position scan
    print step
    currentRun = int(opt.firstRun) + step*3    
    command = "python analysis/analyze_run_array.py --run "+ str(currentRun) +" --arrayCode "+str(opt.arrayCode)+" -i "+str(opt.inputDir)+" -o "+str(opt.outputDir)
    print command
    #os.system(command)

    #Update command to merge trees
    commandMerge = commandMerge+" "+str(opt.outputDir)+"/"+"tree"+"_Run"+str(currentRun).zfill(6)+"_*"
    
print commandMerge
#os.system(commandMerge)
