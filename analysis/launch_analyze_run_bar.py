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

usage = "usage: python analysis/launch_analyze_run_bar.py --firstRun 1 -i /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/output/TestArray -o /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/output/TestArray/RESULTS --barCode 0"

parser = optparse.OptionParser(usage)

parser.add_option("--firstRun", dest="firstRun",
                  help="first (pedestal) run number of the scan")

parser.add_option("--lastRun", dest="lastRun",
                  help="last (pedestal) run number of the scan")

parser.add_option("-i", "--input", dest="inputDir",default="/data/TOFPET/LYSOBARS",
                  help="input directory")

parser.add_option("-o", "--output", dest="outputDir",default="/data/TOFPET/LYSOBARS/RESULTS",
                  help="output directory")

parser.add_option("-b", "--barCode", dest="barCode", default=-99,
                  help="code of the crystal bar")

parser.add_option("--barInArray", dest="barInArray", action='store_true', default='False',
                  help="the bar is inside an array")

(opt, args) = parser.parse_args()

if not opt.firstRun:   
    parser.error('first run number not provided')

if not opt.lastRun:   
    parser.error('last run number not provided')

if not opt.inputDir:   
    parser.error('input directory not provided')

if not opt.outputDir:   
    parser.error('output directory not provided')

#------------------------------------------------

print opt.barInArray

nFilesInScan = int( ((int(opt.lastRun)-1) - (int(opt.firstRun)+1)) / 3. + 1)
print "nFilesInScan: ", nFilesInScan

mergedTree = str(opt.outputDir)+"/"+"tree_"+"FirstRun" + str(opt.firstRun.zfill(6)) + "_LastRun" + str(opt.lastRun.zfill(6)) + "_BAR" + str(opt.barCode.zfill(6))+".root"

commandMerge = "hadd -f "+mergedTree
print commandMerge

for step in range(0,nFilesInScan):

    #Launch analysis for each step of the scan
    print step
    currentRun = int(opt.firstRun) + 1 + step*3    
    
    if opt.barInArray==False:
        command = "python analysis/analyze_run_bar.py --run "+ str(currentRun) +" --barCode "+str(opt.barCode)+" -i "+str(opt.inputDir)+" -o "+str(opt.outputDir)
    if opt.barInArray==True:
       command = "python analysis/analyze_run_barInArray.py --run "+ str(currentRun) +" --barCode "+str(opt.barCode)+" -i "+str(opt.inputDir)+" -o "+str(opt.outputDir) 

    print command
    os.system(command)


    #Update command to merge trees
    commandMerge = commandMerge+" "+str(opt.outputDir)+"/"+"tree"+"_Run"+str(currentRun).zfill(6)+"_*"
    
print commandMerge
os.system(commandMerge)


