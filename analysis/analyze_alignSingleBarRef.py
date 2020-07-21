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

usage = "usage: python analysis/analyze_alignSingleBarRef.py -i /media/cmsdaq/ext/data/ALIGNMENT/ALIGNBARREF_21_07_2020 -o /media/cmsdaq/ext/data/ALIGNMENT/ALIGNBARREF_21_07_2020"

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

histoY = TH1F("histoY","histoY",510,-0.5,50.5)
histoX = TH1F("histoX","histoX",510,-0.5,50.5)

for file in list_allfiles:

    if ("_coincidences.root" in file):
        input_filename_coinc = opt.inputDir + "/" + file
        print input_filename_coinc

        X = float(input_filename_coinc.split("/")[-1].split("_")[4].replace("X",""))
        Y = float(input_filename_coinc.split("/")[-1].split("_")[5].replace("Y",""))
        POS = int(input_filename_coinc.split("/")[-1].split("_")[3].replace("POS",""))
        print X, Y, POS    

        tfile = TFile.Open(input_filename_coinc)
        tree = tfile.Get("data")
        #tree.Print()

        nhits_bar = 0 
        #nhits_coinc = 0 
        for event in range (0,tree.GetEntries()):
            tree.GetEntry(event)
                    
            if(tree.energy[0]>-9 and tree.energy[33]>-9):
                nhits_bar = nhits_bar + 1

            #if(tree.energy[0]>-9 and tree.energy[1]>-9 and tree.energy[2]>-9):
            #     nhits_coinc = nhits_coinc + 1

        print nhits_bar
        #, nhits_coinc

        #scan X
        if (POS >= 17 and POS <= 33):
            histoX.SetBinContent(histoX.GetXaxis().FindBin(X),nhits_bar)
            histoX.SetBinError(histoX.GetXaxis().FindBin(X),sqrt(nhits_bar))

        #scan Y
        if (POS >= 0 and POS <= 16):
            histoY.SetBinContent(histoY.GetXaxis().FindBin(Y),nhits_bar)
            histoY.SetBinError(histoY.GetXaxis().FindBin(Y),sqrt(nhits_bar))

#fit
binxmax = histoY.GetBinCenter(histoY.GetMaximumBin()) 
print "binxmax: ", binxmax

#func_fity = TF1("func_fity","gaus",binxmax-3,binxmax+3)
#fity = histoY.Fit("func_fity","SR")
fity = histoY.Fit("pol2","S")
func_fity = histoY.GetFunction("pol2")

fitx = histoX.Fit("pol2","S")
func_fitx = histoX.GetFunction("pol2")

#maximum
max_X = func_fitx.GetX(func_fitx.GetMaximum())
max_Y = func_fity.GetX(func_fity.GetMaximum())
print "================================="
print "==== maxX, maxY: " , max_X, max_Y
print "================================="

#style
histoX.GetXaxis().SetTitle("X [mm]")
histoX.GetYaxis().SetTitle("Number of bar hits")
histoX.SetMarkerStyle(20)
histoX.SetMarkerSize(0.7)

histoY.GetXaxis().SetTitle("Y [mm]")
histoY.GetYaxis().SetTitle("Number of bar hits")
histoY.SetMarkerStyle(20)
histoY.SetMarkerSize(0.7)

text1=TLatex()
text1.SetTextSize(0.04)

#plots
c1 = TCanvas("c2","",500,500)
histoY.Draw("pe")
histoY.GetYaxis().SetLimits(histoY.GetMinimum()*0.8,histoY.GetMaximum()*1.2)
histoY.GetYaxis().SetRangeUser(histoY.GetMinimum()*0.8,histoY.GetMaximum()*1.2)
c1.SetGridx()
c1.SetGridy()
text1.DrawLatexNDC(0.11,0.93,"Y_{max} = %.1f mm" % max_Y)

c2 = TCanvas("c3","",500,500)
histoX.Draw("pe")
histoX.GetYaxis().SetLimits(histoX.GetMinimum()*0.8,histoX.GetMaximum()*1.2)
histoX.GetYaxis().SetRangeUser(histoX.GetMinimum()*0.8,histoX.GetMaximum()*1.2)
c2.SetGridx()
c2.SetGridy()
text1.DrawLatexNDC(0.11,0.93,"X_{max} = %.1f mm" % max_X)

c1.SaveAs(opt.outputDir+"/"+"alignArray_Y.png")
c1.SaveAs(opt.outputDir+"/"+"alignArray_Y.root")
c2.SaveAs(opt.outputDir+"/"+"alignArray_X.png")
c2.SaveAs(opt.outputDir+"/"+"alignArray_X.root")
