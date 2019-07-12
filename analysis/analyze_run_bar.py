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

def setParameters(function,Norm,Peak):

    ## Normalisation
    function.SetParameter(0,Norm)
    function.SetParLimits(0,0.,Norm*1000.)
    
    ## 1274 KeV compton 
    function.SetParameter(1,0.4)
    function.SetParLimits(1,0.1,1)
    function.SetParameter(2,1.8*Peak)
    function.SetParLimits(2,1.7*Peak,1.9*Peak)

    ## 1274 KeV "photo-electric" 
    function.SetParameter(3,1.)
    function.SetParLimits(3,0.2,5.)
    function.SetParameter(4,2.1*Peak)
    function.SetParLimits(4,2.0*Peak,2.2*Peak)
    function.SetParameter(5,0.1*Peak)
    function.SetParLimits(5,0.03*Peak,0.2*Peak)
    function.SetParameter(17,0.4)
    function.SetParLimits(17,0.1,2.)
    function.SetParameter(18,2.)
    function.SetParLimits(18,0.1,10.)
    
    ## 511 KeV compton
    function.SetParameter(6,20.)
    function.SetParLimits(6,0.,1000.)
    function.SetParameter(7,0.4)
    function.SetParLimits(7,0.1,1)
    function.SetParameter(8,0.6*Peak)
    function.SetParLimits(8,0.05*Peak,1.3*Peak)
    
    ## Trigger turn on (Compton+BS)
    function.SetParameter(12,5.)
    function.SetParLimits(12,0,10.)
    function.SetParameter(13,5.)
    function.SetParLimits(13,0.1,10.)
    
    ## 511 KeV photoelectric
    function.SetParameter(9,15.)
    function.SetParLimits(9,0.,1000.)
    function.SetParameter(10,Peak)
    function.SetParLimits(10,0.9*Peak,1.1*Peak)
    function.SetParameter(11,0.05*Peak)
    function.SetParLimits(11,0.02*Peak,0.2*Peak)
    
    ## Back scatter peak
    function.SetParameter(14,0.01)
    function.SetParLimits(14,0.,10.)
    function.SetParameter(15,0.45*Peak)
    function.SetParLimits(15,0.3*Peak,0.6*Peak)
    function.SetParameter(16,0.07*Peak)
    function.SetParLimits(16,0.04*Peak,0.13*Peak)
    ##

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
    
def fitSpectrum(histo,function,xmin,xmax,canvas,fitres,label):

    histo.GetXaxis().SetRange(25,1000)
    peak=histo.GetBinCenter(histo.GetMaximumBin())
    norm=float(histo.GetEntries())/float(histo.GetNbinsX())
    histo.GetXaxis().SetRangeUser(xmin,xmax)
    setParameters(function,norm,peak)
    
    canvas.cd()
    histo.Draw("PE")
    goodChi2 = 0.
    previousChi2overNdf = -99.
    while goodChi2==0.:
        histo.Fit(function.GetName(),"LR+0N","",xmin,min(peak*2.4,xmax))
        print function.GetChisquare(), function.GetNDF(), function.GetChisquare()/function.GetNDF()
        if abs(function.GetChisquare()/function.GetNDF()-previousChi2overNdf)<0.01*previousChi2overNdf:
            histo.Fit(function.GetName(),"LR+","",xmin,min(peak*2.4,xmax))
            canvas.Update()
            goodChi2 = 1.
        previousChi2overNdf = function.GetChisquare()/function.GetNDF()
    print function.GetChisquare(), function.GetNDF(), function.GetChisquare()/function.GetNDF()

    fitres[(label,"peak1","mean","value")]=function.GetParameter(10)
    fitres[(label,"peak1","mean","sigma")]=function.GetParError(10)
    fitres[(label,"peak1","sigma","value")]=function.GetParameter(11)
    fitres[(label,"peak1","sigma","sigma")]=function.GetParError(11)
    fitres[(label,"peak2","mean","value")]=function.GetParameter(4)
    fitres[(label,"peak2","mean","sigma")]=function.GetParError(4)
    fitres[(label,"peak2","sigma","value")]=function.GetParameter(5)
    fitres[(label,"peak2","sigma","sigma")]=function.GetParError(5)
    fitres[(label,"backpeak","mean","value")]=function.GetParameter(15)
    fitres[(label,"backpeak","mean","sigma")]=function.GetParError(15)

    canvas.Write()

def fitSaturation(function,xmin,xmax,canvas,fitres,label):    

    canvas.cd()
    n_points = 2
    a_true_energy = [511.,1275.]
    a_err_true_energy = [0.,0.]
    a_meas_energy = [fitResults[(label,"peak1","mean","value")],
                     fitResults[(label,"peak2","mean","value")]]
    a_err_meas_energy = [fitResults[(label,"peak1","mean","sigma")],
                         fitResults[(label,"peak2","mean","sigma")]]
    g_sat = TGraphErrors(n_points,
                         array('d',a_true_energy),array('d',a_meas_energy),
                         array('d',a_err_true_energy),array('d',a_err_meas_energy))
    g_sat.GetXaxis().SetLimits(xmin,xmax)
    g_sat.GetYaxis().SetLimits(0.,fitResults[(label,"peak2","mean","value")]*1.2)
    g_sat.SetMarkerStyle(20)   
 
    function.SetParameter(0,fitResults[(label,"peak2","mean","value")])
    function.SetParLimits(0,fitResults[(label,"peak2","mean","value")]*0.9,fitResults[(label,"peak2","mean","value")]*3)
    function.SetParameter(1,0.0007)
    function.SetParLimits(1,0.00001,0.01)
    
    g_sat.Draw("APE")
    g_sat.Fit(function.GetName(),"WR","",xmin,xmax)
    g_sat.GetXaxis().UnZoom()
    g_sat.GetYaxis().UnZoom()

    fitres[(label,"peak12","alpha","value")]=function.GetParameter(0)
    fitres[(label,"peak12","alpha","sigma")]=function.GetParError(0)
    fitres[(label,"peak12","beta","value")]=function.GetParameter(1)
    fitres[(label,"peak12","beta","sigma")]=function.GetParError(1)

    canvas.Write()

###############
## Pixel+Bar ##
###############
channels = [59,315,291]
###############

usage = "usage: python analysis/analyze_run_bar.py --run 2 -i /media/cmsdaq/ext/TOFPET/data/BarReproducibility__Temp24__03_07_2019 -o /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis --barCode 99"

parser = optparse.OptionParser(usage)

parser.add_option("-r", "--run", dest="run",
                  help="run number")

parser.add_option("-i", "--input", dest="inputDir",
                  help="input directory")

parser.add_option("-o", "--output", dest="outputDir",
                  help="output directory")

parser.add_option("-b", "--barCode", dest="barCode", default=-9,
                  help="code of the crystal bar")

(opt, args) = parser.parse_args()

if not opt.run:   
    parser.error('run number not provided')

if not opt.inputDir:   
    parser.error('input directory not provided')

if not opt.outputDir:   
    parser.error('output directory not provided')

#if not opt.barCode:   
#    parser.error('code of the crystal bar not provided')

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
h1_energy_pixel = TH1F("h1_energy_pixel", "", 200, 0, 200)
c1_energy_pixel = TCanvas("c1_energy_pixel", "", 900, 700)
c1_sat_pixel = TCanvas("c1_sat_pixel", "", 900, 700)
h1_temp_pixel = TH1F("h1_temp_pixel", "", 1000, 15, 50)
h1_temp_bar = TH1F("h1_temp_bar", "", 1000, 15, 50)
h1_temp_int = TH1F("h1_temp_int", "", 1000, 15, 50)

tfileSingles.cd()
for event in range (0,treeSingles.GetEntries()):
    treeSingles.GetEntry(event)
    if( treeSingles.channelID==channels[0]):
        h1_energy_pixel.Fill(treeSingles.energy-mean_PedTot[channels[0]])
    h1_temp_pixel.Fill(treeSingles.tempSiPMRef)
    h1_temp_bar.Fill(treeSingles.tempSiPMTest)
    h1_temp_int.Fill(treeSingles.tempInt)

Temp_pixel = h1_temp_pixel.GetMean()
Temp_bar = h1_temp_bar.GetMean()
Temp_internal = h1_temp_int.GetMean()

################################################
## 4) Analyze coincidences
################################################

tfileCoinc = TFile.Open(input_filename_coinc)
treeCoinc = tfileCoinc.Get("data")
h1_energyTot_bar = TH1F("h1_energyTot_bar", "", 200, 0, 200)
h1_energy1_bar = TH1F("h1_energy1_bar", "", 200, 0, 200)
h1_energy2_bar = TH1F("h1_energy2_bar", "", 200, 0, 200)
h2_energy1VSenergy2_bar = TH2F("h2_energy1VSenergy2_bar", "", 200, 0, 200, 200, 0, 200)
c1_energy1_bar = TCanvas("c1_energy1_bar", "", 900, 700)
c1_energyTot_bar = TCanvas("c1_energyTot_bar", "", 900, 700)
c1_sat_bar = TCanvas("c1_sat_bar", "", 900, 700)

tfileCoinc.cd()
for event in range (0,treeCoinc.GetEntries()):
    treeCoinc.GetEntry(event)
    energy1 = treeCoinc.energy[1]-mean_PedTot[channels[1]]
    energy2 = treeCoinc.energy[2]-mean_PedTot[channels[2]]
    energyBar =  energy1 + energy2
    if( treeCoinc.energy[1]>-9. and treeCoinc.energy[2]>-9. ):
        h1_energyTot_bar.Fill(energyBar)
        h1_energy1_bar.Fill(energy1)
        h1_energy2_bar.Fill(energy2)
        h2_energy1VSenergy2_bar.Fill(energy1,energy2)

################################################
## 5) Output file
################################################

tfileoutput = TFile( "histo_Run"+run+".root", "recreate" )
tfileoutput.cd()

################################################
## 6) Fit energy spectra
################################################

fitResults = {}

## Setup
minEnergy = 4
maxEnergy = 150
n_paramameters = 19

## Pixel (ref)
fTot_pixel = TF1("fTot_pixel",totalFunction,minEnergy,maxEnergy,n_paramameters)
fTot_pixel.SetNpx(1000)
fitSpectrum(h1_energy_pixel,fTot_pixel,minEnergy,maxEnergy,c1_energy_pixel,fitResults,"pixel")

## Bar (ref)
fTot_bar = TF1("fTot_bar",totalFunction,minEnergy,maxEnergy,n_paramameters)
fTot_bar.SetNpx(1000)
fitSpectrum(h1_energyTot_bar,fTot_bar,minEnergy,maxEnergy,c1_energyTot_bar,fitResults,"bar")

################################################
## 7) Fit response vs photon energy
################################################

## Setup
minE = 0.
maxE = 1300.

## Pixel (ref)
fExpo_pixel = TF1("fExpo_pixel","[0]*(1-TMath::Exp(-[1]*x))",minE,maxE)
fitSaturation(fExpo_pixel,minE,maxE,c1_sat_pixel,fitResults,"pixel")

## Bar (ref)
fExpo_bar = TF1("fExpo_bar","[0]*(1-TMath::Exp(-[1]*x))",minE,maxE)
fitSaturation(fExpo_bar,minE,maxE,c1_sat_bar,fitResults,"bar")

################################################
## 8) Write histograms
################################################

#Pedestals
for ch in channels:
    #pedestals
    histos_Ped1[ch].Write()
    histos_Ped2[ch].Write()
    histos_PedTot[ch].Write()
    #print "--- Channel = "+str(ch).zfill(3)+" ---"
    #print "Pedestal1 "+str(mean_Ped1[ch])+" "+str(rms_Ped1[ch]) 
    #print "Pedestal2 "+str(mean_Ped2[ch])+" "+str(rms_Ped2[ch]) 
    #print "PedestalTot "+str(mean_PedTot[ch])+" "+str(rms_PedTot[ch]) 

#Pixel
h1_energy_pixel.Write()
print "--- Pixel ---"
print "Pixel Peak 1: "+str(fitResults[('pixel',"peak1","mean","value")])+" +/- "+str(fitResults[('pixel',"peak1","mean","sigma")]) 
print "Pixel Peak 2: "+str(fitResults[('pixel',"peak2","mean","value")])+" +/- "+str(fitResults[('pixel',"peak2","mean","sigma")]) 
print "Pixel Backpeak : "+str(fitResults[('pixel',"backpeak","mean","value")])+" +/- "+str(fitResults[('pixel',"backpeak","mean","sigma")]) 
print "Pixel Alpha: "+str(fitResults[('pixel',"peak12","alpha","value")])+" +/- "+str(fitResults[('pixel',"peak12","alpha","sigma")]) 
print "Pixel Beta: "+str(fitResults[('pixel',"peak12","beta","value")])+" +/- "+str(fitResults[('pixel',"peak12","beta","sigma")]) 

#Bar
h1_energyTot_bar.Write()
h1_energy1_bar.Write()
h1_energy2_bar.Write()
h2_energy1VSenergy2_bar.Write()
print "--- Bar ---"
print "Bar Peak 1: "+str(fitResults[('bar',"peak1","mean","value")])+" +/- "+str(fitResults[('bar',"peak1","mean","sigma")]) 
print "Bar Peak 2: "+str(fitResults[('bar',"peak2","mean","value")])+" +/- "+str(fitResults[('bar',"peak2","mean","sigma")]) 
print "Bar Backpeak : "+str(fitResults[('bar',"backpeak","mean","value")])+" +/- "+str(fitResults[('bar',"backpeak","mean","sigma")]) 
print "Pixel Alpha: "+str(fitResults[('bar',"peak12","alpha","value")])+" +/- "+str(fitResults[('bar',"peak12","alpha","sigma")]) 
print "Pixel Beta: "+str(fitResults[('bar',"peak12","beta","value")])+" +/- "+str(fitResults[('bar',"peak12","beta","sigma")]) 

tfileoutput.Close()
tfilePed1.cd()
tfilePed1.Close()
tfilePed2.cd()
tfilePed2.Close()
tfileSingles.cd()
tfileSingles.Close()
tfileCoinc.cd()
tfileCoinc.Close()

################################################
## 8) Write root tree with measurements
################################################

tfileoutputtree = TFile( "tree_Run"+run+".root", "recreate" )
tfileoutputtree.cd()

treeOutput = TTree( 'results', 'root tree with measurements' )

peak1_mean_pixel = array( 'd', [ -999. ] )
err_peak1_mean_pixel = array( 'd', [ -999. ] )
peak2_mean_pixel = array( 'd', [ -999. ] )
err_peak2_mean_pixel = array( 'd', [ -999. ] )
peak1_sigma_pixel = array( 'd', [ -999. ] )
err_peak1_sigma_pixel = array( 'd', [ -999. ] )
peak2_sigma_pixel = array( 'd', [ -999. ] )
err_peak2_sigma_pixel = array( 'd', [ -999. ] )
alpha_pixel = array( 'd', [ -999. ] )
err_alpha_pixel = array( 'd', [ -999. ] )
beta_pixel = array( 'd', [ -999. ] )
err_beta_pixel = array( 'd', [ -999. ] )
#
peak1_mean_bar = array( 'd', [ -999. ] )
err_peak1_mean_bar = array( 'd', [ -999. ] )
peak2_mean_bar = array( 'd', [ -999. ] )
err_peak2_mean_bar = array( 'd', [ -999. ] )
peak1_sigma_bar = array( 'd', [ -999. ] )
err_peak1_sigma_bar = array( 'd', [ -999. ] )
peak2_sigma_bar = array( 'd', [ -999. ] )
err_peak2_sigma_bar = array( 'd', [ -999. ] )
alpha_bar = array( 'd', [ -999. ] )
err_alpha_bar = array( 'd', [ -999. ] )
beta_bar = array( 'd', [ -999. ] )
err_beta_bar = array( 'd', [ -999. ] )
#
temp_pixel = array( 'd', [ -999. ] )
temp_bar = array( 'd', [ -999. ] )
temp_int = array( 'd', [ -999. ] )
#
code_bar = array( 'i', [ -9 ] )

treeOutput.Branch( 'peak1_mean_pixel', peak1_mean_pixel, 'peak1_mean_pixel/D' )
treeOutput.Branch( 'err_peak1_mean_pixel', err_peak1_mean_pixel, 'err_peak1_mean_pixel/D' )
treeOutput.Branch( 'peak2_mean_pixel', peak2_mean_pixel, 'peak2_mean_pixel/D' )
treeOutput.Branch( 'err_peak2_mean_pixel', err_peak2_mean_pixel, 'err_peak2_mean_pixel/D' )
treeOutput.Branch( 'peak1_sigma_pixel', peak1_sigma_pixel, 'peak1_sigma_pixel/D' )
treeOutput.Branch( 'err_peak1_sigma_pixel', err_peak1_sigma_pixel, 'err_peak1_sigma_pixel/D' )
treeOutput.Branch( 'peak2_sigma_pixel', peak2_sigma_pixel, 'peak2_sigma_pixel/D' )
treeOutput.Branch( 'err_peak2_sigma_pixel', err_peak2_sigma_pixel, 'err_peak2_sigma_pixel/D' )
treeOutput.Branch( 'alpha_pixel', alpha_pixel, 'alpha_pixel/D' )
treeOutput.Branch( 'err_alpha_pixel', err_alpha_pixel, 'err_alpha_pixel/D' )
treeOutput.Branch( 'beta_pixel', beta_pixel, 'beta_pixel/D' )
treeOutput.Branch( 'err_beta_pixel', err_beta_pixel, 'err_beta_pixel/D' )
#
treeOutput.Branch( 'peak1_mean_bar', peak1_mean_bar, 'peak1_mean_bar/D' )
treeOutput.Branch( 'err_peak1_mean_bar', err_peak1_mean_bar, 'err_peak1_mean_bar/D' )
treeOutput.Branch( 'peak2_mean_bar', peak2_mean_bar, 'peak2_mean_bar/D' )
treeOutput.Branch( 'err_peak2_mean_bar', err_peak2_mean_bar, 'err_peak2_mean_bar/D' )
treeOutput.Branch( 'peak1_sigma_bar', peak1_sigma_bar, 'peak1_sigma_bar/D' )
treeOutput.Branch( 'err_peak1_sigma_bar', err_peak1_sigma_bar, 'err_peak1_sigma_bar/D' )
treeOutput.Branch( 'peak2_sigma_bar', peak2_sigma_bar, 'peak2_sigma_bar/D' )
treeOutput.Branch( 'err_peak2_sigma_bar', err_peak2_sigma_bar, 'err_peak2_sigma_bar/D' )
treeOutput.Branch( 'alpha_bar', alpha_bar, 'alpha_bar/D' )
treeOutput.Branch( 'err_alpha_bar', err_alpha_bar, 'err_alpha_bar/D' )
treeOutput.Branch( 'beta_bar', beta_bar, 'beta_bar/D' )
treeOutput.Branch( 'err_beta_bar', err_beta_bar, 'err_beta_bar/D' )
#
treeOutput.Branch( 'temp_pixel', temp_pixel, 'temp_pixel/D' )
treeOutput.Branch( 'temp_bar', temp_bar, 'temp_bar/D' )
treeOutput.Branch( 'temp_int', temp_int, 'temp_int/D' )
#
treeOutput.Branch( 'code_bar', code_bar, 'code_bar/I' )

peak1_mean_pixel[0] = fitResults[('pixel',"peak1","mean","value")]
err_peak1_mean_pixel[0] = fitResults[('pixel',"peak1","mean","sigma")]
peak2_mean_pixel[0] = fitResults[('pixel',"peak2","mean","value")]
err_peak2_mean_pixel[0] = fitResults[('pixel',"peak2","mean","sigma")]
peak1_sigma_pixel[0] = fitResults[('pixel',"peak1","sigma","value")]
err_peak1_sigma_pixel[0] = fitResults[('pixel',"peak1","sigma","sigma")]
peak2_sigma_pixel[0] = fitResults[('pixel',"peak2","sigma","value")]
err_peak2_sigma_pixel[0] = fitResults[('pixel',"peak2","sigma","sigma")]
alpha_pixel[0] = fitResults[('pixel',"peak12","alpha","value")]
err_alpha_pixel[0] = fitResults[('pixel',"peak12","alpha","sigma")]
beta_pixel[0] = fitResults[('pixel',"peak12","beta","value")]
err_beta_pixel[0] = fitResults[('pixel',"peak12","beta","sigma")]
#
peak1_mean_bar[0] = fitResults[('bar',"peak1","mean","value")]
err_peak1_mean_bar[0] = fitResults[('bar',"peak1","mean","sigma")]
peak2_mean_bar[0] = fitResults[('bar',"peak2","mean","value")]
err_peak2_mean_bar[0] = fitResults[('bar',"peak2","mean","sigma")]
peak1_sigma_bar[0] = fitResults[('bar',"peak1","sigma","value")]
err_peak1_sigma_bar[0] = fitResults[('bar',"peak1","sigma","sigma")]
peak2_sigma_bar[0] = fitResults[('bar',"peak2","sigma","value")]
err_peak2_sigma_bar[0] = fitResults[('bar',"peak2","sigma","sigma")]
alpha_bar[0] = fitResults[('bar',"peak12","alpha","value")]
err_alpha_bar[0] = fitResults[('bar',"peak12","alpha","sigma")]
beta_bar[0] = fitResults[('bar',"peak12","beta","value")]
err_beta_bar[0] = fitResults[('bar',"peak12","beta","sigma")]
#
temp_pixel[0] = Temp_pixel
temp_bar[0] = Temp_bar
temp_int[0] = Temp_internal
#
if opt.barCode:
    code_bar[0] = int(opt.barCode)

treeOutput.Fill()
tfileoutputtree.Write()
tfileoutputtree.Close()

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

'''


