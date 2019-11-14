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

from ROOT import *

usage = "usage: run from Timing-TOFPET: process_runs.py -r 1,2,3,4,5 [or 1-5] -d myfolder"

parser = optparse.OptionParser(usage)

parser.add_option("-r", "--runs", dest="runs",
                  help="list of run numbers to be analyzed: 1,2,3,4,5,6 or 1-6")

parser.add_option("-d", "--directory", dest="directory",
                  help="input/output directory")

(opt, args) = parser.parse_args()

if not opt.runs:   
    parser.error('Run list not provided')

if not opt.directory:   
    parser.error('Input/Output directory not provided')

################################################

gROOT.SetBatch(True)

################################################

run_list = []
if ("," in opt.runs) and ("-" not in opt.runs):
    run_list = opt.runs.split(",")
    print "Runs to be processed ", run_list, " in directory ", opt.directory
if ("-" in opt.runs) and ("," not in opt.runs):
    run_list_tmp = opt.runs.split("-")
    for ii in range( int(run_list_tmp[0]) , int(run_list_tmp[1])+1 ) :
        run_list.append(str(ii))
    print "Runs to be processed ", run_list, " in directory ", opt.directory 

if len(run_list) == 0:
    parser.error('No good run list provided')

list_allfiles = os.listdir(opt.directory)

for irun in run_list:

    run = "Run"+irun.zfill(6)
    print "Processing ", run, " ....."

    input_filename_rawf = ""
    input_filename_ini = ""
    input_filename_txt = ""
    input_filename_temp = ""

    list_allfiles = os.listdir(opt.directory)
    #print list_allfiles                                                                                                                                                                  
    for thisfile in list_allfiles:
        
        if (run in thisfile and ".rawf" in thisfile):
            input_filename_rawf = opt.directory + "/" + thisfile
            print input_filename_rawf
        if (run in thisfile and ".ini" in thisfile):
            input_filename_ini = opt.directory + "/" + thisfile
            print input_filename_ini
        if (run in thisfile and ".txt" in thisfile):
            input_filename_txt = opt.directory + "/" + thisfile
            print input_filename_txt
        if (run in thisfile and ".temp" in thisfile):
            input_filename_temp = opt.directory + "/" + thisfile
            print input_filename_temp

    if (input_filename_rawf==""):
        parser.error('missing rawf file for '+run)
    if (input_filename_ini==""):
        parser.error('missing ini file for '+run)
    if (input_filename_txt==""):
        parser.error('missing txt file for '+run)
    if (input_filename_temp==""):
        parser.error('missing temp file for '+run)

    fileNameNoExtension = input_filename_rawf.split(".rawf")[0]
    #print fileNameNoExtension

    startTime = input_filename_rawf.split("/")[-1].split("_")[1]
    #print startTime
    year = startTime.split("-")[0]
    month = startTime.split("-")[1]
    day = startTime.split("-")[2]
    hours = startTime.split("-")[3]
    minutes = startTime.split("-")[4]
    seconds = startTime.split("-")[5]
    #print startTime, year, month, day, hours, minutes, seconds
    unixTimeStart = long(time.mktime(datetime.datetime.strptime(startTime, "%Y-%m-%d-%H-%M-%S").timetuple())) + 3
    #+3 to account for the 3-seconds "sleep" in run_TOF.py
    #print unixTimeStart

    ###############################
    ### 1) Read configuration file
    ###############################
    cfg = open(input_filename_txt, "r")
    convertsinglescript = ""
    convertcoincidencescript = ""    

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

        if (linetype == "CONVERTSINGLESCRIPT" and linesize==2):
            convertsinglescript = splitline[1]

        if (linetype == "CONVERTCOINCIDENCESCRIPT" and linesize==2):
            convertcoincidencescript = splitline[1]

    ###############################
    ### 2) Create file with singles
    ###############################
    print "Creating root file with tree (singles)..."
    commandConvertSingles = "./"+convertsinglescript+" --config "+ input_filename_ini +" -i "+fileNameNoExtension+" -o "+fileNameNoExtension+"_singles.root"+" --writeRoot"
    print commandConvertSingles
    os.system(commandConvertSingles)
    print "File created."
    print "\n"

    ## Add branches to root tree (singles)
    print "Update root file with tree (singles)..."
    inputfilename = fileNameNoExtension+"_singles.root"
    tfileinput = TFile.Open(inputfilename,"update")
    treeInput = tfileinput.Get("data")
    unixTime = array( 'l' , [0])
    tempInt = array( 'd' , [-999.])
    tempExt = array( 'd' , [-999.])
    tempBoardTest = array( 'd' , [-999.])
    tempBoardRef = array( 'd' , [-999.])
    tempSiPMTest = array( 'd' , [-999.])
    tempSiPMRef = array( 'd' , [-999.])

    unixTimeBranch = treeInput.Branch( 'unixTime', unixTime, 'unixTime/L' )
    tempIntBranch = treeInput.Branch( 'tempInt', tempInt, 'tempInt/D' )
    tempExtBranch = treeInput.Branch( 'tempExt', tempExt, 'tempExt/D' )
    tempBoardTestBranch = treeInput.Branch( 'tempBoardTest', tempBoardTest, 'tempBoardTest/D' )
    tempBoardRefBranch = treeInput.Branch( 'tempBoardRef', tempBoardRef, 'tempBoardRef/D' )
    tempSiPMTestBranch = treeInput.Branch( 'tempSiPMTest', tempSiPMTest, 'tempSiPMTest/D' )
    tempSiPMRefBranch = treeInput.Branch( 'tempSiPMRef', tempSiPMRef, 'tempSiPMRef/D' )

    ReadNewTemperature = 0 
    TInt = -999. 
    TExt = -999.
    TBoardTest = -999. 
    TBoardRef = -999. 
    TSiPMTest = -999.
    TSiPMRef = -999.

    previousTime = 0
    for event in treeInput:
        unixTime[0] = long(event.time * 10**-12) + unixTimeStart #unix time in seconds of the current event

        ## Read temperatures from file every fixed DeltaT (10^12 ps = 1 s by default)
        if previousTime==0:
            ReadNewTemperature=1 
            previousTime = event.time
        elif (event.time - previousTime) <= 10**12:
            tempInt[0] = TInt
            tempExt[0] = TExt
            tempBoardTest[0] = TBoardTest
            tempBoardRef[0] = TBoardRef
            tempSiPMTest[0] = TSiPMTest
            tempSiPMRef[0] = TSiPMRef
        elif (event.time - previousTime) > 10**12:
            ReadNewTemperature=1
            previousTime = event.time

        if ReadNewTemperature==1:
            tempFile = open(input_filename_temp, "r")    
            for line in tempFile:
                #skip commented out lines or empty lines
                if (line.startswith("#")):
                    continue
                if line in ['\n','\r\n']:
                    continue
        
                line = line.rstrip('\n')
                splitline = line.split()

                linesize = len(splitline)
                if (linesize==7):
                    # find match within 2 seconds
                    if( abs(long(unixTime[0])-long(splitline[0])) < 2):
                        #calibration for temperature sensors is included
                        TInt = float(splitline[2])+0.16
                        TExt = float(splitline[3])-0.03
                        TBoardTest = float(splitline[4])-0.88
                        TBoardRef = float(splitline[1])-0.75
                        TSiPMTest = float(splitline[6])+0.09
                        TSiPMRef = float(splitline[5])+0.22
                        tempInt[0] = TInt
                        tempExt[0] = TExt
                        tempBoardTest[0] = TBoardTest
                        tempBoardRef[0] = TBoardRef
                        tempSiPMTest[0] = TSiPMTest
                        tempSiPMRef[0] = TSiPMRef
                        break
            ReadNewTemperature=0
            tempFile.close()
        
        unixTimeBranch.Fill()
        tempIntBranch.Fill()
        tempExtBranch.Fill()
        tempBoardTestBranch.Fill()
        tempBoardRefBranch.Fill()
        tempSiPMTestBranch.Fill()
        tempSiPMRefBranch.Fill()

    treeInput.Write("",TFile.kOverwrite)
    tfileinput.Close()
    print "File updated."
    print "\n"

    ####################################
    ### 3) Create file with coincidences
    ####################################

    print "Creating root file with tree (N-coincidences) from singles..."
    commandConvertCoincidences = "python "+convertcoincidencescript+" -c "+ input_filename_txt +" -i "+ fileNameNoExtension+"_singles.root" +" -o "+fileNameNoExtension+"_coincidences.root"
    print commandConvertCoincidences
    os.system(commandConvertCoincidences)
    print "File created."
    print "\n"

