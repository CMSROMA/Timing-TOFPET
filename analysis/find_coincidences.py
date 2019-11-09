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

usage = "usage: run from Timing-TOFPET: python analysis/find_coincidences.py -c config_main.txt -i xxx_singles.root -o xxx_coincidences.root -n 3"

parser = optparse.OptionParser(usage)

parser.add_option("-c", "--config", dest="configFile",
                  help="config file")

parser.add_option("-i", "--input", dest="inputRootFile",
                  help="input root file with singles")

parser.add_option("-o", "--output", dest="outputRootFile",
                  help="output root file with coincidences")

parser.add_option("-n", "--nch", dest="nch",
                  help="number of active channels")

parser.add_option("-p", "--prescale", dest="prescale",
                  default=1,
                  help="prescale of singles")

(opt, args) = parser.parse_args()

if not opt.configFile:   
    parser.error('config file not provided')
#
if not opt.inputRootFile:   
   parser.error('input root file not provided')

if not opt.outputRootFile:   
    parser.error('output root file not provided')
#
#if not opt.nch:   
#    parser.error('number of active channels not provided')

################################################

gROOT.SetBatch(True)
gROOT.ProcessLine(".L /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis/findCoincidences.C+")

gROOT.ProcessLine('TFile* f = new TFile("%s");'%opt.inputRootFile)
gROOT.ProcessLine('TTree* tree; f->GetObject("data",tree);')
gROOT.ProcessLine("findCoincidences analysis(tree)")
#gROOT.ProcessLine('analysis.Init(tree)')
gROOT.ProcessLine('analysis.configFile="%s"'%opt.configFile)
gROOT.ProcessLine('analysis.outputFile="%s"'%opt.outputRootFile)
gBenchmark.Start( 'findCoincidences' )
gROOT.ProcessLine("analysis.Loop()")
gBenchmark.Show( 'findCoincidences' )

