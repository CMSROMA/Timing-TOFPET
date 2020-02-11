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

#--------------------------------------------------------

usage = "usage: python analysis/analyze_alignPixelRef.py -i /data/TOFPET/ALIGNPIXELREF -o /data/TOFPET/ALIGNPIXELREF"

parser = optparse.OptionParser(usage)

parser.add_option("-i", "--input", dest="inputDir",
                  help="input directory")

parser.add_option("-o", "--output", dest="outputDir",
                  help="output directory")

(opt, args) = parser.parse_args()

if not opt.inputDir:   
    parser.error('input directory not provided')

if not opt.outputDir:   
    parser.error('output directory not provided')

#--------------------------------------------------------

gROOT.SetBatch(True)

gStyle.SetOptTitle(0)
gStyle.SetOptStat("e")
gStyle.SetOptFit(1111111)
gStyle.SetStatH(0.09)

#--------------------------------------------------------

list_allfiles = os.listdir(opt.inputDir)
#print list_allfiles

histo = TH2F("histo","histo",510,-0.5,50.5,51,-0.5,50.5)
histoY = TH1F("histoY","histoY",510,-0.5,50.5)
histoX = TH1F("histoX","histoX",510,-0.5,50.5)

for file in list_allfiles:

    if ("_singles.root" in file):
        input_filename_singles = opt.inputDir + "/" + file
        print input_filename_singles

        X = float(input_filename_singles.split("/")[-1].split("_")[4].replace("X",""))
        Y = float(input_filename_singles.split("/")[-1].split("_")[5].replace("Y",""))
        POS = int(input_filename_singles.split("/")[-1].split("_")[3].replace("POS",""))
        print X, Y, POS    

        tfile = TFile.Open(input_filename_singles)
        tree = tfile.Get("data")
        #tree.Print()

        nhits = 0 
        for event in range (0,tree.GetEntries()):
            tree.GetEntry(event)
            #print tree.energy
                    
            if(tree.channelID==59 and tree.energy>-9):
                nhits = nhits + 1

        print nhits
        binx = histo.GetXaxis().FindBin(X)
        biny = histo.GetYaxis().FindBin(Y)
        histo.SetBinContent(binx,biny,nhits)

        #scan Y
        if (POS >= 0 and POS <= 14):
            histoY.SetBinContent(histoY.GetXaxis().FindBin(Y),nhits)
            histoY.SetBinError(histoY.GetXaxis().FindBin(Y),sqrt(nhits))

        #scan X
        if (POS >= 15 and POS <= 29):
            histoX.SetBinContent(histoX.GetXaxis().FindBin(X),nhits)
            histoX.SetBinError(histoX.GetXaxis().FindBin(X),sqrt(nhits))

#fit
fitx = histoX.Fit("pol2","S")
func_fitx = histoX.GetFunction("pol2")
fity = histoY.Fit("pol2","S")
func_fity = histoY.GetFunction("pol2")

#maximum
max_X = func_fitx.GetX(func_fitx.GetMaximum())
max_Y = func_fity.GetX(func_fity.GetMaximum())
print "================================="
print "==== maxX, maxY: " , max_X, max_Y
print "================================="

#style
histoX.GetXaxis().SetTitle("X [mm]")
histoX.GetYaxis().SetTitle("Number of hits")

histoY.GetXaxis().SetTitle("Y [mm]")
histoY.GetYaxis().SetTitle("Number of hits")

#plots
c1 = TCanvas("c1","",500,500)
histo.Draw("colz")
c2 = TCanvas("c2","",500,500)
histoY.Draw("pe")
c2.SetGridx()
c2.SetGridy()
c3 = TCanvas("c3","",500,500)
histoX.Draw("pe")
c3.SetGridx()
c3.SetGridy()

c1.SaveAs(opt.outputDir+"/"+"alignPixelRef_XY.png")
c2.SaveAs(opt.outputDir+"/"+"alignPixelRef_Y.png")
c3.SaveAs(opt.outputDir+"/"+"alignPixelRef_X.png")
