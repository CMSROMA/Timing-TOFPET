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


def Map(tf):
    """                                                                                                                  
    Maps objets as dict[obj_name][0] using a TFile (tf) and TObject to browse.                                           
    """
    m = {}
    for k in tf.GetListOfKeys():
        n = k.GetName()
        m[n] = tf.Get(n)
    return m


def setParameters(function,Norm,Peak):

    ## Normalisation
    function.SetParameter(0,Norm)
    function.SetParLimits(0,0.,Norm*1000.)
    
    ## 1274 KeV compton 
    function.SetParameter(1,0.4)
    function.SetParLimits(1,0.1,1)
    function.SetParameter(2,1.7*Peak)
    function.SetParLimits(2,1.6*Peak,1.8*Peak)

    ## 1274 KeV "photo-electric" 
    function.SetParameter(3,1.)
    function.SetParLimits(3,0.2,5.)
    function.SetParameter(4,1.8*Peak)
    function.SetParLimits(4,1.7*Peak,1.9*Peak)
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
    function.SetParameter(8,0.7*Peak)
    function.SetParLimits(8,0.6*Peak,0.85*Peak)
    
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

def setParameters_coinc(function,Norm,Peak):

    ## Normalisation
    function.SetParameter(0,Norm)
    function.SetParLimits(0,0.,Norm*1000.)
    
    ## 511 KeV compton
    function.SetParameter(3,20.)
    function.SetParLimits(3,0.,1000.)
    function.SetParameter(4,0.4)
    function.SetParLimits(4,0.1,1)
    function.SetParameter(5,0.7*Peak)
    function.SetParLimits(5,0.6*Peak,0.85*Peak)
    
    ## Trigger turn on (Compton+BS)
    function.SetParameter(1,5.)
    function.SetParLimits(1,0,10.)
    function.SetParameter(2,5.)
    function.SetParLimits(2,0.1,10.)
    
    ## 511 KeV photoelectric
    function.SetParameter(6,15.)
    function.SetParLimits(6,0.,1000.)
    function.SetParameter(7,Peak)
    function.SetParLimits(7,0.9*Peak,1.1*Peak)
    function.SetParameter(8,0.05*Peak)
    function.SetParLimits(8,0.02*Peak,0.1*Peak)

    #flat background
    function.SetParameter(9,15.)
    function.SetParLimits(9,0.,1000.)
    
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

def totalFunction_coinc(x,par):    
    return par[0]*(( 1 + TMath.Erf((x[0]-par[1])/(par[2]*TMath.Sqrt(x[0]))) )*( par[3]/(1+TMath.Exp(par[4]*(x[0]-par[5]))) )+par[6]*TMath.Gaus(x[0],par[7],par[8])+par[9])

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
    
def fitSpectrum(histo,function,xmin,xmax,canvas,fitres,label,code,run,outputDIR):

    histo.GetXaxis().SetRange(25,1000)
    peak=histo.GetBinCenter(histo.GetMaximumBin())
    norm=float(histo.GetEntries())/float(histo.GetNbinsX())
    histo.GetXaxis().SetRangeUser(xmin,xmax)
    setParameters(function,norm,peak)

    #histo.SetTitle( "Run" + str(run.zfill(6)) + " " + label + str(code.zfill(6)) )
    histo.GetXaxis().SetTitle("QDC counts")
    histo.GetYaxis().SetTitle("Events")
    histo.GetYaxis().SetTitleOffset(1.6)
 
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


    f1_bkg = TF1("f1_bkg",function,xmin,min(peak*2.4,xmax),19)
    f1_bkg.SetLineColor(kGreen+1)
    #f1_bkg.SetLineStyle(7)
    f1_bkg.SetParameter(0,function.GetParameter(0))
    f1_bkg.SetParameter(1,function.GetParameter(1))
    f1_bkg.SetParameter(2,function.GetParameter(2))
    f1_bkg.SetParameter(3,function.GetParameter(3))
    f1_bkg.SetParameter(4,function.GetParameter(4))
    f1_bkg.SetParameter(5,function.GetParameter(5))
    f1_bkg.SetParameter(6,function.GetParameter(6))
    f1_bkg.SetParameter(7,function.GetParameter(7))
    f1_bkg.SetParameter(8,function.GetParameter(8))
    f1_bkg.SetParameter(9,0.)
    f1_bkg.SetParameter(10,function.GetParameter(10))
    f1_bkg.SetParameter(11,function.GetParameter(11))
    f1_bkg.SetParameter(12,function.GetParameter(12))
    f1_bkg.SetParameter(13,function.GetParameter(13))
    f1_bkg.SetParameter(14,function.GetParameter(14))
    f1_bkg.SetParameter(15,function.GetParameter(15))
    f1_bkg.SetParameter(16,function.GetParameter(16))
    f1_bkg.SetParameter(17,function.GetParameter(17))
    f1_bkg.SetParameter(18,function.GetParameter(18))

    f1_bkg.Draw("same")

    pt1 = TPaveText(0.100223,0.915556,0.613586,0.967407,"brNDC")
    text1 = pt1.AddText( "Run" + str(run).zfill(6) + " " + label + str(code).zfill(6) )
    pt1.SetFillColor(0)
    pt1.Draw()

    canvas.Update()
    canvas.SaveAs(outputDIR+"/"+"Run"+str(run).zfill(6)+"_BAR"+str(code).zfill(6)+"_SourceSpectrum_"+label+".pdf")
    canvas.SaveAs(outputDIR+"/"+"Run"+str(run).zfill(6)+"_BAR"+str(code).zfill(6)+"_SourceSpectrum_"+label+".png")
    canvas.Write()

def fitSpectrum_coinc(histo,function,xmin,xmax,canvas,fitres,label,code,run,outputDIR):

    histo.GetXaxis().SetRange(25,1000)
    peak=histo.GetBinCenter(histo.GetMaximumBin())
    norm=float(histo.GetEntries())/float(histo.GetNbinsX())
    histo.GetXaxis().SetRangeUser(xmin,xmax)
    setParameters_coinc(function,norm,peak)
    print peak

    #histo.SetTitle( "Run" + str(run.zfill(6)) + " " + label + str(code.zfill(6)) )
    histo.GetXaxis().SetTitle("QDC counts")
    histo.GetYaxis().SetTitle("Events")
    histo.GetYaxis().SetTitleOffset(1.6)
 
    canvas.cd()
    histo.Draw("PE")
    goodChi2 = 0.
    previousChi2overNdf = -99.
    while goodChi2==0.:
        histo.Fit(function.GetName(),"LR+0N","",xmin,min(peak*1.6,xmax))
        print function.GetChisquare(), function.GetNDF(), function.GetChisquare()/function.GetNDF()
        if abs(function.GetChisquare()/function.GetNDF()-previousChi2overNdf)<0.01*previousChi2overNdf:
            histo.Fit(function.GetName(),"LR+","",xmin,min(peak*1.6,xmax))
            canvas.Update()
            goodChi2 = 1.
        previousChi2overNdf = function.GetChisquare()/function.GetNDF()
    print function.GetChisquare(), function.GetNDF(), function.GetChisquare()/function.GetNDF()

    fitres[(label,"peak1","mean","value")]=function.GetParameter(7)
    fitres[(label,"peak1","mean","sigma")]=function.GetParError(7)
    fitres[(label,"peak1","sigma","value")]=function.GetParameter(8)
    fitres[(label,"peak1","sigma","sigma")]=function.GetParError(8)

    f1_bkg = TF1("f1_bkg",function,xmin,min(peak*1.6,xmax),10)
    f1_bkg.SetLineColor(kGreen+1)
    #f1_bkg.SetLineStyle(7)
    f1_bkg.SetParameter(0,function.GetParameter(0))
    f1_bkg.SetParameter(1,function.GetParameter(1))
    f1_bkg.SetParameter(2,function.GetParameter(2))
    f1_bkg.SetParameter(3,function.GetParameter(3))
    f1_bkg.SetParameter(4,function.GetParameter(4))
    f1_bkg.SetParameter(5,function.GetParameter(5))
    f1_bkg.SetParameter(6,0.)
    f1_bkg.SetParameter(7,function.GetParameter(7))
    f1_bkg.SetParameter(8,function.GetParameter(8))
    f1_bkg.SetParameter(9,function.GetParameter(9))

    f1_bkg.Draw("same")

    pt2 = TPaveText(0.100223,0.915556,0.613586,0.967407,"brNDC")    
    text2 = pt2.AddText( "Run" + str(run).zfill(6) + " " + label + str(code).zfill(6) )
    pt2.SetFillColor(0)
    pt2.Draw()

    canvas.Update()
    canvas.SaveAs(outputDIR+"/"+"Run"+str(run).zfill(6)+"_BAR"+str(code).zfill(6)+"_SourceSpectrum_"+label+".pdf")
    canvas.SaveAs(outputDIR+"/"+"Run"+str(run).zfill(6)+"_BAR"+str(code).zfill(6)+"_SourceSpectrum_"+label+".png")
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
channels = [59,270,300]
###############

usage = "usage: python analysis/analyze_run_bar.py --run 2 -i /media/cmsdaq/ext/TOFPET/data/BarReproducibility__Temp24__03_07_2019 -o /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis --barCode 99"

parser = optparse.OptionParser(usage)

parser.add_option("-r", "--run", dest="run",
                  help="run number")

parser.add_option("-i", "--input", dest="inputDir",default="/data/TOFPET/LYSOBARS",
                  help="input directory")

parser.add_option("-o", "--output", dest="outputDir",default="/data/TOFPET/LYSOBARS/RESULTS",
                  help="output directory")

parser.add_option("-b", "--barCode", dest="barCode", default=-99,
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
gStyle.SetOptStat("e")
gStyle.SetOptFit(1111111)
gStyle.SetStatH(0.09)

################################################
## 1) Find input files
################################################

run = str(opt.run).zfill(6)
print "Run ", run

input_filename_ped1 = ""
input_filename_ped2 = ""
input_filename_singles = ""
input_filename_coinc = ""

list_allfiles = os.listdir(opt.inputDir)
#print list_allfiles

for file in list_allfiles:

    if ("Run"+str(int(opt.run)-1).zfill(6) in file and "_singles.root" in file):
        input_filename_ped1 = opt.inputDir + "/" + file
        print input_filename_ped1

    if ("Run"+str(int(opt.run)+1).zfill(6) in file and "_singles.root" in file):
        input_filename_ped2 = opt.inputDir + "/" + file
        print input_filename_ped2

    if ("Run"+run in file and "_singles.root" in file):
        input_filename_singles = opt.inputDir + "/" + file
        print input_filename_singles

    if ("Run"+run in file and "_coincidences.root" in file):
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

posX = float(((input_filename_coinc.split("_X")[1]).split("_"))[0])
if not (posX >-1 and posX<60):
    parser.error('Info on array position  not found in the input filename')
else:
    print "PosX: ", posX

posY = float(((input_filename_coinc.split("_Y")[1]).split("_"))[0])
if not (posY >-1 and posY<60):
    parser.error('Info on array position  not found in the input filename')
else:
    print "PosY: ", posY

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

    histo1 = TProfile("tprof_ped1_energy_ch"+str(ch), "", 4, -0.5, 3.5, 0, 500,"s")
    #histo1 = TH1F("h1_ped1_energy_ch"+str(ch), "", 500, 0, 500)
    histos_Ped1[ch]=histo1

    histo2 = TProfile("tprof_ped2_energy_ch"+str(ch), "", 4, -0.5, 3.5, 0, 500,"s")
    #histo2 = TH1F("h1_ped2_energy_ch"+str(ch), "", 500, 0, 500)
    histos_Ped2[ch]=histo2

    histoTot = TProfile("tprof_pedTot_energy_ch"+str(ch), "", 4, -0.5, 3.5, 0, 500,"s")
    #histoTot = TH1F("h1_pedTot_energy_ch"+str(ch), "", 500, 0, 500)
    histos_PedTot[ch]=histoTot

    for tac in range (0,4):
        mean_Ped1[(ch,tac)]=-9 
        rms_Ped1[(ch,tac)]=-9 
        mean_Ped2[(ch,tac)]=-9 
        rms_Ped2[(ch,tac)]=-9 
        mean_PedTot[(ch,tac)]=-9 
        rms_PedTot[(ch,tac)]=-9 

tfilePed1.cd()
for event in range (0,treePed1.GetEntries()):
    treePed1.GetEntry(event)
    for ch in channels:
        if( treePed1.channelID==ch):
            histos_Ped1[ch].Fill(treePed1.tacID,treePed1.energy)
            histos_PedTot[ch].Fill(treePed1.tacID,treePed1.energy)

tfilePed2.cd()
for event in range (0,treePed2.GetEntries()):
    treePed2.GetEntry(event)
    for ch in channels:
        if( treePed2.channelID==ch):
            histos_Ped2[ch].Fill(treePed2.tacID,treePed2.energy)
            histos_PedTot[ch].Fill(treePed2.tacID,treePed2.energy)

h1_pedTotMean=TH1F("h1_pedTotMean","",3000,-0.5,2999.5)
h1_pedTotRms=TH1F("h1_pedTotRms","",3000,-0.5,2999.5)

for ch in channels:
    for tac in range (0,4):

        mean_Ped1[(ch,tac)]=histos_Ped1[ch].GetBinContent(tac+1)
        rms_Ped1[(ch,tac)]=histos_Ped1[ch].GetBinError(tac+1)

        mean_Ped2[(ch,tac)]=histos_Ped2[ch].GetBinContent(tac+1)
        rms_Ped2[(ch,tac)]=histos_Ped2[ch].GetBinError(tac+1)

        mean_PedTot[(ch,tac)]=histos_PedTot[ch].GetBinContent(tac+1)
        rms_PedTot[(ch,tac)]=histos_PedTot[ch].GetBinError(tac+1)

        h1_pedTotMean.SetBinContent(ch*4+tac+1,mean_PedTot[(ch,tac)])
        h1_pedTotMean.SetBinError(ch*4+tac+1,0)
        h1_pedTotRms.SetBinContent(ch*4+tac+1,rms_PedTot[(ch,tac)])
        h1_pedTotRms.SetBinError(ch*4+tac+1,0)

commandOutputDir = "mkdir -p "+opt.outputDir
print commandOutputDir
os.system(commandOutputDir)

pedoutput = TFile( opt.outputDir+"/"+"ped_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root", "recreate" )
pedoutput.cd()
h1_pedTotMean.Write()
h1_pedTotRms.Write()
pedoutput.Close()

print "Pedestals analyzed"


################################################
## 3) Analyze singles
################################################

print "Analzying singles"

gROOT.ProcessLine('o = TString(gSystem->GetMakeSharedLib()); o = o.ReplaceAll(" -c ", " -std=c++11 -c "); gSystem->SetMakeSharedLib(o.Data());')
#gROOT.ProcessLine(".L /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis/singleAnalysis.C+")
gROOT.ProcessLine(".L analysis/singleAnalysis.C+")
gROOT.ProcessLine('TFile* f = new TFile("%s");'%input_filename_singles)
gROOT.ProcessLine('TTree* tree; f->GetObject("data",tree);')
gROOT.ProcessLine("singleAnalysis sAnalysis(tree);")
gROOT.ProcessLine('sAnalysis.LoadPedestals("%s");'%(opt.outputDir+"/"+"ped_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root"))
gROOT.ProcessLine('sAnalysis.pixelChId=%d;'%channels[0])
gROOT.ProcessLine('sAnalysis.outputFile="%s";'%(opt.outputDir+"/"+"histo_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root"))
gBenchmark.Start( 'singleAnalysis' )
gROOT.ProcessLine("sAnalysis.Loop();")
gBenchmark.Show( 'singleAnalysis' )

print "Singles analyzed"

#Temp_pixel = h1_temp_pixel.GetMean()
#Temp_bar = h1_temp_bar.GetMean()
#Temp_internal = h1_temp_int.GetMean()

################################################
## 4) Analyze coincidences
################################################

print "Analyzing coincidences"

#gROOT.ProcessLine(".L /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis/coincidenceAnalysisBar.C+")
gROOT.ProcessLine(".L analysis/coincidenceAnalysisBar.C+")
gROOT.ProcessLine('TFile* fCoinc = new TFile("%s");'%input_filename_coinc)
gROOT.ProcessLine('TTree* treeCoinc; fCoinc->GetObject("data",treeCoinc);')
gROOT.ProcessLine("coincidenceAnalysisBar cAnalysis(treeCoinc);")
gROOT.ProcessLine('cAnalysis.LoadPedestals("%s");'%(opt.outputDir+"/"+"ped_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root"))
gROOT.ProcessLine('cAnalysis.channels[0]=%d;'%channels[0])
gROOT.ProcessLine('cAnalysis.channels[1]=%d;'%channels[1])
gROOT.ProcessLine('cAnalysis.channels[2]=%d;'%channels[2])
gROOT.ProcessLine('cAnalysis.outputFile="%s";'%(opt.outputDir+"/"+"histo_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root"))
gBenchmark.Start( 'coincidenceAnalysisBar' )
gROOT.ProcessLine("cAnalysis.Loop();")
gBenchmark.Show( 'coincidenceAnalysisBar' )

print "Coincidences analyzed"

################################################
## 5) Output file
################################################
tfileoutput = TFile( opt.outputDir+"/"+"histo_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root", "update" )
tfileoutput.cd()
histos=Map(tfileoutput)

################################################
## 6) Fit energy spectra
################################################
c1_energy_pixel = TCanvas("c1_energy_pixel", "", 900, 700)
c1_energy_pixelCoinc = TCanvas("c1_energy_pixelCoinc", "", 900, 700)
c1_energy_bar = TCanvas("c1_energy_bar", "", 900, 700)
c1_energy_barCoinc = TCanvas("c1_energy_barCoinc", "", 900, 700)

fitResults = {}

## Setup singles
minEnergy = 7
maxEnergy = 250
n_paramameters = 19

## Pixel
fTot_pixel = TF1("fTot_pixel",totalFunction,minEnergy,maxEnergy,n_paramameters)
fTot_pixel.SetNpx(1000)
fitSpectrum(histos['h1_energy_pixel'],fTot_pixel,minEnergy,maxEnergy,c1_energy_pixel,fitResults,"pixel","",opt.run,opt.outputDir)
histos['h1_energy_pixel'].Write()
## Bar
fTot_bar = TF1("fTot_bar",totalFunction,minEnergy,maxEnergy,n_paramameters)
fTot_bar.SetNpx(1000)
fitSpectrum(histos['h1_energyTot_bar'],fTot_bar,minEnergy,maxEnergy,c1_energy_pixelCoinc,fitResults,"bar",opt.barCode,opt.run,opt.outputDir)
histos['h1_energyTot_bar'].Write()

## Setup coincidences
n_paramameters_coinc = 10

## Pixel
minEnergy_coinc = 7
maxEnergy_coinc = 160

fTot_pixel_coinc = TF1("fTot_pixel_coinc",totalFunction_coinc,minEnergy_coinc,maxEnergy_coinc,n_paramameters_coinc)
fTot_pixel_coinc.SetNpx(1000)
fitSpectrum_coinc(histos['h1_energy_pixel_coinc'],fTot_pixel_coinc,minEnergy_coinc,maxEnergy_coinc,c1_energy_bar,fitResults,"pixelCoinc","",opt.run,opt.outputDir)
histos['h1_energy_pixel_coinc'].Write()

## Bar
minEnergy_coinc = 7
maxEnergy_coinc = 100

fTot_bar_coinc = TF1("fTot_bar_coinc",totalFunction_coinc,minEnergy_coinc,maxEnergy_coinc,n_paramameters_coinc)
fTot_bar_coinc.SetNpx(1000)
fitSpectrum_coinc(histos['h1_energyTot_bar_coinc'],fTot_bar_coinc,minEnergy_coinc,maxEnergy_coinc,c1_energy_barCoinc,fitResults,"barCoinc",opt.barCode,opt.run,opt.outputDir)
histos['h1_energyTot_bar_coinc'].Write()

tfileoutput.Close()

'''
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
'''

################################################
## 8) Coincidence time resolution (CTR)
################################################

print "Cuts for CTR calculation:"
print fitResults[('pixelCoinc',"peak1","mean","value")] - fitResults[('pixelCoinc',"peak1","sigma","value")]
print fitResults[('pixelCoinc',"peak1","mean","value")] + fitResults[('pixelCoinc',"peak1","sigma","value")]
print fitResults[('barCoinc',"peak1","mean","value")] - fitResults[('barCoinc',"peak1","sigma","value")]
print fitResults[('barCoinc',"peak1","mean","value")] + fitResults[('barCoinc',"peak1","sigma","value")]

#gROOT.ProcessLine(".L /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis/ctrAnalysisBar.C+")
gROOT.ProcessLine(".L analysis/ctrAnalysisBar.C+")
gROOT.ProcessLine('TFile* fCTR = new TFile("%s");'%input_filename_coinc)
gROOT.ProcessLine('TTree* treeCTR; fCTR->GetObject("data",treeCTR);')
gROOT.ProcessLine("ctrAnalysisBar ctAnalysis(treeCTR);")

gROOT.ProcessLine('ctAnalysis.LoadPedestals("%s");'%(opt.outputDir+"/"+"ped_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root"))
gROOT.ProcessLine('ctAnalysis.channels[0]=%d;'%channels[0])
gROOT.ProcessLine('ctAnalysis.channels[1]=%d;'%channels[1])
gROOT.ProcessLine('ctAnalysis.channels[2]=%d;'%channels[2])
gROOT.ProcessLine('ctAnalysis.outputFile="%s";'%(opt.outputDir+"/"+"histo_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root"))
gROOT.ProcessLine('ctAnalysis.pixel_511Peak_mean=%f;'%fitResults[('pixelCoinc',"peak1","mean","value")])
gROOT.ProcessLine('ctAnalysis.pixel_511Peak_sigma=%f;'%fitResults[('pixelCoinc',"peak1","sigma","value")])
gROOT.ProcessLine('ctAnalysis.bar_511Peak_mean=%f;'%fitResults[('barCoinc',"peak1","mean","value")])
gROOT.ProcessLine('ctAnalysis.bar_511Peak_sigma=%f;'%fitResults[('barCoinc',"peak1","sigma","value")])

gBenchmark.Start( 'ctrAnalysis' )
gROOT.ProcessLine("ctAnalysis.Loop();")
gBenchmark.Show( 'ctrAnalysis' )

##CTR
tfileoutput = TFile( opt.outputDir+"/"+"histo_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root", "update" )
tfileoutput.cd()
histos=Map(tfileoutput)

c1_CTR = TCanvas("c1_CTR", "", 900, 700)
#c1_energy.cd()
c1_CTR.cd()
histos['h1_CTR'].Draw("PE")  
#f_gaus = TF1("f_gaus","gaus",histos['h1_CTR'].GetMean()-2*histos['h1_CTR'].GetRMS(),histos['h1_CTR'].GetMean()+2*histos['h1_CTR'].GetRMS())
#histos['h1_CTR'].Fit(f_gaus,"LR+0N","",histos['h1_CTR'].GetMean()-1*histos['h1_CTR'].GetRMS(),histos['h1_CTR'].GetMean()+1*histos['h1_CTR'].GetRMS())
#histos['h1_CTR'].Fit(f_gaus,"LR+","",f_gaus.GetParameter(1)-3.5*f_gaus.GetParameter(2),f_gaus.GetParameter(1)+3.5*f_gaus.GetParameter(2))
#fix fit range - Livia: changed from GetMean
f_gaus = TF1("f_gaus","gaus",histos['h1_CTR'].GetBinCenter(histos['h1_CTR'].GetMaximumBin())-550.,histos['h1_CTR'].GetBinCenter(histos['h1_CTR'].GetMaximumBin())+550.)
histos['h1_CTR'].Fit(f_gaus,"R+0N","",histos['h1_CTR'].GetBinCenter(histos['h1_CTR'].GetMaximumBin())-550.,histos['h1_CTR'].GetBinCenter(histos['h1_CTR'].GetMaximumBin())+550.)
histos['h1_CTR'].Fit(f_gaus,"R+","",f_gaus.GetParameter(1)-550.,f_gaus.GetParameter(1)+550.)

#f_gaus = TF1("f_gaus","gaus",histos['h1_CTR'].GetMean()-550.,histos['h1_CTR'].GetMean()+550.)
#histos['h1_CTR'].Fit(f_gaus,"R+0N","",histos['h1_CTR'].GetMean()-550.,histos['h1_CTR'].GetMean()+550.)
#histos['h1_CTR'].Fit(f_gaus,"R+","",f_gaus.GetParameter(1)-550.,f_gaus.GetParameter(1)+550.)


histos['h1_CTR'].GetXaxis().SetRangeUser(f_gaus.GetParameter(1)-550.,f_gaus.GetParameter(1)+550.)
histos['h1_CTR'].GetXaxis().SetTitle("t_{bar} - t_{pixel} [ps]")
histos['h1_CTR'].GetYaxis().SetTitle("Events")
histos['h1_CTR'].GetYaxis().SetTitleOffset(1.6)

fitResults[("barCoinc","CTR","mean","value")]=f_gaus.GetParameter(1)
fitResults[("barCoinc","CTR","mean","sigma")]=f_gaus.GetParError(1)
fitResults[("barCoinc","CTR","sigma","value")]=f_gaus.GetParameter(2)
fitResults[("barCoinc","CTR","sigma","sigma")]=f_gaus.GetParError(2)

pt3 = TPaveText(0.100223,0.915556,0.613586,0.967407,"brNDC")
text3 = pt3.AddText( "Run" + str(opt.run).zfill(6) + " BAR" + str(opt.barCode).zfill(6) )
pt3.SetFillColor(0)
pt3.Draw()
#FIXME: check why it does not show the label on the canvas!

tfileoutput.cd()
c1_CTR.cd()
c1_CTR.Update()
c1_CTR.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run).zfill(6)+"_BAR"+str(opt.barCode).zfill(6)+"_CTR"+".pdf")
c1_CTR.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run).zfill(6)+"_BAR"+str(opt.barCode).zfill(6)+"_CTR"+".png")
c1_CTR.Write()
histos['h1_CTR'].Write()

################################################
## 9) Write histograms
################################################

#Pedestals
h1_pedTotMean.Write()
h1_pedTotRms.Write()

for ch in channels:

    #pedestals
    histos_Ped1[ch].Write()
    histos_Ped2[ch].Write()
    histos_PedTot[ch].Write()
    print "--- Channel = "+str(ch).zfill(3)+" ---"

    for tac in range(0,4):
        print "====" 
        print "TacID ", tac 
        print "Pedestal1 "+str(mean_Ped1[(ch,tac)])+" "+str(rms_Ped1[(ch,tac)]) 
        print "Pedestal2 "+str(mean_Ped2[(ch,tac)])+" "+str(rms_Ped2[(ch,tac)]) 
        print "PedestalTot "+str(mean_PedTot[(ch,tac)])+" "+str(rms_PedTot[(ch,tac)]) 

#Pixel
print "--- Pixel ---"
print "Pixel Peak 1: "+str(fitResults[('pixel',"peak1","mean","value")])+" +/- "+str(fitResults[('pixel',"peak1","mean","sigma")]) 
print "Pixel Peak 2: "+str(fitResults[('pixel',"peak2","mean","value")])+" +/- "+str(fitResults[('pixel',"peak2","mean","sigma")]) 
print "Pixel Backpeak : "+str(fitResults[('pixel',"backpeak","mean","value")])+" +/- "+str(fitResults[('pixel',"backpeak","mean","sigma")]) 
print "Pixel Peak 1 Coinc: "+str(fitResults[('pixelCoinc',"peak1","mean","value")])+" +/- "+str(fitResults[('pixelCoinc',"peak1","mean","sigma")]) 
#print "Pixel Alpha: "+str(fitResults[('pixel',"peak12","alpha","value")])+" +/- "+str(fitResults[('pixel',"peak12","alpha","sigma")]) 
#print "Pixel Beta: "+str(fitResults[('pixel',"peak12","beta","value")])+" +/- "+str(fitResults[('pixel',"peak12","beta","sigma")]) 

#Bar
print "--- Bar ---"
print "Bar Peak 1: "+str(fitResults[('bar',"peak1","mean","value")])+" +/- "+str(fitResults[('bar',"peak1","mean","sigma")]) 
print "Bar Peak 2: "+str(fitResults[('bar',"peak2","mean","value")])+" +/- "+str(fitResults[('bar',"peak2","mean","sigma")]) 
print "Bar Backpeak : "+str(fitResults[('bar',"backpeak","mean","value")])+" +/- "+str(fitResults[('bar',"backpeak","mean","sigma")]) 
print "Bar Peak 1 Coinc: "+str(fitResults[('barCoinc',"peak1","mean","value")])+" +/- "+str(fitResults[('barCoinc',"peak1","mean","sigma")]) 
#print "Pixel Alpha: "+str(fitResults[('bar',"peak12","alpha","value")])+" +/- "+str(fitResults[('bar',"peak12","alpha","sigma")]) 
#print "Pixel Beta: "+str(fitResults[('bar',"peak12","beta","value")])+" +/- "+str(fitResults[('bar',"peak12","beta","sigma")]) 

#Bar+pixel
print "--- CTR ---"
print "CTR mean: "+str(fitResults[('barCoinc',"CTR","mean","value")])+" +/- "+str(fitResults[('barCoinc',"CTR","mean","sigma")]) 
print "CTR sigma: "+str(fitResults[('barCoinc',"CTR","sigma","value")])+" +/- "+str(fitResults[('barCoinc',"CTR","sigma","sigma")]) 

Temp_pixel = histos['h1_temp_pixel'].GetMean()
Temp_bar = histos['h1_temp_bar'].GetMean()
Temp_internal = histos['h1_temp_int'].GetMean()

tfileoutput.Close()
tfilePed1.cd()
tfilePed1.Close()
tfilePed2.cd()
tfilePed2.Close()

################################################
## 10) Write root tree with measurements
################################################

tfileoutputtree = TFile( opt.outputDir+"/"+"tree_Run"+run+"_BAR"+str(str(opt.barCode).zfill(6))+".root", "recreate" )
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
#alpha_pixel = array( 'd', [ -999. ] )
#err_alpha_pixel = array( 'd', [ -999. ] )
#beta_pixel = array( 'd', [ -999. ] )
#err_beta_pixel = array( 'd', [ -999. ] )
peak1_mean_pixelCoinc = array( 'd', [ -999. ] )
err_peak1_mean_pixelCoinc = array( 'd', [ -999. ] )
peak1_sigma_pixelCoinc = array( 'd', [ -999. ] )
err_peak1_sigma_pixelCoinc = array( 'd', [ -999. ] )
#
peak1_mean_bar = array( 'd', [ -999. ] )
err_peak1_mean_bar = array( 'd', [ -999. ] )
peak2_mean_bar = array( 'd', [ -999. ] )
err_peak2_mean_bar = array( 'd', [ -999. ] )
peak1_sigma_bar = array( 'd', [ -999. ] )
err_peak1_sigma_bar = array( 'd', [ -999. ] )
peak2_sigma_bar = array( 'd', [ -999. ] )
err_peak2_sigma_bar = array( 'd', [ -999. ] )
#alpha_bar = array( 'd', [ -999. ] )
#err_alpha_bar = array( 'd', [ -999. ] )
#beta_bar = array( 'd', [ -999. ] )
#err_beta_bar = array( 'd', [ -999. ] )
peak1_mean_barCoinc = array( 'd', [ -999. ] )
err_peak1_mean_barCoinc = array( 'd', [ -999. ] )
peak1_sigma_barCoinc = array( 'd', [ -999. ] )
err_peak1_sigma_barCoinc = array( 'd', [ -999. ] )
#
CTR_mean_barCoinc = array( 'd', [ -999. ] )
err_CTR_mean_barCoinc = array( 'd', [ -999. ] )
CTR_sigma_barCoinc = array( 'd', [ -999. ] )
err_CTR_sigma_barCoinc = array( 'd', [ -999. ] )
#
temp_pixel = array( 'd', [ -999. ] )
temp_bar = array( 'd', [ -999. ] )
temp_int = array( 'd', [ -999. ] )
pos_X = array( 'd', [ -999. ] )
pos_Y = array( 'd', [ -999. ] )
#
code_bar = array( 'i', [ -9 ] )
runNumber = array( 'i', [ -9 ] )

treeOutput.Branch( 'peak1_mean_pixel', peak1_mean_pixel, 'peak1_mean_pixel/D' )
treeOutput.Branch( 'err_peak1_mean_pixel', err_peak1_mean_pixel, 'err_peak1_mean_pixel/D' )
treeOutput.Branch( 'peak2_mean_pixel', peak2_mean_pixel, 'peak2_mean_pixel/D' )
treeOutput.Branch( 'err_peak2_mean_pixel', err_peak2_mean_pixel, 'err_peak2_mean_pixel/D' )
treeOutput.Branch( 'peak1_sigma_pixel', peak1_sigma_pixel, 'peak1_sigma_pixel/D' )
treeOutput.Branch( 'err_peak1_sigma_pixel', err_peak1_sigma_pixel, 'err_peak1_sigma_pixel/D' )
treeOutput.Branch( 'peak2_sigma_pixel', peak2_sigma_pixel, 'peak2_sigma_pixel/D' )
treeOutput.Branch( 'err_peak2_sigma_pixel', err_peak2_sigma_pixel, 'err_peak2_sigma_pixel/D' )
#treeOutput.Branch( 'alpha_pixel', alpha_pixel, 'alpha_pixel/D' )
#treeOutput.Branch( 'err_alpha_pixel', err_alpha_pixel, 'err_alpha_pixel/D' )
#treeOutput.Branch( 'beta_pixel', beta_pixel, 'beta_pixel/D' )
#treeOutput.Branch( 'err_beta_pixel', err_beta_pixel, 'err_beta_pixel/D' )
treeOutput.Branch( 'peak1_mean_pixelCoinc', peak1_mean_pixelCoinc, 'peak1_mean_pixelCoinc/D' )
treeOutput.Branch( 'err_peak1_mean_pixelCoinc', err_peak1_mean_pixelCoinc, 'err_peak1_mean_pixelCoinc/D' )
treeOutput.Branch( 'peak1_sigma_pixelCoinc', peak1_sigma_pixelCoinc, 'peak1_sigma_pixelCoinc/D' )
treeOutput.Branch( 'err_peak1_sigma_pixelCoinc', err_peak1_sigma_pixelCoinc, 'err_peak1_sigma_pixelCoinc/D' )
#
treeOutput.Branch( 'peak1_mean_bar', peak1_mean_bar, 'peak1_mean_bar/D' )
treeOutput.Branch( 'err_peak1_mean_bar', err_peak1_mean_bar, 'err_peak1_mean_bar/D' )
treeOutput.Branch( 'peak2_mean_bar', peak2_mean_bar, 'peak2_mean_bar/D' )
treeOutput.Branch( 'err_peak2_mean_bar', err_peak2_mean_bar, 'err_peak2_mean_bar/D' )
treeOutput.Branch( 'peak1_sigma_bar', peak1_sigma_bar, 'peak1_sigma_bar/D' )
treeOutput.Branch( 'err_peak1_sigma_bar', err_peak1_sigma_bar, 'err_peak1_sigma_bar/D' )
treeOutput.Branch( 'peak2_sigma_bar', peak2_sigma_bar, 'peak2_sigma_bar/D' )
treeOutput.Branch( 'err_peak2_sigma_bar', err_peak2_sigma_bar, 'err_peak2_sigma_bar/D' )
#treeOutput.Branch( 'alpha_bar', alpha_bar, 'alpha_bar/D' )
#treeOutput.Branch( 'err_alpha_bar', err_alpha_bar, 'err_alpha_bar/D' )
#treeOutput.Branch( 'beta_bar', beta_bar, 'beta_bar/D' )
#treeOutput.Branch( 'err_beta_bar', err_beta_bar, 'err_beta_bar/D' )
treeOutput.Branch( 'peak1_mean_barCoinc', peak1_mean_barCoinc, 'peak1_mean_barCoinc/D' )
treeOutput.Branch( 'err_peak1_mean_barCoinc', err_peak1_mean_barCoinc, 'err_peak1_mean_barCoinc/D' )
treeOutput.Branch( 'peak1_sigma_barCoinc', peak1_sigma_barCoinc, 'peak1_sigma_barCoinc/D' )
treeOutput.Branch( 'err_peak1_sigma_barCoinc', err_peak1_sigma_barCoinc, 'err_peak1_sigma_barCoinc/D' )
#
treeOutput.Branch( 'CTR_mean_barCoinc', CTR_mean_barCoinc, 'CTR_mean_barCoinc/D' )
treeOutput.Branch( 'err_CTR_mean_barCoinc', err_CTR_mean_barCoinc, 'err_CTR_mean_barCoinc/D' )
treeOutput.Branch( 'CTR_sigma_barCoinc', CTR_sigma_barCoinc, 'CTR_sigma_barCoinc/D' )
treeOutput.Branch( 'err_CTR_sigma_barCoinc', err_CTR_sigma_barCoinc, 'err_CTR_sigma_barCoinc/D' )
#
treeOutput.Branch( 'temp_pixel', temp_pixel, 'temp_pixel/D' )
treeOutput.Branch( 'temp_bar', temp_bar, 'temp_bar/D' )
treeOutput.Branch( 'temp_int', temp_int, 'temp_int/D' )
treeOutput.Branch( 'pos_X', pos_X, 'pos_X/D' )
treeOutput.Branch( 'pos_Y', pos_Y, 'pos_Y/D' )
#
treeOutput.Branch( 'code_bar', code_bar, 'code_bar/I' )
treeOutput.Branch( 'runNumber', runNumber, 'runNumber/I' )

peak1_mean_pixel[0] = fitResults[('pixel',"peak1","mean","value")]
err_peak1_mean_pixel[0] = fitResults[('pixel',"peak1","mean","sigma")]
peak2_mean_pixel[0] = fitResults[('pixel',"peak2","mean","value")]
err_peak2_mean_pixel[0] = fitResults[('pixel',"peak2","mean","sigma")]
peak1_sigma_pixel[0] = fitResults[('pixel',"peak1","sigma","value")]
err_peak1_sigma_pixel[0] = fitResults[('pixel',"peak1","sigma","sigma")]
peak2_sigma_pixel[0] = fitResults[('pixel',"peak2","sigma","value")]
err_peak2_sigma_pixel[0] = fitResults[('pixel',"peak2","sigma","sigma")]
#alpha_pixel[0] = fitResults[('pixel',"peak12","alpha","value")]
#err_alpha_pixel[0] = fitResults[('pixel',"peak12","alpha","sigma")]
#beta_pixel[0] = fitResults[('pixel',"peak12","beta","value")]
#err_beta_pixel[0] = fitResults[('pixel',"peak12","beta","sigma")]
peak1_mean_pixelCoinc[0] = fitResults[('pixelCoinc',"peak1","mean","value")]
err_peak1_mean_pixelCoinc[0] = fitResults[('pixelCoinc',"peak1","mean","sigma")]
peak1_sigma_pixelCoinc[0] = fitResults[('pixelCoinc',"peak1","sigma","value")]
err_peak1_sigma_pixelCoinc[0] = fitResults[('pixelCoinc',"peak1","sigma","sigma")]
#
peak1_mean_bar[0] = fitResults[('bar',"peak1","mean","value")]
err_peak1_mean_bar[0] = fitResults[('bar',"peak1","mean","sigma")]
peak2_mean_bar[0] = fitResults[('bar',"peak2","mean","value")]
err_peak2_mean_bar[0] = fitResults[('bar',"peak2","mean","sigma")]
peak1_sigma_bar[0] = fitResults[('bar',"peak1","sigma","value")]
err_peak1_sigma_bar[0] = fitResults[('bar',"peak1","sigma","sigma")]
peak2_sigma_bar[0] = fitResults[('bar',"peak2","sigma","value")]
err_peak2_sigma_bar[0] = fitResults[('bar',"peak2","sigma","sigma")]
#alpha_bar[0] = fitResults[('bar',"peak12","alpha","value")]
#err_alpha_bar[0] = fitResults[('bar',"peak12","alpha","sigma")]
#beta_bar[0] = fitResults[('bar',"peak12","beta","value")]
#err_beta_bar[0] = fitResults[('bar',"peak12","beta","sigma")]
peak1_mean_barCoinc[0] = fitResults[('barCoinc',"peak1","mean","value")]
err_peak1_mean_barCoinc[0] = fitResults[('barCoinc',"peak1","mean","sigma")]
peak1_sigma_barCoinc[0] = fitResults[('barCoinc',"peak1","sigma","value")]
err_peak1_sigma_barCoinc[0] = fitResults[('barCoinc',"peak1","sigma","sigma")]
#
CTR_mean_barCoinc[0] = fitResults[('barCoinc',"CTR","mean","value")]
err_CTR_mean_barCoinc[0] = fitResults[('barCoinc',"CTR","mean","sigma")]
CTR_sigma_barCoinc[0] = fitResults[('barCoinc',"CTR","sigma","value")]
err_CTR_sigma_barCoinc[0] = fitResults[('barCoinc',"CTR","sigma","sigma")]
#
temp_pixel[0] = Temp_pixel
temp_bar[0] = Temp_bar
temp_int[0] = Temp_internal
pos_X[0] = posX
pos_Y[0] = posY
#
runNumber[0] = int(opt.run)
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


