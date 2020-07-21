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

nFilesInScan = 5

mergedTree = str(opt.outputDir)+"/"+"tree_"+"FirstRun" + str(opt.firstRun.zfill(6)) + "_LastRun" + str((int(opt.firstRun)+(nFilesInScan-1)*3)).zfill(6) + "_ARRAY" + str(opt.arrayCode.zfill(6))+".root"

commandMerge = "hadd -f "+mergedTree
print commandMerge

for step in range(0,nFilesInScan):

    #Launch analysis for each step of the position scan
    print step
    currentRun = int(opt.firstRun) + step*3    
    command = "python analysis/analyze_run_array.py --run "+ str(currentRun) +" --arrayCode "+str(opt.arrayCode)+" -i "+str(opt.inputDir)+" -o "+str(opt.outputDir)
    print command
    os.system(command)

    #Update command to merge trees
    commandMerge = commandMerge+" "+str(opt.outputDir)+"/"+"tree"+"_Run"+str(currentRun).zfill(6)+"_*"
    
print commandMerge
os.system(commandMerge)

#### Analysis Summary #####

tfileResults = TFile.Open(mergedTree)
treeResults = tfileResults.Get("results")

h1_spectra_bar = TH1F("h1_spectra_bar", "", 1000, 0, 100)
h1_CTR_bar = TH1F("h1_CTR_bar", "", 5000, 0, 500)
h1_ct_bar = TH1F("h1_ct_bar", "", 1000, 0, 10)

#n = 5
bar_id, ph_peak, ph_peak_err,  CTR_sigma, ct, CTR_sigma_err, ct_err, bar_err = array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' )

for event in range (0,treeResults.GetEntries()):
    treeResults.GetEntry(event)
    h1_spectra_bar.Fill(treeResults.peak1_mean_barCoinc)
    h1_CTR_bar.Fill(treeResults.CTR_sigma_barCoinc)
    #h1_ct_bar.Fill(treeResults.Xtalk_mean_barCoinc/treeResults.peak1_mean_barCoinc) # only for Casaccia
    h1_ct_bar.Fill(treeResults.Xtalk_average_barCoinc/treeResults.peak1_mean_barCoinc) # average introduced on 12/02/2020 
    bar_id.append(treeResults.bar)
    bar_err.append(0)
    CTR_sigma.append(treeResults.CTR_sigma_barCoinc)
    CTR_sigma_err.append(treeResults.err_CTR_sigma_barCoinc)
    ph_peak.append(treeResults.peak1_mean_barCoinc)
    ph_peak_err.append(treeResults.err_peak1_mean_barCoinc)
    #ct.append((treeResults.Xtalk_mean_barCoinc)/(treeResults.peak1_mean_barCoinc))
    ct.append((treeResults.Xtalk_average_barCoinc)/(treeResults.peak1_mean_barCoinc))
    #xtalk_err_value=treeResults.err_Xtalk_mean_barCoinc
    xtalk_err_value=0.
    peak_err_value=treeResults.err_peak1_mean_barCoinc
    #ct_err_value=sqrt((xtalk_err_value**2)/((treeResults.peak1_mean_barCoinc)**2)+(peak_err_value**2*((treeResults.Xtalk_mean_barCoinc)**2)/((treeResults.peak1_mean_barCoinc)**4)))    
    ct_err_value=sqrt((xtalk_err_value**2)/((treeResults.peak1_mean_barCoinc)**2)+(peak_err_value**2*((treeResults.Xtalk_average_barCoinc)**2)/((treeResults.peak1_mean_barCoinc)**4)))    
    ct_err.append(ct_err_value)

##########################################

mergedLabel = str(opt.outputDir)+"/"+"tree_"+"FirstRun" + str(opt.firstRun.zfill(6)) + "_LastRun" + str((int(opt.firstRun)+(nFilesInScan-1)*3)).zfill(6) + "_ARRAY" + str(opt.arrayCode.zfill(6))

#pt1 = TPaveText(0.100223,0.915556,0.613586,0.967407,"brNDC")
#text1 = pt1.AddText( str(opt.firstRun.zfill(6)) + "_LastRun" + str((int(opt.firstRun)+(nFilesI\nScan-1)*3)).zfill(6) + "_ARRAY" + str(opt.arrayCode.zfill(6))+"plot" )
#pt1.SetFillColor(0)
#pt1.Draw()
#c1_spectra.Update()

gr_phe_peak = TGraphErrors( nFilesInScan, bar_id, ph_peak, bar_err, ph_peak_err )
c1_spectra = TCanvas("phe_peak", "phe_peak", 900, 700)     

#edits Livia
mean1 = TPaveText(0.12, 0.12, 0.45, 0.2, "brNDC")
mean1.SetFillColor(kWhite)
mean1.SetBorderSize(0)
mean1.AddText(Form("mean = %.3f #pm %.3f"%(h1_spectra_bar.GetMean(),h1_spectra_bar.GetRMS())))

c1_spectra.cd()  
gStyle.SetOptStat(1111);
c1_spectra.SetGrid();
gr_phe_peak.GetXaxis().SetTitle("BAR ID")
gr_phe_peak.GetYaxis().SetTitle("Energy (QDC)")
gr_phe_peak.SetLineColor( 2 )
gr_phe_peak.SetMarkerColor( 1 )
gr_phe_peak.SetMarkerStyle( 21 )
gr_phe_peak.Draw()
mean1.Draw()
c1_spectra.SaveAs(mergedLabel+"_"+"SUMMARY_phePeak.png")

gr_CTR = TGraphErrors(nFilesInScan, bar_id, CTR_sigma, bar_err, CTR_sigma_err)
c2_CTR = TCanvas("CTR_sigma", "CTR_sigma", 900, 700)
mean2 = TPaveText(0.15, 0.75, 0.45, 0.89, "brNDC")
mean2.SetFillColor(kWhite)
mean2.SetBorderSize(0)
mean2.AddText(Form("mean = %.3f #pm %.3f"%(h1_CTR_bar.GetMean(),h1_CTR_bar.GetRMS())))

c2_CTR.cd()
gStyle.SetOptStat(1111);
c2_CTR.SetGrid();
gr_CTR.GetXaxis().SetTitle("BAR ID")
gr_CTR.GetYaxis().SetTitle("CTR_sigma(ps)")
gr_CTR.SetLineColor( 2 )
gr_CTR.SetMarkerColor( 1 )
gr_CTR.SetMarkerStyle( 21 )
gr_CTR.Draw()
mean2.Draw()
c2_CTR.SaveAs(mergedLabel+"_"+"SUMMARY_CTR.png")

gr_ct = TGraphErrors(nFilesInScan, bar_id, ct, bar_err, ct_err)
c3_ct = TCanvas("cross-talk", "cross-talk", 900, 700)
mean3 = TPaveText(0.6, 0.78, 0.9, 0.88, "brNDC")
mean3.SetFillColor(kWhite)
mean3.SetBorderSize(0)
mean3.AddText(Form("mean = %.3f #pm %.3f"%(h1_ct_bar.GetMean(),h1_ct_bar.GetRMS())))
c3_ct.cd()
gStyle.SetOptStat(1111);
c3_ct.SetGrid();
gr_ct.GetXaxis().SetTitle("BAR ID")
gr_ct.GetYaxis().SetTitle("ct fraction")
gr_ct.SetLineColor( 2 )
gr_ct.SetMarkerColor( 1 )
gr_ct.SetMarkerStyle( 21 )
gr_ct.Draw()
mean3.Draw()
c3_ct.SaveAs(mergedLabel+"_"+"SUMMARY_xtalk.png")

###################################################

ph_peak_mean = h1_spectra_bar.GetMean()
ph_peak_RMS = h1_spectra_bar.GetRMS()

CTR_sigma_mean = h1_CTR_bar.GetMean()
CTR_sigma_RMS = h1_CTR_bar.GetRMS()

ct_mean = h1_ct_bar.GetMean()
ct_RMS = h1_ct_bar.GetRMS()

#printing for ELOG
print "ARRAY" + str(opt.arrayCode.zfill(6))+" RUNS: ", 
for step in range(0,nFilesInScan):
    print int(opt.firstRun) + step*3, " - ", 
print " "
print "ph_peak_mean="+str("{:10.3f}".format(ph_peak_mean))
print "ph_peak_RMS="+str("{:10.3f}".format(ph_peak_RMS))
print "CTR_sigma_mean="+str("{:10.3f}".format(CTR_sigma_mean))+" ps"
print "CTR_sigma_RMS="+str("{:10.3f}".format(CTR_sigma_RMS))+" ps"
print "ct_mean="+str("{:10.3f}".format(ct_mean))
print "ct_RMS="+str("{:10.3f}".format(ct_RMS))

