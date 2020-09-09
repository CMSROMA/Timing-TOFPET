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
    nfound = spectrum.Search(histo , 3 ,"new",0.25)
    xpeaks = spectrum.GetPositionX()
    posPeak = []
    for i in range(spectrum.GetNPeaks()):
        posPeak.append(xpeaks[i])
    posPeak.sort()

    if(len(posPeak)==0):
        fitres[(label,"peak1","mean","value")]=-999
        fitres[(label,"peak1","mean","sigma")]=-999
        fitres[(label,"peak1","sigma","value")]=-999
        fitres[(label,"peak1","sigma","sigma")]=-999
        return 1

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
## 7) Coincidence time resolution (CTR)
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
        gROOT.ProcessLine('ctrAnalysis.alignedBar_511Peak_mean.push_back(-9.);')
        gROOT.ProcessLine('ctrAnalysis.alignedBar_511Peak_sigma.push_back(-9.);')
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


### Time resolution ###

tfileoutput = TFile( opt.outputDir+"/"+"histo_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root", "update" )
tfileoutput.cd()
histos=Map(tfileoutput)

c1_energy.cd()

lowStat_channels = []

for barId in range(0,16):

    if( histos[("h1_deltaT12_bar%d"%barId)].GetEntries()<300 ):
        lowStat_channels.append(barId)

    if ( (barId in dead_channels) or (barId in lowStat_channels) ) :
        fitResults[('barCoinc%d'%barId,"deltaT12_bar","mean","value")]=-9
        fitResults[('barCoinc%d'%barId,"deltaT12_bar","mean","sigma")]=-9
        fitResults[('barCoinc%d'%barId,"deltaT12_bar","sigma","value")]=-9
        fitResults[('barCoinc%d'%barId,"deltaT12_bar","sigma","sigma")]=-9
        print "== No time resolution plots of bar%d"%barId
        continue

    histos[("h1_deltaT12_bar%d"%barId)].Draw("PE")
    f_gaus = TF1("f_gaus","gaus",
                 histos[("h1_deltaT12_bar%d"%barId)].GetBinCenter(histos[("h1_deltaT12_bar%d"%barId)].GetMaximumBin())-1000.,
                 histos[("h1_deltaT12_bar%d"%barId)].GetBinCenter(histos[("h1_deltaT12_bar%d"%barId)].GetMaximumBin())+1000.)
    histos[("h1_deltaT12_bar%d"%barId)].Fit(f_gaus,"R+0N","",histos[("h1_deltaT12_bar%d"%barId)].GetBinCenter(histos[("h1_deltaT12_bar%d"%barId)].GetMaximumBin())-2.5*histos[("h1_deltaT12_bar%d"%barId)].GetRMS(),histos[("h1_deltaT12_bar%d"%barId)].GetBinCenter(histos[("h1_deltaT12_bar%d"%barId)].GetMaximumBin())+2.5*histos[("h1_deltaT12_bar%d"%barId)].GetRMS())
    histos[("h1_deltaT12_bar%d"%barId)].Fit(f_gaus,"R+","",f_gaus.GetParameter(1)-2.5*f_gaus.GetParameter(2),f_gaus.GetParameter(1)+2.5*f_gaus.GetParameter(2))
    histos[("h1_deltaT12_bar%d"%barId)].GetXaxis().SetRangeUser(f_gaus.GetParameter(1)-1000.,f_gaus.GetParameter(1)+1000.)
    histos[("h1_deltaT12_bar%d"%barId)].GetXaxis().SetTitle(("(t_{1} - t_{2}) bar%d [ps]"%barId))
    histos[("h1_deltaT12_bar%d"%barId)].GetYaxis().SetTitle("Events")
    histos[("h1_deltaT12_bar%d"%barId)].GetYaxis().SetTitleOffset(1.6)

    fitResults[('barCoinc%d'%barId,"deltaT12_bar","mean","value")]=f_gaus.GetParameter(1)
    fitResults[('barCoinc%d'%barId,"deltaT12_bar","mean","sigma")]=f_gaus.GetParError(1)
    fitResults[('barCoinc%d'%barId,"deltaT12_bar","sigma","value")]=f_gaus.GetParameter(2)
    fitResults[('barCoinc%d'%barId,"deltaT12_bar","sigma","sigma")]=f_gaus.GetParError(2)

    pt3 = TPaveText(0.100223,0.915556,0.613586,0.967407,"brNDC")
    text3 = pt3.AddText( "Run" + str(opt.run.zfill(6)) + " ARRAY" + str(opt.arrayCode.zfill(6)) + " BAR"+str(barId))
    pt3.SetFillColor(0)
    pt3.Draw()
    c1_energy.cd()
    c1_energy.Update()
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(barId)+"_deltaT12_bar"+".pdf")
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(barId)+"_deltaT12_bar"+".png")
    c1_energy.Write()
    histos[("h1_deltaT12_bar%d"%barId)].Write()


### Cross talk ###

lowStat_channels_xtalk = []

for barId in range(0,16):

    if( histos[("h1_nhits_bar%d_Xtalk"%barId)].GetEntries()<300 ):
        lowStat_channels_xtalk.append(barId)

    if ( (barId in dead_channels) or (barId in lowStat_channels_xtalk) 
         or (barId-1 in dead_channels) or (barId+1 in dead_channels) ) :
        fitResults[('barCoinc%d'%barId,"XtalkEnergyLeft","median","value")]=-9
        fitResults[('barCoinc%d'%barId,"XtalkEnergyRight","median","value")]=-9
        fitResults[('barCoinc%d'%barId,"XtalkLeft","median","value")]=-9
        fitResults[('barCoinc%d'%barId,"XtalkRight","median","value")]=-9
        print "== No xtalk info bar%d"%barId
        continue

    # calculate median of xtalk left and right histograms
    prob = array( 'd', [ 0.5 ] )
    XtalkLeft_median = array( 'd' , [0.] )
    XtalkRight_median = array( 'd' , [0.] )
    histos[("h1_energyLeft_bar%d_Xtalk"%barId)].GetQuantiles(1,XtalkLeft_median,prob)
    histos[("h1_energyRight_bar%d_Xtalk"%barId)].GetQuantiles(1,XtalkRight_median,prob)

    # correct left and right energy for 511 keV peak position 
    barIdLeft = barId-1
    barIdRight = barId+1
    if (barId != 0):
        fitResults[('barCoinc%d'%barId,"XtalkEnergyLeft","median","value")]=XtalkLeft_median[0]
        fitResults[('barCoinc%d'%barId,"XtalkLeft","median","value")]=XtalkLeft_median[0] / fitResults[('barCoinc%d'%barIdLeft,"peak1","mean","value")]
    else:
        fitResults[('barCoinc%d'%barId,"XtalkEnergyLeft","median","value")]=0.
        fitResults[('barCoinc%d'%barId,"XtalkLeft","median","value")]=0.

    if (barId != 15):
        fitResults[('barCoinc%d'%barId,"XtalkEnergyRight","median","value")]=XtalkRight_median[0]
        fitResults[('barCoinc%d'%barId,"XtalkRight","median","value")]=XtalkRight_median[0] / fitResults[('barCoinc%d'%barIdRight,"peak1","mean","value")]
    else:
        fitResults[('barCoinc%d'%barId,"XtalkEnergyRight","median","value")]=0.
        fitResults[('barCoinc%d'%barId,"XtalkRight","median","value")]=0.

    fitResults[('barCoinc%d'%barId,"Xtalk","median","value")] = fitResults[('barCoinc%d'%barId,"XtalkLeft","median","value")] + fitResults[('barCoinc%d'%barId,"XtalkRight","median","value")]

    # plots
    pt4 = TPaveText(0.100223,0.915556,0.613586,0.967407,"brNDC")
    text4 = pt4.AddText( "Run" + str(opt.run.zfill(6)) + " ARRAY" + str(opt.arrayCode.zfill(6)) + " BAR"+str(barId))
    pt4.SetFillColor(0)
    pt4.Draw()
    c1_energy.cd()
    c1_energy.Update()
    histos[("h1_energyLeft_bar%d_Xtalk"%barId)].Draw()
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(barId)+"_XtalkEnergyLeft"+".pdf")
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(barId)+"_XtalkEnergyLeft"+".png")
    c1_energy.Write()

    c1_energy.Update()
    histos[("h1_energyRight_bar%d_Xtalk"%barId)].Draw()
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(barId)+"_XtalkEnergyRight"+".pdf")
    c1_energy.SaveAs(opt.outputDir+"/"+"Run"+str(opt.run.zfill(6))+"_ARRAY"+str(opt.arrayCode.zfill(6))+"_BAR"+str(barId)+"_XtalkEnergyRight"+".png")
    c1_energy.Write()

    print ""
    print "=== ", barId , "==="
    print "XtalkEnergyLeft", fitResults[('barCoinc%d'%barId,"XtalkEnergyLeft","median","value")]
    print "XtalkEnergyRight", fitResults[('barCoinc%d'%barId,"XtalkEnergyRight","median","value")]
    print "XtalkLeft", fitResults[('barCoinc%d'%barId,"XtalkLeft","median","value")]
    print "XtalkRight", fitResults[('barCoinc%d'%barId,"XtalkRight","median","value")]
    print "Xtalk", fitResults[('barCoinc%d'%barId,"Xtalk","median","value")]
    print "=== ==="

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
    #print "--- Channel = "+str(ch).zfill(3)+" ---"

    #for tac in range(0,4):
        #print "====" 
        #print "TacID ", tac 
        #print "Pedestal1 "+str(mean_Ped1[(ch,tac)])+" "+str(rms_Ped1[(ch,tac)]) 
        #print "Pedestal2 "+str(mean_Ped2[(ch,tac)])+" "+str(rms_Ped2[(ch,tac)]) 
        #print "PedestalTot "+str(mean_PedTot[(ch,tac)])+" "+str(rms_PedTot[(ch,tac)]) 

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

tfileoutputtree = TFile( opt.outputDir+"/"+"tree_Run"+run+"_ARRAY"+str(str(opt.arrayCode).zfill(6))+".root", "recreate" )
tfileoutputtree.cd()

treeOutput = TTree( 'results', 'root tree with measurements' )

#----------------------

#
temp_pixel = array( 'd', [ -999. ] )
temp_bar = array( 'd', [ -999. ] )
temp_int = array( 'd', [ -999. ] )
pos_X = array( 'd', [ -999. ] )
pos_Y = array( 'd', [ -999. ] )
#
code_array = array( 'i', [ -999 ] )
runNumber = array( 'i', [ -999 ] )
#
peak1_mean_barRef = array( 'd', [ -999. ] )
err_peak1_mean_barRef = array( 'd', [ -999. ] )
peak1_sigma_barRef = array( 'd', [ -999. ] )
err_peak1_sigma_barRef = array( 'd', [ -999. ] )
#
peak1_mean_barCoinc = array( 'd', [ -999. ]*16 )
err_peak1_mean_barCoinc = array( 'd', [ -999. ]*16 )
peak1_sigma_barCoinc = array( 'd', [ -999. ]*16 )
err_peak1_sigma_barCoinc = array( 'd', [ -999. ]*16 )
#
deltaT12_mean_barCoinc = array( 'd', [ -999. ]*16 )
err_deltaT12_mean_barCoinc = array( 'd', [ -999. ]*16 )
deltaT12_sigma_barCoinc = array( 'd', [ -999. ]*16 )
err_deltaT12_sigma_barCoinc = array( 'd', [ -999. ]*16 )
#
XtalkLeft_median_barCoinc = array( 'd', [ -999. ]*16 )
XtalkRight_median_barCoinc = array( 'd', [ -999. ]*16 )
Xtalk_median_barCoinc = array( 'd', [ -999. ]*16 )

#----------------------

#
treeOutput.Branch( 'temp_pixel', temp_pixel, 'temp_pixel/D' )
treeOutput.Branch( 'temp_bar', temp_bar, 'temp_bar/D' )
treeOutput.Branch( 'temp_int', temp_int, 'temp_int/D' )
treeOutput.Branch( 'pos_X', pos_X, 'pos_X/D' )
treeOutput.Branch( 'pos_Y', pos_Y, 'pos_Y/D' )
#
treeOutput.Branch( 'code_array', code_array, 'code_array/I' )
treeOutput.Branch( 'runNumber', runNumber, 'runNumber/I' )
#
treeOutput.Branch( 'peak1_mean_barRef', peak1_mean_barRef, 'peak1_mean_barRef/D' )
treeOutput.Branch( 'err_peak1_mean_barRef', err_peak1_mean_barRef, 'err_peak1_mean_barRef/D' )
treeOutput.Branch( 'peak1_sigma_barRef', peak1_sigma_barRef, 'peak1_sigma_barRef/D' )
treeOutput.Branch( 'err_peak1_sigma_barRef', err_peak1_sigma_barRef, 'err_peak1_sigma_barRef/D' )
#
treeOutput.Branch( 'peak1_mean_barCoinc', peak1_mean_barCoinc, 'peak1_mean_barCoinc[16]/D' )
treeOutput.Branch( 'err_peak1_mean_barCoinc', err_peak1_mean_barCoinc, 'err_peak1_mean_barCoinc[16]/D' )
treeOutput.Branch( 'peak1_sigma_barCoinc', peak1_sigma_barCoinc, 'peak1_sigma_barCoinc[16]/D' )
treeOutput.Branch( 'err_peak1_sigma_barCoinc', err_peak1_sigma_barCoinc, 'err_peak1_sigma_barCoinc[16]/D' )
#
treeOutput.Branch( 'deltaT12_mean_barCoinc', deltaT12_mean_barCoinc, 'deltaT12_mean_barCoinc[16]/D' )
treeOutput.Branch( 'err_deltaT12_mean_barCoinc', err_deltaT12_mean_barCoinc, 'err_deltaT12_mean_barCoinc[16]/D' )
treeOutput.Branch( 'deltaT12_sigma_barCoinc', deltaT12_sigma_barCoinc, 'deltaT12_sigma_barCoinc[16]/D' )
treeOutput.Branch( 'err_deltaT12_sigma_barCoinc', err_deltaT12_sigma_barCoinc, 'err_deltaT12_sigma_barCoinc[16]/D' )
#
treeOutput.Branch( 'XtalkLeft_median_barCoinc', XtalkLeft_median_barCoinc, 'XtalkLeft_median_barCoinc[16]/D' )
treeOutput.Branch( 'XtalkRight_median_barCoinc', XtalkRight_median_barCoinc, 'XtalkRight_median_barCoinc[16]/D' )
treeOutput.Branch( 'Xtalk_median_barCoinc', Xtalk_median_barCoinc, 'Xtalk_median_barCoinc[16]/D' )

#----------------------

#
temp_pixel[0] = Temp_pixel
temp_bar[0] = Temp_bar
temp_int[0] = Temp_internal
pos_X[0] = posX
pos_Y[0] = posY
#
runNumber[0] = int(opt.run)
if opt.arrayCode:
    code_array[0] = int(opt.arrayCode)
#
peak1_mean_barRef[0] = fitResults[('barRef',"peak1","mean","value")]
err_peak1_mean_barRef[0] = fitResults[('barRef',"peak1","mean","sigma")]
peak1_sigma_barRef[0] = fitResults[('barRef',"peak1","sigma","value")]
err_peak1_sigma_barRef[0] = fitResults[('barRef',"peak1","sigma","sigma")]
#
for barId in range(0,16):

    print "=== barId%d ===="%barId

    ## LO 
    if ( barId in dead_channels ) :
        continue

    print "barId%d -- Store LO in root tree:"%barId
    peak1_mean_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"peak1","mean","value")]
    err_peak1_mean_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"peak1","mean","sigma")]
    peak1_sigma_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"peak1","sigma","value")]
    err_peak1_sigma_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"peak1","sigma","sigma")]

    ## Time resolution
    if ( barId in lowStat_channels ) :
        continue
    else:
        print "barId%d -- Store time resolution in root tree:"%barId
        deltaT12_mean_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"deltaT12_bar","mean","value")]
        err_deltaT12_mean_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"deltaT12_bar","mean","sigma")]
        deltaT12_sigma_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"deltaT12_bar","sigma","value")]
        err_deltaT12_sigma_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"deltaT12_bar","sigma","sigma")]

    ## Xtalk
    if ( (barId in lowStat_channels_xtalk) or (barId-1 in dead_channels) or (barId+1 in dead_channels) ) :
        continue
    else:
        print "barId%d -- Store xtalk in root tree:"%barId
        XtalkLeft_median_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"XtalkLeft","median","value")]
        XtalkRight_median_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"XtalkRight","median","value")]
        Xtalk_median_barCoinc[barId] = fitResults[('barCoinc%d'%barId,"Xtalk","median","value")]

    print "=== ==="
#

#----------------------

treeOutput.Fill()
tfileoutputtree.Write()
tfileoutputtree.Close()




