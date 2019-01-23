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

from ROOT import *

usage = "usage: run from Timing-TOFPET: python run_TOFPET.py -c config_main.txt"

parser = optparse.OptionParser(usage)

parser.add_option("-c", "--config", dest="configFile",
                  help="config file")

(opt, args) = parser.parse_args()

if not opt.configFile:   
    parser.error('config file not provided')

################################################

gROOT.SetBatch(True)

current_time = datetime.datetime.now()
simpletimeMarker = "%04d-%02d-%02d__%02d-%02d-%02d" % (current_time.year,current_time.month,current_time.day,current_time.hour,current_time.minute,current_time.second)

unixTimeStart = long(time.time())

###############################
### 0) Read config file
###############################
cfg = open(opt.configFile, "r")

config_template_file = ""
hv_dac = ""
run_calib = ""
calib_dir = ""
tdc_calib = ""
qdc_calib = ""
disc_calib = ""
sipm_bias = ""
disc_settings = ""
channel_map = ""
trigger_map = ""
lsb_t1 = ""
lsb_t2 = ""
daqscript = ""
convertsinglescript = ""
convertcoincidencescript = ""
#convertNcoincidencescript = ""
mode = ""
runtime = ""
output_dir = ""
output_label = ""
dic_channels = {}
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

    if (linetype == "CONFIG_INI_TEMPLATE" and linesize==2):
        config_template_file = splitline[1]

    if (linetype == "HV_DAC" and linesize==2):
        hv_dac = splitline[1]

    if (linetype == "RUN_CALIB" and linesize==2):
        run_calib = splitline[1]

    if (linetype == "CALIB_DIR" and linesize==2):
        calib_dir = splitline[1]

    if (linetype == "TDC_CALIB" and linesize==2):
        tdc_calib = splitline[1]

    if (linetype == "QDC_CALIB" and linesize==2):
        qdc_calib = splitline[1]

    if (linetype == "DISC_CALIB" and linesize==2):
        disc_calib = splitline[1]

    if (linetype == "SIPM_BIAS" and linesize==2):
        sipm_bias = splitline[1]

    if (linetype == "DISC_SETTINGS" and linesize==2):
        disc_settings = splitline[1]

    if (linetype == "CHANNEL_MAP" and linesize==2):
        channel_map = splitline[1]

    if (linetype == "TRIGGER_MAP" and linesize==2):
        trigger_map = splitline[1]

    if (linetype == "LSB_T1" and linesize==2):
        lsb_t1 = splitline[1]

    if (linetype == "LSB_T2" and linesize==2):
        lsb_t2 = splitline[1]

    if (linetype == "DAQSCRIPT" and linesize==2):
        daqscript = splitline[1]

    if (linetype == "CONVERTSINGLESCRIPT" and linesize==2):
        convertsinglescript = splitline[1]

    if (linetype == "CONVERTCOINCIDENCESCRIPT" and linesize==2):
        convertcoincidencescript = splitline[1]

    #if (linetype == "CONVERTNCOINCIDENCESCRIPT" and linesize==2):
    #    convertNcoincidencescript = splitline[1]

    if (linetype == "MODE" and linesize==2):
        mode = splitline[1]

    if (linetype == "TIME" and linesize==2):
        runtime = splitline[1]

    if (linetype == "OUTPUT_DIR" and linesize==2):
        output_dir = splitline[1]

    if (linetype == "OUTPUT_LABEL" and linesize==2):
        output_label = splitline[1]

    #print linetype, linesize

    if (linetype == "CH" and linesize==16):
        #read channel settings
        chId = splitline[1]
        channels.append(chId)        

        NHV = splitline[2]
        VBR = splitline[3]
        OV = splitline[4]
        NCHIP = splitline[5]
        NCH = splitline[6]
        VTH_1 = splitline[7]
        VTH_2 = splitline[8]
        VTH_E = splitline[9]
        SIPM_CODE = splitline[10]
        SIPM_TYPE = splitline[11]
        X = splitline[12]
        Y = splitline[13]
        Z = splitline[14]
        CRYSTAL = splitline[15]
        #write channel settings in dictionary
        dic_channels[(chId,"NHV")]=NHV
        dic_channels[(chId,"VBR")]=VBR
        dic_channels[(chId,"OV")]=OV
        dic_channels[(chId,"NCHIP")]=NCHIP
        dic_channels[(chId,"NCH")]=NCH
        dic_channels[(chId,"VTH_1")]=VTH_1
        dic_channels[(chId,"VTH_2")]=VTH_2
        dic_channels[(chId,"VTH_E")]=VTH_E
        dic_channels[(chId,"SIPM_CODE")]=SIPM_CODE
        dic_channels[(chId,"SIPM_TYPE")]=SIPM_TYPE
        dic_channels[(chId,"X")]=X
        dic_channels[(chId,"Y")]=Y
        dic_channels[(chId,"Z")]=Z
        dic_channels[(chId,"CRYSTAL")]=CRYSTAL

#print config_template_file, hv_dac, run_calib, calib_dir, tdc_calib, qdc_calib, disc_calib, sipm_bias, disc_settings, channel_map, trigger_map, lsb_t1, lsb_t2, daqscript, convertsinglescript, convertcoincidencescript, mode, runtime,  output_dir, output_label
#print dic_channels[("0","VBR")]
print "Active channels: ", channels

###############################
### 1) Check calibration status
###############################
tdc_calib_path = calib_dir+"/"+tdc_calib
qdc_calib_path = calib_dir+"/"+qdc_calib
disc_calib_path = calib_dir+"/"+disc_calib

tdc_calib_exists = os.path.isfile(tdc_calib_path)
qdc_calib_exists = os.path.isfile(qdc_calib_path)
disc_calib_exists = os.path.isfile(disc_calib_path)

if run_calib=="1" and (tdc_calib_exists or qdc_calib_exists or disc_calib_exists):
    print "WARNING: Not possible to run calibration since at least one calibration file already exists"
    print "Exit..."
    sys.exit()

if run_calib=="0" and ( not (tdc_calib_exists and qdc_calib_exists and disc_calib_exists) ):
    print "WARNING: Not possible to run daq since at least one calibration file is missing"
    print "Exit..."
    sys.exit()

###############################
### 2) Create new sipm bias table
###############################
sipm_bias_table_template = sipm_bias
sipm_bias_table_current = "data/sipm_bias_current.tsv"
sipmbiasTemplate = open(sipm_bias_table_template, "r")
sipmbiasCurrent = open(sipm_bias_table_current, "w")
for line in sipmbiasTemplate:

    #skip commented out lines or empty lines
    if (line.startswith("#")):
        sipmbiasCurrent.write(line)
        continue
    if line in ['\n','\r\n']:
        sipmbiasCurrent.write(line)
        continue

    line = line.rstrip('\n')
    splitline = line.split()
    #print line

    HVfound = 0
    for ch in channels:
        if(splitline[2]==dic_channels[(ch,"NHV")] and len(splitline)==6 and HVfound==0):
            HVfound=1
            sipmbiasCurrent.write("0\t0\t"+
                                  dic_channels[(ch,"NHV")]+"\t"+
                                  str(float(dic_channels[(ch,"VBR")])-5)+"\t"+
                                  dic_channels[(ch,"VBR")]+"\t"+
                                  dic_channels[(ch,"OV")]+"\n"
                              )

    if HVfound==0:
        sipmbiasCurrent.write(line+'\n')
    
sipmbiasCurrent.close()
sipmbiasTemplate.close()

###############################
### 3) Create new discriminator threshold table
###############################
disc_settings_table_template = disc_settings
disc_settings_table_current = "data/disc_settings_current.tsv"
discSetTemplate = open(disc_settings_table_template, "r")
discSetCurrent = open(disc_settings_table_current, "w")
for line in discSetTemplate:

    #skip commented out lines or empty lines
    if (line.startswith("#")):
        discSetCurrent.write(line)
        continue
    if line in ['\n','\r\n']:
        discSetCurrent.write(line)
        continue

    line = line.rstrip('\n')
    splitline = line.split()
    #print line

    CHfound = 0
    for ch in channels:
        if(splitline[2]==dic_channels[(ch,"NCHIP")] 
           and splitline[3]==dic_channels[(ch,"NCH")] 
           and len(splitline)==7):
            CHfound=1
            discSetCurrent.write("0\t0\t"+
                                  dic_channels[(ch,"NCHIP")]+"\t"+
                                  dic_channels[(ch,"NCH")]+"\t"+
                                  dic_channels[(ch,"VTH_1")]+"\t"+
                                  dic_channels[(ch,"VTH_2")]+"\t"+
                                  dic_channels[(ch,"VTH_E")]+"\n"
                              )

    if CHfound==0:
        discSetCurrent.write(line+'\n')
    
discSetCurrent.close()
discSetTemplate.close()

###############################
### 4) Create new configuration file
###############################
config_template = config_template_file
config_current = "config_current.ini"
configFileTemplate = open(config_template, "r")
configFileCurrent = open(config_current, "w")
for line in configFileTemplate:

    #skip commented out lines or empty lines
    if (line.startswith("#")):
        configFileCurrent.write(line)
        continue
    if line in ['\n','\r\n']:
        configFileCurrent.write(line)
        continue

    line = line.rstrip('\n')

    if "HV_DAC" in line:
        line = line.replace("HV_DAC",hv_dac)
    if "TDC_CALIB" in line:
        line = line.replace("TDC_CALIB",tdc_calib_path)
    if "QDC_CALIB" in line:
        line = line.replace("QDC_CALIB",qdc_calib_path)
    if "DISC_CALIB" in line:
        line = line.replace("DISC_CALIB",disc_calib_path)
    if "SIPM_BIAS" in line:
        line = line.replace("SIPM_BIAS",sipm_bias_table_current)
    if "DISC_SETTINGS" in line:
        line = line.replace("DISC_SETTINGS",disc_settings_table_current)
    if "CHANNEL_MAP" in line:
        line = line.replace("CHANNEL_MAP",channel_map)
    if "TRIGGER_MAP" in line:
        line = line.replace("TRIGGER_MAP",trigger_map)
    if "LSB_T1" in line:
        line = line.replace("LSB_T1",lsb_t1)
    if "LSB_T2" in line:
        line = line.replace("LSB_T2",lsb_t2)

    configFileCurrent.write(line+"\n")
 
configFileCurrent.close()
configFileTemplate.close()

###############################
### 5) Run calibration
###############################
#calibration scripts
disc_calib_script = "acquire_threshold_calibration"
disc_calib_process_script = "process_threshold_calibration"
tdc_calib_script = "acquire_tdc_calibration"
tdc_calib_process_script = "process_tdc_calibration"
qdc_calib_script = "acquire_qdc_calibration"
qdc_calib_process_script = "process_qdc_calibration"

if run_calib=="1":
    
    commandOutputCalibDir = "mkdir -p "+calib_dir
    print commandOutputCalibDir
    os.system(commandOutputCalibDir)

    print "Starting discriminator calibration..."
    commandDiscCalib = "./"+disc_calib_script+" --config "+config_current+" -o "+calib_dir+"/"+"disc_calibration"
    commandDiscCalibProcess = "./"+disc_calib_process_script+" --config "+config_current+" -i "+calib_dir+"/"+"disc_calibration"+" -o "+disc_calib_path+" --root-file "+disc_calib_path.split(".tsv")[0]+".root"
    print commandDiscCalib    
    os.system(commandDiscCalib)
    print commandDiscCalibProcess    
    os.system(commandDiscCalibProcess)
    print "End discriminator calibration"
    print "\n"

    print "Starting TDC and QDC calibration..."
    commandTdcCalib = "./"+tdc_calib_script+" --config "+config_current+" -o "+calib_dir+"/"+"tdc_calibration"
    commandTdcCalibProcess = "./"+tdc_calib_process_script+" --config "+config_current+" -i "+calib_dir+"/"+"tdc_calibration"+" -o "+tdc_calib_path.split(".tsv")[0]
    commandQdcCalib = "./"+qdc_calib_script+" --config "+config_current+" -o "+calib_dir+"/"+"qdc_calibration"
    commandQdcCalibProcess = "./"+qdc_calib_process_script+" --config "+config_current+" -i "+calib_dir+"/"+"qdc_calibration"+" -o "+qdc_calib_path.split(".tsv")[0]
    print commandTdcCalib    
    os.system(commandTdcCalib)
    print commandQdcCalib    
    os.system(commandQdcCalib)
    print commandTdcCalibProcess    
    os.system(commandTdcCalibProcess)
    print commandQdcCalibProcess    
    os.system(commandQdcCalibProcess)
    print "End TDC and QDC calibration"
    print "\n"

    commandCpConfigForCalib = "cp "+opt.configFile+" "+calib_dir+"/"+"config_for_calibration.txt"
    print commandCpConfigForCalib
    os.system(commandCpConfigForCalib)

###############################
### 6) Run daq
###############################
commandOutputDir = "mkdir -p "+output_dir
print commandOutputDir
os.system(commandOutputDir)

outputFileLabel = output_label+"_"+mode+"_"+runtime
newname = output_dir+"/"+outputFileLabel
newconfigname = newname+".ini"

commandCpConfig = "cp "+opt.configFile+" "+newconfigname
print commandCpConfig
os.system(commandCpConfig)

print "Starting run..."
commandRun = "./"+daqscript+" --config "+ config_current +" --mode "+ mode +" --time "+ runtime +" -o "+newname
print commandRun
os.system(commandRun)
print "End run"
print "\n"

###############################
### 7) Convert output to ROOT trees
###############################
print "Creating root file with tree (singles)..."
commandConvertSingles = "./"+convertsinglescript+" --config "+ config_current +" -i "+newname+" -o "+newname+"_singles.root"+" --writeRoot"
print commandConvertSingles
os.system(commandConvertSingles)
print "File created."
print "\n"

## Add branches to root tree (singles)
print "Update root file with tree (singles)..."
inputfilename = newname+"_singles.root"
tfileinput = TFile.Open(inputfilename,"update")
treeInput = tfileinput.Get("data")
unixTime = array( 'l' , [0])
unixTimeBranch = treeInput.Branch( 'unixTime', unixTime, 'unixTime/L' )
for event in treeInput:
    unixTime[0] = long(event.time * 10**-12) + unixTimeStart #unix time in seconds of the current event
    unixTimeBranch.Fill()
treeInput.Write("",TFile.kOverwrite)
tfileinput.Close()
print "File updated."
print "\n"

#print "Creating root file with tree (coincidences)..."
#commandConvertCoincidences = "./"+convertcoincidencescript+" --config "+ config_current +" -i "+newname+" -o "+newname+"_coincidences.root"+" --writeRoot"
#print commandConvertCoincidences
#os.system(commandConvertCoincidences)
#print "File created."
#print "\n"

print "Creating root file with tree (N-coincidences) from singles..."
commandConvertCoincidences = "python "+convertcoincidencescript+" -c "+ opt.configFile +" -i "+ newname+"_singles.root" +" -n "+str(len(channels))+" -o "+newname+"_coincidences.root"
print commandConvertCoincidences
os.system(commandConvertCoincidences)
print "File created."
print "\n"
