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

###############
## Pixel+Bar ##
###############
channels = [59,291,315]
###############

usage = "usage: python analysis/analyze_run_bar.py --run 2 -i /media/cmsdaq/ext/TOFPET/data/BarReproducibility__Temp24__03_07_2019 -o /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis"

parser = optparse.OptionParser(usage)

parser.add_option("-r", "--run", dest="run",
                  help="run number")

parser.add_option("-i", "--input", dest="inputDir",
                  help="input directory")

parser.add_option("-o", "--output", dest="outputDir",
                  help="output directory")

(opt, args) = parser.parse_args()

if not opt.run:   
    parser.error('run number not provided')

if not opt.inputDir:   
    parser.error('input directory not provided')

if not opt.outputDir:   
    parser.error('output directory not provided')

################################################

gROOT.SetBatch(True)

################################################
## 1) Find input files
################################################

run = opt.run.zfill(6)
#print run

input_filename_ped1 = ""
input_filename_ped2 = ""
input_filename_singles = ""
input_filename_coinc = ""

list_allfiles = os.listdir(opt.inputDir)
#print list_allfiles

for file in list_allfiles:

    if (str(int(run)-1).zfill(6) in file and "_singles.root" in file):
        input_filename_ped1 = opt.inputDir + "/" + file
        print input_filename_ped1

    if (str(int(run)+1).zfill(6) in file and "_singles.root" in file):
        input_filename_ped2 = opt.inputDir + "/" + file
        print input_filename_ped2

    if (run in file and "_singles.root" in file):
        input_filename_singles = opt.inputDir + "/" + file
        print input_filename_singles

    if (run in file and "_coincidences.root" in file):
        input_filename_coinc = opt.inputDir + "/" + file
        print input_filename_coinc
    
if (input_filename_ped1==""):
    parser.error('missing pedestal1 file')
if (input_filename_ped2==""):
    parser.error('missing pedestal2 file')
if (input_filename_singles==""):
    parser.error('missing singles file')
if (input_filename_coinc==""):
    parser.error('missing coincidence file')

################################################
## 2) Analyze pedestals
################################################

tfilePed1 = TFile.Open(input_filename_ped1)
treePed1 = tfilePed1.Get("data")
tfilePed2 = TFile.Open(input_filename_ped2)
treePed2 = tfilePed2.Get("data")

histos_Ped1 = {} 
mean_Ped1 = {} 
rms_Ped1 = {} 
histos_Ped2 = {} 
mean_Ped2 = {} 
rms_Ped2 = {} 
histos_PedTot = {} 
mean_PedTot = {} 
rms_PedTot = {} 

for ch in channels:

    histo1 = TH1F("h1_ped1_energy_ch"+str(ch), "", 500, 0, 500)
    histos_Ped1[ch]=histo1
    mean_Ped1[ch]=-9 
    rms_Ped1[ch]=-9 

    histo2 = TH1F("h1_ped2_energy_ch"+str(ch), "", 500, 0, 500)
    histos_Ped2[ch]=histo2
    mean_Ped2[ch]=-9 
    rms_Ped2[ch]=-9 

    histoTot = TH1F("h1_pedTot_energy_ch"+str(ch), "", 500, 0, 500)
    histos_PedTot[ch]=histoTot
    mean_PedTot[ch]=-9 
    rms_PedTot[ch]=-9 

tfilePed1.cd()
for event in range (0,treePed1.GetEntries()):
    treePed1.GetEntry(event)
    for ch in channels:
        if( treePed1.channelID==ch):
            histos_Ped1[ch].Fill(treePed1.energy)
            histos_PedTot[ch].Fill(treePed1.energy)

tfilePed2.cd()
for event in range (0,treePed2.GetEntries()):
    treePed2.GetEntry(event)
    for ch in channels:
        if( treePed2.channelID==ch):
            histos_Ped2[ch].Fill(treePed2.energy)
            histos_PedTot[ch].Fill(treePed2.energy)

for ch in channels:

    mean_Ped1[ch]=histos_Ped1[ch].GetMean()
    rms_Ped1[ch]=histos_Ped1[ch].GetRMS() 

    mean_Ped2[ch]=histos_Ped2[ch].GetMean()
    rms_Ped2[ch]=histos_Ped2[ch].GetRMS() 

    mean_PedTot[ch]=histos_PedTot[ch].GetMean()
    rms_PedTot[ch]=histos_PedTot[ch].GetRMS() 

################################################
## 3) Analyze singles
################################################

tfileSingles = TFile.Open(input_filename_singles)
treeSingles = tfileSingles.Get("data")
histos_Singles = {} 

for ch in channels:

    histo1 = TH1F("h1_singles_energy_ch"+str(ch), "", 200, 0, 200)
    histos_Singles[ch]=histo1

tfileSingles.cd()
for event in range (0,treeSingles.GetEntries()):
    treeSingles.GetEntry(event)
    for ch in channels:
        if( treeSingles.channelID==ch):
            histos_Singles[ch].Fill(treeSingles.energy-mean_PedTot[ch])

################################################
## X) Output file
################################################

tfileoutput = TFile( "output.root", 'recreate' )
tfileoutput.cd()

for ch in channels:
    #pedestals
    histos_Ped1[ch].Write()
    histos_Ped2[ch].Write()
    histos_PedTot[ch].Write()
    print "--- Channel = "+str(ch).zfill(3)+" ---"
    print "Pedestal1 "+str(mean_Ped1[ch])+" "+str(rms_Ped1[ch]) 
    print "Pedestal2 "+str(mean_Ped2[ch])+" "+str(rms_Ped2[ch]) 
    print "PedestalTot "+str(mean_PedTot[ch])+" "+str(rms_PedTot[ch]) 
    #singles
    histos_Singles[ch].Write()

tfileoutput.Close()

tfilePed1.cd()
tfilePed1.Close()
tfilePed2.cd()
tfilePed2.Close()
tfileSingles.cd()
tfileSingles.Close()
