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

def crystalball(x, alpha, n, sigma, mean):
  if (sigma < 0.):
      return 0.
  z = (x - mean)/sigma;
  if (alpha < 0):
      z = -z;
  abs_alpha = abs(alpha);
  if (z  > - abs_alpha):
    return TMath.Exp(- 0.5 * z * z)
  else:
    nDivAlpha = n/abs_alpha
    AA =  TMath.Exp(-0.5*abs_alpha*abs_alpha)
    B = nDivAlpha -abs_alpha
    arg = nDivAlpha/(B-z)
    return AA * TMath.Power(arg,n)

def crystalball_function(x, p):
  return p[0] * crystalball(x[0], p[3], p[4], p[2], p[1])

def setParameters(function,Norm,Peak):

    ## Normalisation
    function.SetParameter(0,Norm)
    function.SetParLimits(0,0.,Norm*1000.)
    
    ## 1274 KeV compton 
    function.SetParameter(1,0.4)
    function.SetParLimits(1,0.1,1)
    function.SetParameter(2,1.9*Peak)
    function.SetParLimits(2,1.8*Peak,2.0*Peak)

    ## 1274 KeV "photo-electric" 
    function.SetParameter(3,1.)
    function.SetParLimits(3,0.2,5.)
    function.SetParameter(4,2.4*Peak)
    function.SetParLimits(4,2.2*Peak,2.65*Peak)
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
        histo.Fit(function.GetName(),"LR+0N","",xmin,min(peak*2.7,xmax))
        print function.GetChisquare(), function.GetNDF(), function.GetChisquare()/function.GetNDF()
        if abs(function.GetChisquare()/function.GetNDF()-previousChi2overNdf)<0.01*previousChi2overNdf:
            histo.Fit(function.GetName(),"LR+","",xmin,min(peak*2.7,xmax))
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

    f1_bkg = TF1("f1_bkg",function,xmin,min(peak*2.7,xmax),19)
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
    text1 = pt1.AddText( "Run" + str(run.zfill(6)) + " ARRAY" + str(code.zfill(6)) + " " + " " + label )
    pt1.SetFillColor(0)
    pt1.Draw()

    canvas.Update()
    canvas.SaveAs(outputDIR+"/"+"Run"+str(run.zfill(6))+"_ARRAY"+str(code.zfill(6))+"_SourceSpectrum_"+label+".pdf")
    canvas.SaveAs(outputDIR+"/"+"Run"+str(run.zfill(6))+"_ARRAY"+str(code.zfill(6))+"_SourceSpectrum_"+label+".png")
    canvas.Write()

def fitSpectrum_coinc(histo,function,xmin,xmax,canvas,fitres,label,code,barId,run,outputDIR):

    histo.GetXaxis().SetRange(40,100)
    spectrum = TSpectrum(10)
    nfound = spectrum.Search(histo , 2 ,"goff",0.3)
    xpeaks = spectrum.GetPositionX()
    posPeak = []
    for i in range(spectrum.GetNPeaks()):
        posPeak.append(xpeaks[i])
    posPeak.sort()
    peak  = posPeak[-1]
    print "peak positions:", posPeak
    print "peak, nfound, spectrum.GetNPeaks()", peak, nfound, spectrum.GetNPeaks() 

    #peak=histo.GetBinCenter(histo.GetMaximumBin())
    norm=float(histo.GetEntries())/float(histo.GetNbinsX())
    histo.GetXaxis().SetRangeUser(xmin,xmax)
    setParameters_coinc(function,norm,peak)

    #histo.SetTitle( "Run" + str(run.zfill(6)) + " " + label + str(code.zfill(6)) )
    histo.GetXaxis().SetTitle("QDC counts")
    histo.GetYaxis().SetTitle("Events")
    histo.GetYaxis().SetTitleOffset(1.6)
 
    canvas.cd()
    histo.Draw("PE")
    goodChi2 = 0.
    previousChi2overNdf = -99.
    while goodChi2==0.:
        histo.Fit(function.GetName(),"LR+0N","",xmin,min(peak*1.3,xmax))
        print function.GetChisquare(), function.GetNDF(), function.GetChisquare()/function.GetNDF()
        if abs(function.GetChisquare()/function.GetNDF()-previousChi2overNdf)<0.01*previousChi2overNdf:
            histo.Fit(function.GetName(),"LR+","",xmin,min(peak*1.3,xmax))
            canvas.Update()
            goodChi2 = 1.
        previousChi2overNdf = function.GetChisquare()/function.GetNDF()
    print function.GetChisquare(), function.GetNDF(), function.GetChisquare()/function.GetNDF()

    fitres[(label,"peak1","mean","value")]=function.GetParameter(7)
    fitres[(label,"peak1","mean","sigma")]=function.GetParError(7)
    fitres[(label,"peak1","sigma","value")]=function.GetParameter(8)
    fitres[(label,"peak1","sigma","sigma")]=function.GetParError(8)

    f1_bkg = TF1("f1_bkg",function,xmin,min(peak*1.3,xmax),10)
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
    text2 = pt2.AddText( "Run" + str(run.zfill(6)) + " ARRAY" + str(code.zfill(6)) + " " + "BAR" + str(barId) + " " + label )
    pt2.SetFillColor(0)
    pt2.Draw()

    canvas.Update()
    canvas.SaveAs(outputDIR+"/"+"Run"+str(run.zfill(6))+"_ARRAY"+str(code.zfill(6))+"_BAR"+str(barId)+"_SourceSpectrum_"+label+".pdf")
    canvas.SaveAs(outputDIR+"/"+"Run"+str(run.zfill(6))+"_ARRAY"+str(code.zfill(6))+"_BAR"+str(barId)+"_SourceSpectrum_"+label+".png")
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

#################
## Bar+Array ##
#################
channels = [59,35,282,272,270,262,267,257,265,260,286,285,271,279,273,284,274,281,307,289,300,290,292,304,302,310,317,319,318,316,295,297,301,311]
############### (It should match the sequence of channels in the configuration file. The value reported in this list is NCHIP*64+NCH)

usage = "usage: python analysis/analyze_run_array_with_barRef.py --run 5 -i /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/output/TestArray -o /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/output/TestArray/RESULTS --arrayCode 0"

parser = optparse.OptionParser(usage)

parser.add_option("-r", "--run", dest="run",
                  help="run number")

parser.add_option("-i", "--input", dest="inputDir",default="/data/TOFPET/LYSOARRAYS",
                  help="input directory")

parser.add_option("-o", "--output", dest="outputDir",default="/data/TOFPET/LYSOARRAYS/RESULTS",
                  help="output directory")

parser.add_option("-b", "--arrayCode", dest="arrayCode", default=-99,
                  help="code of the crystal array")

(opt, args) = parser.parse_args()

if not opt.run:   
    parser.error('run number not provided')

if not opt.inputDir:   
    parser.error('input directory not provided')

if not opt.outputDir:   
    parser.error('output directory not provided')

#if not opt.arrayCode:   
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

run = opt.run.zfill(6)
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

#alignedBar = int(((input_filename_coinc.split("_POS")[1]).split("_"))[0])
#if not (alignedBar >-1 and alignedBar<16):
#    parser.error('Info on which bar is aligned with the pixel/source not found in the input filename')
#else:
#    print "Bar aligned with radioactive source and pixel: ", alignedBar

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

commandOutputDir = "mkdir -p "+opt.outputDir
print commandOutputDir
os.system(commandOutputDir)

################################################
## 2) Analyze pedestals
################################################

print "Analyzing pedestals"

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

pedoutput = TFile( opt.outputDir+"/"+"ped_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root", "recreate" )
pedoutput.cd()
h1_pedTotMean.Write()
h1_pedTotRms.Write()
pedoutput.Close()

print "Pedestals analyzed"

################################################
## 3) Analyze singles
################################################

'''
print "Analzying singles"

gROOT.ProcessLine('o = TString(gSystem->GetMakeSharedLib()); o = o.ReplaceAll(" -c ", " -std=c++11 -c "); gSystem->SetMakeSharedLib(o.Data());')
gROOT.ProcessLine(".L /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis/singleAnalysis.C+")
gROOT.ProcessLine('TFile* f = new TFile("%s");'%input_filename_singles)
gROOT.ProcessLine('TTree* tree; f->GetObject("data",tree);')
gROOT.ProcessLine("singleAnalysis sAnalysis(tree);")
gROOT.ProcessLine('sAnalysis.LoadPedestals("%s");'%(opt.outputDir+"/"+"ped_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root"))
gROOT.ProcessLine('sAnalysis.pixelChId=%d;'%channels[0])
gROOT.ProcessLine('sAnalysis.outputFile="%s";'%(opt.outputDir+"/"+"histo_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root"))
gBenchmark.Start( 'singleAnalysis' )
gROOT.ProcessLine("sAnalysis.Loop();")
gBenchmark.Show( 'singleAnalysis' )

print "Singles analyzed"
'''

################################################
## 4) Analyze coincidences
################################################

print "Analyzing coincidences"

gROOT.ProcessLine('o = TString(gSystem->GetMakeSharedLib()); o = o.ReplaceAll(" -c ", " -std=c++11 -c "); gSystem->SetMakeSharedLib(o.Data());')
gROOT.ProcessLine(".L /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis/coincidenceAnalysisWithBarRef.C+")
gROOT.ProcessLine('TFile* f = new TFile("%s");'%input_filename_coinc)
gROOT.ProcessLine('TTree* tree; f->GetObject("data",tree);')
gROOT.ProcessLine("coincidenceAnalysisWithBarRef cAnalysis(tree);")
gROOT.ProcessLine('cAnalysis.LoadPedestals("%s");'%(opt.outputDir+"/"+"ped_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root"))
gROOT.ProcessLine('cAnalysis.outputFile="%s";'%(opt.outputDir+"/"+"histo_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root"))
gBenchmark.Start( 'coincidenceAnalysisWithBarRef' )
gROOT.ProcessLine("cAnalysis.Loop();")
gBenchmark.Show( 'coincidenceAnalysisWithBarRef' )

print "Coincidences analyzed"

################################################
## 5) Output file
################################################

tfileoutput = TFile( opt.outputDir+"/"+"histo_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root", "update" )
tfileoutput.cd()
histos=Map(tfileoutput)

'''
if (histos['h1_energy_pixel'].GetEntries()<50):
    print "ERROR: Too few events ("+ str(histos['h1_energy_pixel'].GetEntries()) +") in histogram "+histos['h1_energy_pixel'].GetName()
    print "Exiting..."
    sys.exit()

if (histos['h1_energy_pixel_coinc%d'%alignedBar].GetEntries()<50):
    print "ERROR: Too few events ("+ str(histos['h1_energy_pixel_coinc%d'%alignedBar].GetEntries()) +") in histogram "+histos['h1_energy_pixel_coinc%d'%alignedBar].GetName()
    print "Exiting..."
    sys.exit()

if (histos['h1_energyTot_bar_coinc%d'%alignedBar].GetEntries()<50):
    print "ERROR: Too few events ("+ str(histos['h1_energyTot_bar_coinc%d'%alignedBar].GetEntries()) +") in histogram "+histos['h1_energyTot_bar_coinc%d'%alignedBar].GetName()
    print "Exiting..."
    sys.exit()
'''

################################################
## 6) Fit energy spectra
################################################
c1_energy = TCanvas("c1_energy_barRef", "", 900, 700)

fitResults = {}

## Setup singles
minEnergy = 15
maxEnergy = 250
n_paramameters = 19

## BarRef
fTot_barRef = TF1("fTot_barRef",totalFunction,minEnergy,maxEnergy,n_paramameters)
fTot_barRef.SetNpx(1000)
fitSpectrum(histos['h1_energyTot_barRef'],fTot_barRef,minEnergy,maxEnergy,c1_energy,fitResults,"barRef",opt.arrayCode,opt.run,opt.outputDir)

histos['h1_energyTot_barRef'].Write()
'''
## Bar
fTot_bar = TF1("fTot_bar",totalFunction,minEnergy,maxEnergy,n_paramameters)
fTot_bar.SetNpx(1000)
fitSpectrum(h1_energyTot_bar,fTot_bar,minEnergy,maxEnergy,c1_energyTot_bar,fitResults,"bar",opt.arrayCode,alignedBar,opt.run,opt.outputDir)
'''

## Setup coincidences
n_paramameters_coinc = 10
minEnergy_coinc = 15
maxEnergy_coinc = 180

## Bars in array
dead_channels = []

fTot_bar_coinc = TF1("fTot_bar_coinc",totalFunction_coinc,minEnergy_coinc,maxEnergy_coinc,n_paramameters_coinc)
fTot_bar_coinc.SetNpx(1000)

for barId in range(0,16):

    if (histos['h1_energyTot_bar_coinc%d'%barId].GetEntries()<50):
        print "ERROR: Too few events ("+ str(histos['h1_energyTot_bar_coinc%d'%barId].GetEntries()) +") in histogram "+histos['h1_energyTot_bar_coinc%d'%barId].GetName()
        print "Skip bar..."
        dead_channels.append(barId)
        continue
    
    fitSpectrum_coinc(histos['h1_energyTot_bar_coinc%d'%barId],fTot_bar_coinc,minEnergy_coinc,maxEnergy_coinc,c1_energy,fitResults,'barCoinc%d'%barId,opt.arrayCode,barId,opt.run,opt.outputDir)
    histos['h1_energyTot_bar_coinc%d'%barId].Write()

tfileoutput.Close()

print "List of bars with at least one dead channel", dead_channels

######################################################
## 7) Coincidence time resolution (CTR) and cross-talk
######################################################

gROOT.ProcessLine(".L /home/cmsdaq/Workspace/TOFPET/Timing-TOFPET/analysis/ctrAnalysisWithBarRef.C+")
gROOT.ProcessLine('TFile* f = new TFile("%s");'%input_filename_coinc)
gROOT.ProcessLine('TTree* tree; f->GetObject("data",tree);')
gROOT.ProcessLine("ctrAnalysisWithBarRef ctrAnalysis(tree);")

gROOT.ProcessLine('ctrAnalysis.LoadPedestals("%s");'%(opt.outputDir+"/"+"ped_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root"))
gROOT.ProcessLine('ctrAnalysis.outputFile="%s";'%(opt.outputDir+"/"+"histo_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root"))
gROOT.ProcessLine('ctrAnalysis.barRef_511Peak_mean=%f;'%fitResults[('barRef',"peak1","mean","value")])
gROOT.ProcessLine('ctrAnalysis.barRef_511Peak_sigma=%f;'%fitResults[('barRef',"peak1","sigma","value")])

for barId in range(0,16):

    if barId in dead_channels:
        gROOT.ProcessLine('ctrAnalysis.alignedBar_511Peak_mean.push_back(-9);')
        gROOT.ProcessLine('ctrAnalysis.alignedBar_511Peak_sigma.push_back(-9);')
        continue

    print "barId%d -- Cuts for CTR calculation:"%barId
    print fitResults[('barRef',"peak1","mean","value")] - fitResults[('barRef',"peak1","sigma","value")]
    print fitResults[('barRef',"peak1","mean","value")] + fitResults[('barRef',"peak1","sigma","value")]
    print fitResults[('barCoinc%d'%barId,"peak1","mean","value")] - fitResults[('barCoinc%d'%barId,"peak1","sigma","value")]
    print fitResults[('barCoinc%d'%barId,"peak1","mean","value")] + fitResults[('barCoinc%d'%barId,"peak1","sigma","value")]
    print "mean, sigma: ", fitResults[('barCoinc%d'%barId,"peak1","mean","value")], fitResults[('barCoinc%d'%barId,"peak1","sigma","value")]
    gROOT.ProcessLine('ctrAnalysis.alignedBar_511Peak_mean.push_back(%f);'%fitResults[('barCoinc%d'%barId,"peak1","mean","value")])
    gROOT.ProcessLine('ctrAnalysis.alignedBar_511Peak_sigma.push_back(%f);'%fitResults[('barCoinc%d'%barId,"peak1","sigma","value")])

gBenchmark.Start( 'ctrAnalysisWithBarRef' )
gROOT.ProcessLine("ctrAnalysis.Loop();")
gBenchmark.Show( 'ctrAnalysisWithBarRef' )

sys.exit()

##CTR
tfileoutput = TFile( opt.outputDir+"/"+"histo_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root", "update" )
tfileoutput.cd()
histos=Map(tfileoutput)

#print histos

c1_energy.cd()

histos['h1_CTR'].Draw("PE")  
#f_gaus = TF1("f_gaus","gaus",histos['h1_CTR'].GetMean()-2*histos['h1_CTR'].GetRMS(),histos['h1_CTR'].GetMean()+2*histos['h1_CTR'].GetRMS())
#histos['h1_CTR'].Fit(f_gaus,"LR+0N","",histos['h1_CTR'].GetMean()-1*histos['h1_CTR'].GetRMS(),histos['h1_CTR'].GetMean()+1*histos['h1_CTR'].GetRMS())
#histos['h1_CTR'].Fit(f_gaus,"LR+","",f_gaus.GetParameter(1)-3.5*f_gaus.GetParameter(2),f_gaus.GetParameter(1)+3.5*f_gaus.GetParameter(2))
f_gaus = TF1("f_gaus","gaus",histos['h1_CTR'].GetBinCenter(histos['h1_CTR'].GetMaximumBin())-550.,histos['h1_CTR'].GetBinCenter(histos['h1_CTR'].GetMaximumBin())+550.)
histos['h1_CTR'].Fit(f_gaus,"R+0N","",histos['h1_CTR'].GetBinCenter(histos['h1_CTR'].GetMaximumBin())-550.,histos['h1_CTR'].GetBinCenter(histos['h1_CTR'].GetMaximumBin())+550.)
#f_gaus = TF1("f_gaus","gaus",histos['h1_CTR'].GetMean()-550.,histos['h1_CTR'].GetMean()+550.)
#histos['h1_CTR'].Fit(f_gaus,"R+0N","",histos['h1_CTR'].GetMean()-550.,histos['h1_CTR'].GetMean()+550.)


histos['h1_CTR'].Fit(f_gaus,"R+","",f_gaus.GetParameter(1)-550.,f_gaus.GetParameter(1)+550.)
histos['h1_CTR'].GetXaxis().SetRangeUser(f_gaus.GetParameter(1)-550.,f_gaus.GetParameter(1)+550.)
histos['h1_CTR'].GetXaxis().SetTitle("t_{bar} - t_{pixel} [ps]")
histos['h1_CTR'].GetYaxis().SetTitle("Events")
histos['h1_CTR'].GetYaxis().SetTitleOffset(1.6)

fitResults[("barCoinc","CTR","mean","value")]=f_gaus.GetParameter(1)
fitResults[("barCoinc","CTR","mean","sigma")]=f_gaus.GetParError(1)
fitResults[("barCoinc","CTR","sigma","value")]=f_gaus.GetParameter(2)
fitResults[("barCoinc","CTR","sigma","sigma")]=f_gaus.GetParError(2)

pt3 = TPaveText(0.100223,0.915556,0.613586,0.967407,"brNDC")
text3 = pt3.AddText( "Run" + str(opt.run.zfill(6)) + " ARRAY" + str(opt.arrayCode.zfill(6)) + " BAR"+str(alignedBar))
pt3.SetFillColor(0)
pt3.Draw()
#FIXME: check why it does not show the label on the canvas!
c1_energy.cd()
c1_energy.Update()
c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(alignedBar)+"_CTR"+".pdf")
c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(alignedBar)+"_CTR"+".png")
c1_energy.Write()
histos['h1_CTR'].Write()

histos['h1_energySum_Xtalk'].Draw("PE") 
f_cb=TF1("f_cb",crystalball_function,-10,100,5)
f_cb.SetParameter(0,100)
f_cb.SetParameter(1,5)
f_cb.SetParameter(2,2)
f_cb.FixParameter(3,-2)
f_cb.SetParameter(4,20)

histos['h1_energySum_Xtalk'].Fit(f_cb,"R+","",0,50)
histos['h1_energySum_Xtalk'].GetXaxis().SetRangeUser(-10,50)
histos['h1_energySum_Xtalk'].GetXaxis().SetTitle("Energy Lateral (Left + Right)")
histos['h1_energySum_Xtalk'].GetYaxis().SetTitle("Events")
histos['h1_energySum_Xtalk'].GetYaxis().SetTitleOffset(1.6)

fitResults[("barCoinc","Xtalk","mean","value")]=f_cb.GetParameter(1)
fitResults[("barCoinc","Xtalk","mean","sigma")]=f_cb.GetParError(1)
fitResults[("barCoinc","Xtalk","sigma","value")]=f_cb.GetParameter(2)
fitResults[("barCoinc","Xtalk","sigma","sigma")]=f_cb.GetParError(2)
fitResults[("barCoinc","Xtalk","ChiSquareOverNdf","value")]=f_cb.GetChisquare()/f_cb.GetNDF()
fitResults[("barCoinc","Xtalk","probChiSquare","value")]=f_cb.GetProb()

fitResults[("barCoinc","Xtalk","average","value")]=histos['h1_energySum_Xtalk'].GetMean()
fitResults[("barCoinc","Xtalk","RMS","value")]=histos['h1_energySum_Xtalk'].GetRMS()

fitResults[("barCoinc","XtalkNhits","average","value")]=histos['h1_nhits_Xtalk'].GetMean()
fitResults[("barCoinc","XtalkNhits","RMS","value")]=histos['h1_nhits_Xtalk'].GetRMS()
fitResults[("barCoinc","XtalkNbars","average","value")]=histos['h1_nbars_Xtalk'].GetMean()
fitResults[("barCoinc","XtalkNbars","RMS","value")]=histos['h1_nbars_Xtalk'].GetRMS()

pt3.Draw()

c1_energy.cd()
c1_energy.Update()
c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(alignedBar)+"_Xtalk"+".pdf")
c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(alignedBar)+"_Xtalk"+".png")
c1_energy.Write()
histos['h1_energySum_Xtalk'].Write()

if (alignedBar-1>=0):
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].Draw("PE") 
    f_cb_Left=TF1("f_cb_Left",crystalball_function,-10,100,5)
    f_cb_Left.SetParameter(0,100)
    f_cb_Left.SetParameter(1,5)
    f_cb_Left.SetParameter(2,2)
    f_cb_Left.FixParameter(3,-2)
    f_cb_Left.SetParameter(4,20)

    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].Fit(f_cb_Left,"R+","",0,50)
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].GetXaxis().SetRangeUser(-10,50)
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].GetXaxis().SetTitle("Energy Left")
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].GetYaxis().SetTitle("Events")
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].GetYaxis().SetTitleOffset(1.6)

    fitResults[("barCoinc","XtalkLeft","mean","value")]=f_cb_Left.GetParameter(1)
    fitResults[("barCoinc","XtalkLeft","mean","sigma")]=f_cb_Left.GetParError(1)
    fitResults[("barCoinc","XtalkLeft","sigma","value")]=f_cb_Left.GetParameter(2)
    fitResults[("barCoinc","XtalkLeft","sigma","sigma")]=f_cb_Left.GetParError(2)
    fitResults[("barCoinc","XtalkLeft","ChiSquareOverNdf","value")]=f_cb_Left.GetChisquare()/f_cb_Left.GetNDF()
    fitResults[("barCoinc","XtalkLeft","probChiSquare","value")]=f_cb_Left.GetProb()

    fitResults[("barCoinc","XtalkLeft","average","value")]=histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].GetMean()
    fitResults[("barCoinc","XtalkLeft","RMS","value")]=histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].GetRMS()

    pt3.Draw()

    c1_energy.cd()
    c1_energy.Update()
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(alignedBar)+"_XtalkLeft"+".pdf")
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(alignedBar)+"_XtalkLeft"+".png")
    c1_energy.Write()
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar-1)].Write()
else:
    fitResults[("barCoinc","XtalkLeft","mean","value")]=-1
    fitResults[("barCoinc","XtalkLeft","mean","sigma")]=-1
    fitResults[("barCoinc","XtalkLeft","sigma","value")]=-1
    fitResults[("barCoinc","XtalkLeft","sigma","sigma")]=-1
    fitResults[("barCoinc","XtalkLeft","ChiSquareOverNdf","value")]=-1
    fitResults[("barCoinc","XtalkLeft","probChiSquare","value")]=-1

    fitResults[("barCoinc","XtalkLeft","average","value")]=-1
    fitResults[("barCoinc","XtalkLeft","RMS","value")]=-1
    
if (alignedBar+1<16):
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].Draw("PE") 
    f_cb_Right=TF1("f_cb_Right",crystalball_function,-10,100,5)
    f_cb_Right.SetParameter(0,100)
    f_cb_Right.SetParameter(1,5)
    f_cb_Right.SetParameter(2,2)
    f_cb_Right.FixParameter(3,-2)
    f_cb_Right.SetParameter(4,20)

    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].Fit(f_cb_Right,"R+","",0,50)
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].GetXaxis().SetRangeUser(-10,50)
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].GetXaxis().SetTitle("Energy Right")
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].GetYaxis().SetTitle("Events")
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].GetYaxis().SetTitleOffset(1.6)

    fitResults[("barCoinc","XtalkRight","mean","value")]=f_cb_Right.GetParameter(1)
    fitResults[("barCoinc","XtalkRight","mean","sigma")]=f_cb_Right.GetParError(1)
    fitResults[("barCoinc","XtalkRight","sigma","value")]=f_cb_Right.GetParameter(2)
    fitResults[("barCoinc","XtalkRight","sigma","sigma")]=f_cb_Right.GetParError(2)
    fitResults[("barCoinc","XtalkRight","ChiSquareOverNdf","value")]=f_cb_Right.GetChisquare()/f_cb_Right.GetNDF()
    fitResults[("barCoinc","XtalkRight","probChiSquare","value")]=f_cb_Right.GetProb()

    fitResults[("barCoinc","XtalkRight","average","value")]=histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].GetMean()
    fitResults[("barCoinc","XtalkRight","RMS","value")]=histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].GetRMS()

    pt3.Draw()

    c1_energy.cd()
    c1_energy.Update()
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(alignedBar)+"_XtalkRight"+".pdf")
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(alignedBar)+"_XtalkRight"+".png")
    c1_energy.Write()
    histos['h1_energyTot_bar_Xtalk%d'%(alignedBar+1)].Write()
else:
    fitResults[("barCoinc","XtalkRight","mean","value")]=-1
    fitResults[("barCoinc","XtalkRight","mean","sigma")]=-1
    fitResults[("barCoinc","XtalkRight","sigma","value")]=-1
    fitResults[("barCoinc","XtalkRight","sigma","sigma")]=-1
    fitResults[("barCoinc","XtalkRight","ChiSquareOverNdf","value")]=-1
    fitResults[("barCoinc","XtalkRight","probChiSquare","value")]=-1

    fitResults[("barCoinc","XtalkRight","average","value")]=-1
    fitResults[("barCoinc","XtalkRight","RMS","value")]=-1

###XTALK 
#if(alignedBar>0 and alignedBar<7):
#    e_1 = h1_energyTot_bar_Xtalk[ibar]
#    e_2 = 

################################################
## 8) Write additional histograms
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

print "--- Bar ---"
#print "Bar Peak 1: "+str(fitResults[('bar',"peak1","mean","value")])+" +/- "+str(fitResults[('bar',"peak1","mean","sigma")]) 
#print "Bar Peak 2: "+str(fitResults[('bar',"peak2","mean","value")])+" +/- "+str(fitResults[('bar',"peak2","mean","sigma")]) 
#print "Bar Backpeak : "+str(fitResults[('bar',"backpeak","mean","value")])+" +/- "+str(fitResults[('bar',"backpeak","mean","sigma")]) 
print "Bar Peak 1 Coinc: "+str(fitResults[('barCoinc',"peak1","mean","value")])+" +/- "+str(fitResults[('barCoinc',"peak1","mean","sigma")]) 
#print "Pixel Alpha: "+str(fitResults[('bar',"peak12","alpha","value")])+" +/- "+str(fitResults[('bar',"peak12","alpha","sigma")]) 
#print "Pixel Beta: "+str(fitResults[('bar',"peak12","beta","value")])+" +/- "+str(fitResults[('bar',"peak12","beta","sigma")]) 

print "--- CTR ---"
print "CTR mean: "+str(fitResults[('barCoinc',"CTR","mean","value")])+" +/- "+str(fitResults[('barCoinc',"CTR","mean","sigma")]) 
print "CTR sigma: "+str(fitResults[('barCoinc',"CTR","sigma","value")])+" +/- "+str(fitResults[('barCoinc',"CTR","sigma","sigma")]) 

print "--- Xtalk ---"
print "Xtalk mean: "+str(fitResults[('barCoinc',"Xtalk","mean","value")])+" +/- "+str(fitResults[('barCoinc',"Xtalk","mean","sigma")]) 
print "Xtalk sigma: "+str(fitResults[('barCoinc',"Xtalk","sigma","value")])+" +/- "+str(fitResults[('barCoinc',"Xtalk","sigma","sigma")]) 
print "Xtalk ChiSquareOverNdf / probChiSquare: "+str(fitResults[('barCoinc',"Xtalk","ChiSquareOverNdf","value")])+" / "+str(fitResults[('barCoinc',"Xtalk","probChiSquare","value")]) 
print "Xtalk average / RMS: "+str(fitResults[('barCoinc',"Xtalk","average","value")])+" / "+str(fitResults[('barCoinc',"Xtalk","RMS","value")]) 
print "XtalkNhits average / RMS: "+str(fitResults[('barCoinc',"XtalkNhits","average","value")])+" / "+str(fitResults[('barCoinc',"XtalkNhits","RMS","value")]) 
print "XtalkNbars average / RMS: "+str(fitResults[('barCoinc',"XtalkNbars","average","value")])+" / "+str(fitResults[('barCoinc',"XtalkNbars","RMS","value")]) 

print "--- Xtalk Left ---"
print "XtalkLeft mean: "+str(fitResults[('barCoinc',"XtalkLeft","mean","value")])+" +/- "+str(fitResults[('barCoinc',"XtalkLeft","mean","sigma")]) 
print "XtalkLeft sigma: "+str(fitResults[('barCoinc',"XtalkLeft","sigma","value")])+" +/- "+str(fitResults[('barCoinc',"XtalkLeft","sigma","sigma")]) 
print "XtalkLeft ChiSquareOverNdf / probChiSquare: "+str(fitResults[('barCoinc',"XtalkLeft","ChiSquareOverNdf","value")])+" / "+str(fitResults[('barCoinc',"XtalkLeft","probChiSquare","value")]) 
print "XtalkLeft average / RMS: "+str(fitResults[('barCoinc',"XtalkLeft","average","value")])+" / "+str(fitResults[('barCoinc',"XtalkLeft","RMS","value")]) 

print "--- Xtalk Right ---"
print "XtalkRight mean: "+str(fitResults[('barCoinc',"XtalkRight","mean","value")])+" +/- "+str(fitResults[('barCoinc',"XtalkRight","mean","sigma")]) 
print "XtalkRight sigma: "+str(fitResults[('barCoinc',"XtalkRight","sigma","value")])+" +/- "+str(fitResults[('barCoinc',"XtalkRight","sigma","sigma")]) 
print "XtalkRight ChiSquareOverNdf / probChiSquare: "+str(fitResults[('barCoinc',"XtalkRight","ChiSquareOverNdf","value")])+" / "+str(fitResults[('barCoinc',"XtalkRight","probChiSquare","value")]) 
print "XtalkRight average / RMS: "+str(fitResults[('barCoinc',"XtalkRight","average","value")])+" / "+str(fitResults[('barCoinc',"XtalkRight","RMS","value")]) 

Temp_pixel = histos['h1_temp_pixel'].GetMean()
Temp_bar = histos['h1_temp_bar'].GetMean()
Temp_internal = histos['h1_temp_int'].GetMean()

tfileoutput.Close()
tfilePed1.cd()
tfilePed1.Close()
tfilePed2.cd()
tfilePed2.Close()

################################################
## 9) Write root tree with measurements
################################################

tfileoutputtree = TFile( opt.outputDir+"/"+"tree_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+"_BAR"+str(alignedBar)+".root", "recreate" )
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
alpha_bar = array( 'd', [ -999. ] )
err_alpha_bar = array( 'd', [ -999. ] )
beta_bar = array( 'd', [ -999. ] )
err_beta_bar = array( 'd', [ -999. ] )
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
Xtalk_mean_barCoinc = array( 'd', [ -999. ] )
err_Xtalk_mean_barCoinc = array( 'd', [ -999. ] )
Xtalk_sigma_barCoinc = array( 'd', [ -999. ] )
err_Xtalk_sigma_barCoinc = array( 'd', [ -999. ] )
Xtalk_ChiSquareOverNdf_barCoinc = array( 'd', [ -999. ] )
Xtalk_probChiSquare_barCoinc = array( 'd', [ -999. ] )
Xtalk_average_barCoinc = array( 'd', [ -999. ] )
Xtalk_RMS_barCoinc = array( 'd', [ -999. ] )
#
XtalkNhits_average_barCoinc = array( 'd', [ -999. ] )
XtalkNhits_RMS_barCoinc = array( 'd', [ -999. ] )
XtalkNbars_average_barCoinc = array( 'd', [ -999. ] )
XtalkNbars_RMS_barCoinc = array( 'd', [ -999. ] )
#
XtalkLeft_mean_barCoinc = array( 'd', [ -999. ] )
err_XtalkLeft_mean_barCoinc = array( 'd', [ -999. ] )
XtalkLeft_sigma_barCoinc = array( 'd', [ -999. ] )
err_XtalkLeft_sigma_barCoinc = array( 'd', [ -999. ] )
XtalkLeft_ChiSquareOverNdf_barCoinc = array( 'd', [ -999. ] )
XtalkLeft_probChiSquare_barCoinc = array( 'd', [ -999. ] )
XtalkLeft_average_barCoinc = array( 'd', [ -999. ] )
XtalkLeft_RMS_barCoinc = array( 'd', [ -999. ] )
#
XtalkRight_mean_barCoinc = array( 'd', [ -999. ] )
err_XtalkRight_mean_barCoinc = array( 'd', [ -999. ] )
XtalkRight_sigma_barCoinc = array( 'd', [ -999. ] )
err_XtalkRight_sigma_barCoinc = array( 'd', [ -999. ] )
XtalkRight_ChiSquareOverNdf_barCoinc = array( 'd', [ -999. ] )
XtalkRight_probChiSquare_barCoinc = array( 'd', [ -999. ] )
XtalkRight_average_barCoinc = array( 'd', [ -999. ] )
XtalkRight_RMS_barCoinc = array( 'd', [ -999. ] )
#
temp_pixel = array( 'd', [ -999. ] )
temp_bar = array( 'd', [ -999. ] )
temp_int = array( 'd', [ -999. ] )
pos_X = array( 'd', [ -999. ] )
pos_Y = array( 'd', [ -999. ] )
#
bar = array( 'i', [ -9 ] )
code_array = array( 'i', [ -9 ] )
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
#treeOutput.Branch( 'peak1_mean_bar', peak1_mean_bar, 'peak1_mean_bar/D' )
#treeOutput.Branch( 'err_peak1_mean_bar', err_peak1_mean_bar, 'err_peak1_mean_bar/D' )
#treeOutput.Branch( 'peak2_mean_bar', peak2_mean_bar, 'peak2_mean_bar/D' )
#treeOutput.Branch( 'err_peak2_mean_bar', err_peak2_mean_bar, 'err_peak2_mean_bar/D' )
#treeOutput.Branch( 'peak1_sigma_bar', peak1_sigma_bar, 'peak1_sigma_bar/D' )
#treeOutput.Branch( 'err_peak1_sigma_bar', err_peak1_sigma_bar, 'err_peak1_sigma_bar/D' )
#treeOutput.Branch( 'peak2_sigma_bar', peak2_sigma_bar, 'peak2_sigma_bar/D' )
#treeOutput.Branch( 'err_peak2_sigma_bar', err_peak2_sigma_bar, 'err_peak2_sigma_bar/D' )
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
treeOutput.Branch( 'Xtalk_mean_barCoinc', Xtalk_mean_barCoinc, 'Xtalk_mean_barCoinc/D' )
treeOutput.Branch( 'err_Xtalk_mean_barCoinc', err_Xtalk_mean_barCoinc, 'err_Xtalk_mean_barCoinc/D' )
treeOutput.Branch( 'Xtalk_sigma_barCoinc', Xtalk_sigma_barCoinc, 'Xtalk_sigma_barCoinc/D' )
treeOutput.Branch( 'err_Xtalk_sigma_barCoinc', err_Xtalk_sigma_barCoinc, 'err_Xtalk_sigma_barCoinc/D' )
treeOutput.Branch( 'Xtalk_ChiSquareOverNdf_barCoinc', Xtalk_ChiSquareOverNdf_barCoinc, 'Xtalk_ChiSquareOverNdf_barCoinc/D' )
treeOutput.Branch( 'Xtalk_probChiSquare_barCoinc', Xtalk_probChiSquare_barCoinc, 'Xtalk_probChiSquare_barCoinc/D' )
treeOutput.Branch( 'Xtalk_average_barCoinc', Xtalk_average_barCoinc, 'Xtalk_average_barCoinc/D' )
treeOutput.Branch( 'Xtalk_RMS_barCoinc', Xtalk_RMS_barCoinc, 'Xtalk_RMS_barCoinc/D' )
#
treeOutput.Branch( 'XtalkNhits_average_barCoinc', XtalkNhits_average_barCoinc, 'XtalkNhits_average_barCoinc/D' )
treeOutput.Branch( 'XtalkNhits_RMS_barCoinc', XtalkNhits_RMS_barCoinc, 'XtalkNhits_RMS_barCoinc/D' )
treeOutput.Branch( 'XtalkNbars_average_barCoinc', XtalkNbars_average_barCoinc, 'XtalkNbars_average_barCoinc/D' )
treeOutput.Branch( 'XtalkNbars_RMS_barCoinc', XtalkNbars_RMS_barCoinc, 'XtalkNbars_RMS_barCoinc/D' )
#
treeOutput.Branch( 'XtalkLeft_mean_barCoinc', XtalkLeft_mean_barCoinc, 'XtalkLeft_mean_barCoinc/D' )
treeOutput.Branch( 'err_XtalkLeft_mean_barCoinc', err_XtalkLeft_mean_barCoinc, 'err_XtalkLeft_mean_barCoinc/D' )
treeOutput.Branch( 'XtalkLeft_sigma_barCoinc', XtalkLeft_sigma_barCoinc, 'XtalkLeft_sigma_barCoinc/D' )
treeOutput.Branch( 'err_XtalkLeft_sigma_barCoinc', err_XtalkLeft_sigma_barCoinc, 'err_XtalkLeft_sigma_barCoinc/D' )
treeOutput.Branch( 'XtalkLeft_ChiSquareOverNdf_barCoinc', XtalkLeft_ChiSquareOverNdf_barCoinc, 'XtalkLeft_ChiSquareOverNdf_barCoinc/D' )
treeOutput.Branch( 'XtalkLeft_probChiSquare_barCoinc', XtalkLeft_probChiSquare_barCoinc, 'XtalkLeft_probChiSquare_barCoinc/D' )
treeOutput.Branch( 'XtalkLeft_average_barCoinc', XtalkLeft_average_barCoinc, 'XtalkLeft_average_barCoinc/D' )
treeOutput.Branch( 'XtalkLeft_RMS_barCoinc', XtalkLeft_RMS_barCoinc, 'XtalkLeft_RMS_barCoinc/D' )
#
treeOutput.Branch( 'XtalkRight_mean_barCoinc', XtalkRight_mean_barCoinc, 'XtalkRight_mean_barCoinc/D' )
treeOutput.Branch( 'err_XtalkRight_mean_barCoinc', err_XtalkRight_mean_barCoinc, 'err_XtalkRight_mean_barCoinc/D' )
treeOutput.Branch( 'XtalkRight_sigma_barCoinc', XtalkRight_sigma_barCoinc, 'XtalkRight_sigma_barCoinc/D' )
treeOutput.Branch( 'err_XtalkRight_sigma_barCoinc', err_XtalkRight_sigma_barCoinc, 'err_XtalkRight_sigma_barCoinc/D' )
treeOutput.Branch( 'XtalkRight_ChiSquareOverNdf_barCoinc', XtalkRight_ChiSquareOverNdf_barCoinc, 'XtalkRight_ChiSquareOverNdf_barCoinc/D' )
treeOutput.Branch( 'XtalkRight_probChiSquare_barCoinc', XtalkRight_probChiSquare_barCoinc, 'XtalkRight_probChiSquare_barCoinc/D' )
treeOutput.Branch( 'XtalkRight_average_barCoinc', XtalkRight_average_barCoinc, 'XtalkRight_average_barCoinc/D' )
treeOutput.Branch( 'XtalkRight_RMS_barCoinc', XtalkRight_RMS_barCoinc, 'XtalkRight_RMS_barCoinc/D' )
#
treeOutput.Branch( 'temp_pixel', temp_pixel, 'temp_pixel/D' )
treeOutput.Branch( 'temp_bar', temp_bar, 'temp_bar/D' )
treeOutput.Branch( 'temp_int', temp_int, 'temp_int/D' )
treeOutput.Branch( 'pos_X', pos_X, 'pos_X/D' )
treeOutput.Branch( 'pos_Y', pos_Y, 'pos_Y/D' )
#
treeOutput.Branch( 'bar', bar, 'bar/I' )
treeOutput.Branch( 'code_array', code_array, 'code_array/I' )
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
#peak1_mean_bar[0] = fitResults[('bar',"peak1","mean","value")]
#err_peak1_mean_bar[0] = fitResults[('bar',"peak1","mean","sigma")]
#peak2_mean_bar[0] = fitResults[('bar',"peak2","mean","value")]
#err_peak2_mean_bar[0] = fitResults[('bar',"peak2","mean","sigma")]
#peak1_sigma_bar[0] = fitResults[('bar',"peak1","sigma","value")]
#err_peak1_sigma_bar[0] = fitResults[('bar',"peak1","sigma","sigma")]
#peak2_sigma_bar[0] = fitResults[('bar',"peak2","sigma","value")]
#err_peak2_sigma_bar[0] = fitResults[('bar',"peak2","sigma","sigma")]
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
Xtalk_mean_barCoinc[0] = fitResults[('barCoinc',"Xtalk","mean","value")]
err_Xtalk_mean_barCoinc[0] = fitResults[('barCoinc',"Xtalk","mean","sigma")]
Xtalk_sigma_barCoinc[0] = fitResults[('barCoinc',"Xtalk","sigma","value")]
err_Xtalk_sigma_barCoinc[0] = fitResults[('barCoinc',"Xtalk","sigma","sigma")]
Xtalk_ChiSquareOverNdf_barCoinc[0] = fitResults[('barCoinc',"Xtalk","ChiSquareOverNdf","value")]
Xtalk_probChiSquare_barCoinc[0] = fitResults[('barCoinc',"Xtalk","probChiSquare","value")]
Xtalk_average_barCoinc[0] = fitResults[('barCoinc',"Xtalk","average","value")]
Xtalk_RMS_barCoinc[0] = fitResults[('barCoinc',"Xtalk","RMS","value")]
#
XtalkNhits_average_barCoinc[0] = fitResults[('barCoinc',"XtalkNhits","average","value")]
XtalkNhits_RMS_barCoinc[0] = fitResults[('barCoinc',"XtalkNhits","RMS","value")]
XtalkNbars_average_barCoinc[0] = fitResults[('barCoinc',"XtalkNbars","average","value")]
XtalkNbars_RMS_barCoinc[0] = fitResults[('barCoinc',"XtalkNbars","RMS","value")]
#
XtalkLeft_mean_barCoinc[0] = fitResults[('barCoinc',"XtalkLeft","mean","value")]
err_XtalkLeft_mean_barCoinc[0] = fitResults[('barCoinc',"XtalkLeft","mean","sigma")]
XtalkLeft_sigma_barCoinc[0] = fitResults[('barCoinc',"XtalkLeft","sigma","value")]
err_XtalkLeft_sigma_barCoinc[0] = fitResults[('barCoinc',"XtalkLeft","sigma","sigma")]
XtalkLeft_ChiSquareOverNdf_barCoinc[0] = fitResults[('barCoinc',"XtalkLeft","ChiSquareOverNdf","value")]
XtalkLeft_probChiSquare_barCoinc[0] = fitResults[('barCoinc',"XtalkLeft","probChiSquare","value")]
XtalkLeft_average_barCoinc[0] = fitResults[('barCoinc',"XtalkLeft","average","value")]
XtalkLeft_RMS_barCoinc[0] = fitResults[('barCoinc',"XtalkLeft","RMS","value")]
#
XtalkRight_mean_barCoinc[0] = fitResults[('barCoinc',"XtalkRight","mean","value")]
err_XtalkRight_mean_barCoinc[0] = fitResults[('barCoinc',"XtalkRight","mean","sigma")]
XtalkRight_sigma_barCoinc[0] = fitResults[('barCoinc',"XtalkRight","sigma","value")]
err_XtalkRight_sigma_barCoinc[0] = fitResults[('barCoinc',"XtalkRight","sigma","sigma")]
XtalkRight_ChiSquareOverNdf_barCoinc[0] = fitResults[('barCoinc',"XtalkRight","ChiSquareOverNdf","value")]
XtalkRight_probChiSquare_barCoinc[0] = fitResults[('barCoinc',"XtalkRight","probChiSquare","value")]
XtalkRight_average_barCoinc[0] = fitResults[('barCoinc',"XtalkRight","average","value")]
XtalkRight_RMS_barCoinc[0] = fitResults[('barCoinc',"XtalkRight","RMS","value")]
#
temp_pixel[0] = Temp_pixel
temp_bar[0] = Temp_bar
temp_int[0] = Temp_internal
pos_X[0] = posX
pos_Y[0] = posY
#
bar[0] = int(alignedBar)
runNumber[0] = int(opt.run)
if opt.arrayCode:
    code_array[0] = int(opt.arrayCode)

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


