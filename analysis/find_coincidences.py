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

usage = "usage: run from Timing-TOFPET: python analysis/find_coincidences.py -i xxx_singles.root -o xxx_coincidences.root -n 3"

parser = optparse.OptionParser(usage)

parser.add_option("-i", "--input", dest="inputRootFile",
                  help="input root file with singles")

parser.add_option("-o", "--output", dest="outputRootFile",
                  help="output root file with coincidences")

parser.add_option("-n", "--nch", dest="nch",
                  help="number of active channels")

(opt, args) = parser.parse_args()

if not opt.inputRootFile:   
    parser.error('input root file not provided')

if not opt.outputRootFile:   
    parser.error('output root file not provided')

if not opt.nch:   
    parser.error('number of active channels not provided')

################################################

gROOT.SetBatch(True)

tfileinput = TFile.Open(opt.inputRootFile)
treeInput = tfileinput.Get("data")
nEntries = treeInput.GetEntries()

tfileoutput = TFile( opt.outputRootFile, 'recreate' )
treeOutput = TTree( 'data', 'tree with coincidences' )

maxn = int(opt.nch)
n_channels = array( 'i', [ -9 ] )
n_coincidences = array( 'i', [ -9 ] )
a_chId = array( 'd', maxn*[ -9. ] )
a_energy = array( 'd', maxn*[ -9. ] )
a_time = array( 'd', maxn*[ -9. ] )

treeOutput.Branch( 'nch', n_channels, 'nch/I' )
treeOutput.Branch( 'ncoinc', n_coincidences, 'ncoinc/I' )
treeOutput.Branch( 'chId', a_chId, 'chId[nch]/D' )
treeOutput.Branch( 'energy', a_energy, 'energy[nch]/D' )
treeOutput.Branch( 'time', a_time, 'time[nch]/D' )

i_singles=0
while i_singles<nEntries:

    if i_singles == nEntries-1:
        break

    #if i_singles>200:
    #    break

    #print "===> i_singles= ", i_singles
    treeInput.GetEntry(i_singles)

    n_channels[0] = int(opt.nch)

    #ref channel
    t_ref = treeInput.time
    a_chId[0] = treeInput.channelID
    a_energy[0] = treeInput.energy
    a_time[0] = treeInput.time

    n_coinc=0
    nch_check_coinc = (int(opt.nch)-1)

    for k in range(i_singles+1, i_singles+1+nch_check_coinc):

        #print "k= ", k
        treeInput.GetEntry(k)

        #time coincidence
        time_coinc = 0
        t_current = treeInput.time
        t_diff = t_current - t_ref
        if abs(t_diff) < 20000: #ps -> 20ns
            time_coinc = 1

        if not time_coinc: #no time coincidence found
            #print "no coincidence found between ref "+str(i_singles)+" and current "+str(k)
            i_singles = k
            break
        else: #time coincidence found
            channelIdx = k - i_singles
            a_chId[channelIdx] = treeInput.channelID
            a_energy[channelIdx] = treeInput.energy
            a_time[channelIdx] = treeInput.time
            n_coinc=n_coinc+1 
            #print "===> i_singles= ", i_singles
            #print "k= ", k
            #print "t_current="+str(t_current)+" t_ref="+str(t_ref)+" t_diff="+str(t_diff)
            #print "coincidence found between "+str(i_singles)+" and "+str(k)
            #print a_time[channelIdx]

            if k==i_singles+1+nch_check_coinc-1:
                i_singles = k+1
                #print "End"
                break
            else:
                continue

    #print n_coinc
    n_coincidences[0] = int(n_coinc)

    if n_coinc>0:
        treeOutput.Fill()

tfileoutput.cd()
tfileoutput.Write()
tfileoutput.Close()

tfileinput.cd()
tfileinput.Close()
