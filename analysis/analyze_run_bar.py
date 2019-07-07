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

def totalFunction(x,par):
    
    t = (x[0]-par[4])/par[5]
    if par[17]<0: 
        t = -t

    absAlpha = abs(par[17])
    if( t >= - absAlpha ):
        crystalball = par[3]*TMath.Exp(-0.5*t*t)
    else:
        a = TMath.Power(par[18]/absAlpha,par[18])*TMath.Exp(-0.5*absAlpha*absAlpha)
        b = par[18]/absAlpha - absAlpha
        crystalball = par[3]*(a/TMath.Power(b-t,par[18]))

    return par[0]*(1./(1+TMath.Exp(par[1]*(x[0]-par[2])))+crystalball+( 1 + TMath.Erf((x[0]-par[12])/(par[13]*TMath.Sqrt(x[0]))) )*( par[6]/(1+TMath.Exp(par[7]*(x[0]-par[8]))) + par[14]*TMath.Gaus(x[0],par[15],par[16]) )+par[9]*TMath.Gaus(x[0],par[10],par[11]))


def f_1274keV_compton(x,par):
    return par[0]*(1./(1+TMath.Exp(par[1]*(x[0]-par[2]))))

def f_1274keV_peak(x,par):
    t = (x[0]-par[1])/par[2]
    if par[3]<0: 
        t = -t

    absAlpha = abs(par[3])
    if( t >= - absAlpha ):
        crystalball = par[0]*TMath.Exp(-0.5*t*t)
    else:
        a = TMath.Power(par[4]/absAlpha,par[4])*TMath.Exp(-0.5*absAlpha*absAlpha)
        b = par[4]/absAlpha - absAlpha
        crystalball = par[0]*(a/TMath.Power(b-t,par[4]))

    return crystalball

def f_511keV_compton_times_turnon(x,par):
    return ( 1 + TMath.Erf((x[0]-par[3])/(par[4]*TMath.Sqrt(x[0]))) ) * par[0]/(1+TMath.Exp(par[1]*(x[0]-par[2])))

def f_backscatter_peak_times_turnon(x,par):
    return ( 1 + TMath.Erf((x[0]-par[3])/(par[4]*TMath.Sqrt(x[0]))) ) * par[0]*TMath.Gaus(x[0],par[1],par[2])

def f_511keV_peak(x,par):
    return par[0]*TMath.Gaus(x[0],par[1],par[2])

def f_background(x,par):
    return par[0]*(1./(1+TMath.Exp(par[1]*(x[0]-par[2])))) + ( 1 + TMath.Erf((x[0]-par[6])/(par[7]*TMath.Sqrt(x[0]))) ) * par[3]/(1+TMath.Exp(par[4]*(x[0]-par[5])))
    

###############
## Pixel+Bar ##
###############
channels = [59,315,291]
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

gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)
gStyle.SetOptFit(1111111)
gStyle.SetStatH(0.09)

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
canvas_Singles = {} 

for ch in channels:

    histo1 = TH1F("h1_singles_energy_ch"+str(ch), "", 200, 0, 200)
    histos_Singles[ch]=histo1

    canvas1=TCanvas("c_singles_energy_ch"+str(ch),"",900,700)
    canvas_Singles[ch]=canvas1

tfileSingles.cd()
for event in range (0,treeSingles.GetEntries()):
    treeSingles.GetEntry(event)
    for ch in channels:
        if( treeSingles.channelID==ch):
            histos_Singles[ch].Fill(treeSingles.energy-mean_PedTot[ch])

################################################
## 3) Analyze coincidences
################################################

tfileCoinc = TFile.Open(input_filename_coinc)
treeCoinc = tfileCoinc.Get("data")
h1_energy_bar = TH1F("h1_energy_bar", "", 200, 0, 200)

tfileCoinc.cd()
for event in range (0,treeCoinc.GetEntries()):
    treeCoinc.GetEntry(event)
    energy1 = treeCoinc.energy[1]-mean_PedTot[channels[1]]
    energy2 = treeCoinc.energy[2]-mean_PedTot[channels[2]]
    energyBar =  energy1 + energy2
    if( treeCoinc.energy[1]>-9. and treeCoinc.energy[2]>-9. ):
        h1_energy_bar.Fill(energyBar)

################################################
## 4) Fits to energy spectrum (511 keV and 1274 keV) 
################################################

minEnergy = 3
maxEnergy = 150

for ch in channels:
    print ch
    if ch == channels[0]:

        histos_Singles[ch].GetXaxis().SetRange(25,1000)
        peak=histos_Singles[ch].GetBinCenter(histos_Singles[ch].GetMaximumBin())
        norm=float(histos_Singles[ch].GetEntries())/histos_Singles[ch].GetNbinsX()
        histos_Singles[ch].GetXaxis().SetRangeUser(minEnergy,maxEnergy)
        '''
        h1_energy_bar.GetXaxis().SetRange(25,1000)
        peak=h1_energy_bar.GetBinCenter(h1_energy_bar.GetMaximumBin())
        norm=float(h1_energy_bar.GetEntries())/h1_energy_bar.GetNbinsX()
        h1_energy_bar.GetXaxis().SetRangeUser(minEnergy,maxEnergy)
        '''
        
        n_paramameters = 19
        fTot = TF1("fTot",totalFunction,minEnergy,maxEnergy,n_paramameters)
        #fTot=TF1("fTot","[0]*(1./(1+TMath::Exp([1]*(x-[2])))+[3]*TMath::Gaus(x,[4],[5])+(1+TMath::Erf((x-[12])/([13]*TMath::Sqrt(x))))*([6]/(1+TMath::Exp([7]*(x-[8])))+[14]*TMath::Gaus(x,[15],[16]))+[9]*TMath::Gaus(x,[10],[11]))",minEnergy,maxEnergy)
        fTot.SetNpx(100000)
        
        ## Normalisation
        fTot.SetParameter(0,norm)
        #fTot.SetParLimits(0,norm*0.1,norm*3)
        ## 1274 KeV compton 
        fTot.SetParameter(1,0.4)
        fTot.SetParLimits(1,0.1,1)
        fTot.SetParameter(2,1.8*peak)
        fTot.SetParLimits(2,1.7*peak,1.9*peak)
        ## 1274 KeV "photo-electric" 
        fTot.SetParameter(3,1.)
        fTot.SetParLimits(3,0.2,5.)
        fTot.SetParameter(4,2.1*peak)
        fTot.SetParLimits(4,2.0*peak,2.2*peak)
        fTot.SetParameter(5,0.1*peak)
        fTot.SetParLimits(5,0.03*peak,0.2*peak)
        fTot.SetParameter(17,0.4)
        fTot.SetParLimits(17,0.1,2.)
        fTot.SetParameter(18,2.)
        fTot.SetParLimits(18,0.1,5.)
        ## 511 KeV compton
        fTot.SetParameter(6,20.)
        #fTot.SetParLimits(6,1,50.)
        fTot.SetParameter(7,0.4)
        fTot.SetParLimits(7,0.1,1)
        fTot.SetParameter(8,0.6*peak)
        fTot.SetParLimits(8,0.05*peak,1.3*peak)
        ## Trigger turn on (Compton+BS)
        fTot.SetParameter(12,5.)
        fTot.SetParLimits(12,0,10.)
        fTot.SetParameter(13,5.)
        fTot.SetParLimits(13,0.1,10.)
        ## 511 KeV photoelectric
        fTot.SetParameter(9,15.)
        #fTot.SetParLimits(9,5,50.)
        fTot.SetParameter(10,peak)
        fTot.SetParLimits(10,0.9*peak,1.1*peak)
        fTot.SetParameter(11,0.05*peak)
        fTot.SetParLimits(11,0.02*peak,0.2*peak)
        ## Back scatter peak
        fTot.SetParameter(14,0.01)
        fTot.SetParLimits(14,0.,10.)
        fTot.SetParameter(15,0.45*peak)
        fTot.SetParLimits(15,0.3*peak,0.6*peak)
        fTot.SetParameter(16,0.07*peak)
        fTot.SetParLimits(16,0.04*peak,0.13*peak)
        ##
        
        canvas_Singles[ch].cd()
 
        histos_Singles[ch].Draw("PE")
        histos_Singles[ch].Fit("fTot","LR+0","",minEnergy,min(peak*2.5,maxEnergy))
        histos_Singles[ch].Fit("fTot","LR+0","",minEnergy,min(peak*2.5,maxEnergy))
        histos_Singles[ch].Fit("fTot","LR+0","",minEnergy,min(peak*2.5,maxEnergy))
        histos_Singles[ch].Fit("fTot","LR+","",minEnergy,min(peak*2.5,maxEnergy))
        '''
        h1_energy_bar.Draw("PE")
        h1_energy_bar.Fit("fTot","LR+0","",minEnergy,min(peak*2.5,maxEnergy))
        h1_energy_bar.Fit("fTot","LR+0","",minEnergy,min(peak*2.5,maxEnergy))
        h1_energy_bar.Fit("fTot","LR+0","",minEnergy,min(peak*2.5,maxEnergy))
        h1_energy_bar.Fit("fTot","LR+","",minEnergy,min(peak*2.5,maxEnergy))
       '''
        
        f1_511keV_peak = TF1("f1_511keV_peak",f_511keV_peak,fTot.GetParameter(10)-5*fTot.GetParameter(11),fTot.GetParameter(10)+5*fTot.GetParameter(11),3)
        f1_511keV_peak.SetNpx(100000)
        f1_511keV_peak.SetLineColor(kGreen+1)
        f1_511keV_peak.SetLineStyle(7)
        f1_511keV_peak.SetParameter(0,fTot.GetParameter(0)*fTot.GetParameter(9))
        f1_511keV_peak.SetParameter(1,fTot.GetParameter(10))
        f1_511keV_peak.SetParameter(2,fTot.GetParameter(11))
        f1_511keV_peak.Draw("same")
        
        f1_1274keV_peak = TF1("f1_1274keV_peak",f_1274keV_peak,fTot.GetParameter(4)-15*fTot.GetParameter(5),fTot.GetParameter(4)+5*fTot.GetParameter(5),5)
        f1_1274keV_peak.SetNpx(100000)
        f1_1274keV_peak.SetLineColor(kGreen+1)
        f1_1274keV_peak.SetLineStyle(7)
        f1_1274keV_peak.SetParameter(0,fTot.GetParameter(0)*fTot.GetParameter(3))
        f1_1274keV_peak.SetParameter(1,fTot.GetParameter(4))
        f1_1274keV_peak.SetParameter(2,fTot.GetParameter(5))
        f1_1274keV_peak.SetParameter(3,fTot.GetParameter(17))
        f1_1274keV_peak.SetParameter(4,fTot.GetParameter(18))
        f1_1274keV_peak.Draw("same")
        
        f1_backscatter_peak_times_turnon = TF1("f1_backscatter_peak_times_turnon",f_backscatter_peak_times_turnon,minEnergy,fTot.GetParameter(15)+5*fTot.GetParameter(16),5)
        f1_backscatter_peak_times_turnon.SetNpx(100000)
        f1_backscatter_peak_times_turnon.SetLineColor(kGreen+1)
        f1_backscatter_peak_times_turnon.SetLineStyle(7)
        f1_backscatter_peak_times_turnon.SetParameter(0,fTot.GetParameter(0)*fTot.GetParameter(14))
        f1_backscatter_peak_times_turnon.SetParameter(1,fTot.GetParameter(15))
        f1_backscatter_peak_times_turnon.SetParameter(2,fTot.GetParameter(16))
        f1_backscatter_peak_times_turnon.SetParameter(3,fTot.GetParameter(12))
        f1_backscatter_peak_times_turnon.SetParameter(4,fTot.GetParameter(13))
        f1_backscatter_peak_times_turnon.Draw("same")

        f1_1274keV_compton = TF1("f1_1274keV_compton",f_1274keV_compton,minEnergy,maxEnergy,3)
        f1_1274keV_compton.SetNpx(100000)
        f1_1274keV_compton.SetLineColor(4)
        f1_1274keV_compton.SetParameter(0,fTot.GetParameter(0))
        f1_1274keV_compton.SetParameter(1,fTot.GetParameter(1))
        f1_1274keV_compton.SetParameter(2,fTot.GetParameter(2))
        #f1_1274keV_compton.Draw("same")
        
        f1_511keV_compton_times_turnon = TF1("f1_511keV_compton_times_turnon",f_511keV_compton_times_turnon,minEnergy,maxEnergy,5)
        f1_511keV_compton_times_turnon.SetNpx(100000)
        f1_511keV_compton_times_turnon.SetLineColor(5)
        f1_511keV_compton_times_turnon.SetParameter(0,fTot.GetParameter(0)*fTot.GetParameter(6))
        f1_511keV_compton_times_turnon.SetParameter(1,fTot.GetParameter(7))
        f1_511keV_compton_times_turnon.SetParameter(2,fTot.GetParameter(8))
        f1_511keV_compton_times_turnon.SetParameter(3,fTot.GetParameter(12))
        f1_511keV_compton_times_turnon.SetParameter(4,fTot.GetParameter(13))
        f1_511keV_compton_times_turnon.Draw("same")
        
        f1_background = TF1("f1_background",f_background,minEnergy,maxEnergy,8)
        f1_background.SetNpx(100000)
        f1_background.SetLineColor(kGreen+3)
        f1_background.SetParameter(0,fTot.GetParameter(0))
        f1_background.SetParameter(1,fTot.GetParameter(1))
        f1_background.SetParameter(2,fTot.GetParameter(2))
        f1_background.SetParameter(3,fTot.GetParameter(0)*fTot.GetParameter(6))
        f1_background.SetParameter(4,fTot.GetParameter(7))
        f1_background.SetParameter(5,fTot.GetParameter(8))
        f1_background.SetParameter(6,fTot.GetParameter(12))
        f1_background.SetParameter(7,fTot.GetParameter(13))
        #f1_background.Draw("same")


################################################
## X) Output file
################################################

tfileoutput = TFile( "output_Run"+run+".root", "recreate" )
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
    canvas_Singles[ch].Write()

#coincidences bar
h1_energy_bar.Write()

tfileoutput.Close()

tfilePed1.cd()
tfilePed1.Close()
tfilePed2.cd()
tfilePed2.Close()
tfileSingles.cd()
tfileSingles.Close()
