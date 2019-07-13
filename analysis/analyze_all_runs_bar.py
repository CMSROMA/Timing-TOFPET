#! /usr/bin/env python

import os
import sys
import optparse
import datetime
import subprocess
import re
from glob import glob
from collections import defaultdict
from collections import OrderedDict
from array import array

from ROOT import *

usage = "usage: python analysis/analyze_all_runs_bar.py -i /data/TOFPET/LYSOBARS -o /data/TOFPET/LYSOBARS/RESULTS"

parser = optparse.OptionParser(usage)

parser.add_option("-i", "--input", dest="inputDir",default="/data/TOFPET/LYSOBARS",
                  help="input directory")

parser.add_option("-o", "--output", dest="outputDir",default="/data/TOFPET/LYSOBARS/RESULTS",
                  help="output directory")

(opt, args) = parser.parse_args()

if not opt.inputDir:   
    parser.error('input directory not provided')

if not opt.outputDir:   
    parser.error('output directory not provided')

commandOutputDir = "mkdir -p "+opt.outputDir
print commandOutputDir
os.system(commandOutputDir)

list_allfiles = os.listdir(opt.inputDir)
#print list_allfiles

for file in list_allfiles:

    if ("PHYS" in file and "_singles.root" in file):
        filename = (file.split("/")[-1]).split("_")
        run = re.sub(r'\b0+(\d)', r'\1', filename[0].split("Run")[1])
        code = re.sub(r'\b0+(\d)', r'\1', filename[2].split("BAR")[1])
        #print run, code
        
        commandRun = "python analysis/analyze_run_bar.py --run "+str(run)+" --barCode "+code+" -i "+opt.inputDir+" -o "+opt.outputDir
        print commandRun
        os.system(commandRun)
        
commandHadd = "hadd "+opt.outputDir+"/"+"tree_all.root "+opt.outputDir+"/tree*.root"
print commandHadd
os.system(commandHadd)
