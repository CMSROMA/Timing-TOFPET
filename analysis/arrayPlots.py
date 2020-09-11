import ROOT as R
R.gROOT.SetBatch(1)
from array import array
import math as mt
import numpy as np
import os
import sys

#reading csv
arraysData=R.TTree("arraysData","arraysData")
arraysData.ReadFile("arraysDB_Milano_Sep2019.csv","name/C:prod/C:type/C:id/I:geo/C:tag/C:temp/F:barID/I:posX/F:posY/F:ly/F:ctr/F:lyRef/F:ctrRef/F:xtLeft/F:xtRight/F:xt/F")

#output dit
outputdir = "arrayPlotsDir"
os.system("mkdir -p "+outputdir)

#general info
producers = [ 'prod1', 'prod5' ]

#########################################################

# Book istograms

histos = {}

graphNames = {"ly_mean":{"min":50.,"max":80.,"nbinX":30,
                         "minPlot":50.,"maxPlot":80.,
                         "xtitle":"LO mean of array [a.u.]",
                         "xtitleVsProd":"LO mean of array (+/- std. dev.) [a.u.]",
                         "thr":-9},
              "ly_relstd":{"min":0.,"max":20.,"nbinX":20,
                           "minPlot":0.,"maxPlot":15.,
                           "xtitle":"Relative spread of array LO [%]",
                           "xtitleVsProd":"Relative spread of array LO (+/- std. dev.) [%]",
                           "thr":5},
              "lyNorm_mean":{"min":0.75,"max":1.25,"nbinX":20,
                             "minPlot":0.75,"maxPlot":1.25,
                             "xtitle":"Norm. LO mean of array [a.u.]",
                             "xtitleVsProd":"Norm. LO mean of array (+/- std. dev.) [a.u.]",
                             "thr":-9},
              "lyNorm_relstd":{"min":0.,"max":20.,"nbinX":20,
                               "minPlot":0.,"maxPlot":15.,
                               "xtitle":"Relative spread of norm. array LO [%]",
                               "xtitleVsProd":"Relative spread of norm. array LO (+/- std. dev.) [%]",
                               "thr":5},

              "sigmat_mean":{"min":100.,"max":160.,"nbinX":20,
                             "minPlot":100.,"maxPlot":160.,
                             "xtitle":"#sigma_{t} mean of array [ps]",
                             "xtitleVsProd":"#sigma_{t} mean of array (+/- std. dev.) [ps]",
                             "thr":150},
              "sigmat_relstd":{"min":0.,"max":20.,"nbinX":20,
                               "minPlot":0.,"maxPlot":15.,
                               "xtitle":"Relative spread of array #sigma_{t} [%]",
                               "xtitleVsProd":"Relative spread of array #sigma_{t} (+/- std. dev.) [%]",
                               "thr":5},
              "sigmatNorm_mean":{"min":0.75,"max":1.25,"nbinX":20,
                                 "minPlot":0.75,"maxPlot":1.25,
                                 "xtitle":"Norm. #sigma_{t} mean of array [a.u.]",
                                 "xtitleVsProd":"Norm. #sigma_{t} mean of array (+/- std. dev.) [a.u.]",
                                 "thr":-9},
              "sigmatNorm_relstd":{"min":0.,"max":20.,"nbinX":20,
                                   "minPlot":0.,"maxPlot":15.,
                                   "xtitle":"Relative spread of norm. array #sigma_{t} [%]",
                                   "xtitleVsProd":"Relative spread of norm. array #sigma_{t} (+/- std. dev.) [%]",
                                   "thr":5},

              "xt_mean":{"min":0.,"max":40,"nbinX":20,
                         "minPlot":0.,"maxPlot":50,
                         "xtitle":"Cross talk mean of array [%]",
                         "xtitleVsProd":"Cross talk mean of array (+/- std. dev.) [%]",
                         "thr":15},
              
              "xt_relstd":{"min":0.,"max":100.,"nbinX":20,
                           "minPlot":0.,"maxPlot":100.,
                           "xtitle":"Relative spread of array cross talk [%]",
                           "xtitleVsProd":"Relative spread of array cross talk (+/- std. dev.) [%]",
                           "thr":5},

              "xtLeft_mean":{"min":0.,"max":40,"nbinX":20,
                             "minPlot":0.,"maxPlot":50,
                             "xtitle":"Cross talk (left) mean of array [%]",
                             "xtitleVsProd":"Cross talk (left) mean of array (+/- std. dev.) [%]",
                             "thr":7.5},
              
              "xtLeft_relstd":{"min":0.,"max":100.,"nbinX":20,
                               "minPlot":0.,"maxPlot":100.,
                               "xtitle":"Relative spread of array cross talk (left) [%]",
                               "xtitleVsProd":"Relative spread of array cross talk (left) (+/- std. dev.) [%]",
                               "thr":5},

              "xtRight_mean":{"min":0.,"max":40,"nbinX":20,
                             "minPlot":0.,"maxPlot":50,
                             "xtitle":"Cross talk (right) mean of array [%]",
                             "xtitleVsProd":"Cross talk (right) mean of array (+/- std. dev.) [%]",
                             "thr":7.5},
              
              "xtRight_relstd":{"min":0.,"max":100.,"nbinX":20,
                               "minPlot":0.,"maxPlot":100.,
                               "xtitle":"Relative spread of array cross talk (right) [%]",
                               "xtitleVsProd":"Relative spread of array cross talk (right) (+/- std. dev.) [%]",
                               "thr":5}
          }

print graphNames

for var, values in graphNames.items():
    print var, values
    histos[var+'_VsProd']=R.TGraphErrors(len(producers)) 

for prod in producers:
    for var, values in graphNames.items():
        histos[var+'_'+prod]=R.TH1F(var+'_'+prod,var+'_'+prod,values["nbinX"],values["min"],values["max"])        

#########################################################

# Create dictionary with pre-irradiation data

# 1) create list of arrays for each producer

listArrayPreIRR = {}

for prod in producers: 
    listArrayPreIRR[prod] = []

for arr in arraysData:

    if ( arr.ly < 0. or arr.ctr < 0. or arr.lyRef < 0. or arr.ctrRef < 0. or arr.xt < 0.):
        continue

    prod = arr.prod.rstrip('\x00')

    if arr.id not in listArrayPreIRR[prod]:
        listArrayPreIRR[prod].append(arr.id)

for prod in producers: 
    listArrayPreIRR[prod].sort()
    print listArrayPreIRR[prod]

# 2) create dictionary dataPreIRR[prod][array]

dataPreIRR = {}
blacklistBars = [0]

for prod in producers:
    for arr in listArrayPreIRR[prod]:
        dataPreIRR[prod+str(arr)] = []

for arr in arraysData:

    if ( arr.ly < 0. or arr.ctr < 0. or arr.lyRef < 0. or arr.ctrRef < 0. or arr.xt < 0.):
        continue

    prod = arr.prod.rstrip('\x00')
    tag = arr.tag.rstrip('\x00')
    prodN = int(prod.strip('prod'))
    ID = arr.id
    
    if("IRR0" in tag):
        if (arr.barID not in blacklistBars):
            dataPreIRR[prod+str(ID)].append({'name':arr.name.rstrip('\x00'), 'type':arr.type.rstrip('\x00'), 
                                             'geo' :arr.geo.rstrip('\x00'), 'id':ID, 'barID': arr.barID, 
                                             'ly': arr.ly, 'lyNorm': arr.ly/arr.lyRef, 
                                             'sigmat': arr.ctr/2., 'sigmatNorm': (arr.ctr/2.) / (arr.ctrRef/2.), 
                                             'xtLeft': arr.xtLeft, 'xtRight': arr.xtRight, 'xt':arr.xt})

#########################################################

# Make plots

R.gStyle.SetOptTitle(0)
c1=R.TCanvas("c1","c1",800,800)
 
#loop over producers
for iprod,prod in enumerate(producers): 
    
    prodN = int(prod.strip('prod'))

    print ""
    print "---------------------------------- producer ", prod, "----------------------------------"

    #-- Fill histograms --#

    #loop over arrays
    for arr in listArrayPreIRR[prod]:
        print " ======= array ", arr, "..."
        print dataPreIRR[prod+str(arr)]

        nbars = len( dataPreIRR[prod+str(arr)] )

        #loop over bars in array
        ly = np.empty(nbars)
        lyNorm = np.empty(nbars)
        sigmat = np.empty(nbars)
        sigmatNorm = np.empty(nbars)        
        xt = np.empty(nbars)
        xtLeft = np.empty(nbars)
        xtRight = np.empty(nbars)

        for i,meas in enumerate(dataPreIRR[prod+str(arr)]):
            ly[i]=meas['ly']
            lyNorm[i]=meas['lyNorm']
            sigmat[i]=meas['sigmat']
            sigmatNorm[i]=meas['sigmatNorm']
            xt[i]=meas['xt']   
            xtLeft[i]=meas['xtLeft']   
            xtRight[i]=meas['xtRight']   

        #overall measurements for a given array
        #NOTE: check the dictionary "graphNames"
        ly_mean = ly.mean()
        ly_relstd = ly.std()/ly.mean()
        lyNorm_mean = lyNorm.mean()
        lyNorm_relstd = lyNorm.std()/lyNorm.mean()

        sigmat_mean = sigmat.mean()
        sigmat_relstd = sigmat.std()/sigmat.mean()
        sigmatNorm_mean = sigmatNorm.mean()
        sigmatNorm_relstd = sigmatNorm.std()/sigmatNorm.mean()

        xt_mean = xt.mean()
        xt_relstd = xt.std()/xt.mean()
        xtLeft_mean = xtLeft.mean()
        xtLeft_relstd = xtLeft.std()/xtLeft.mean()
        xtRight_mean = xtRight.mean()
        xtRight_relstd = xtRight.std()/xtRight.mean()

        print ly_mean, ly_relstd, lyNorm_mean, lyNorm_relstd, sigmat_mean, sigmat_relstd, sigmatNorm_mean, sigmatNorm_relstd, xt_mean, xt_relstd, xtLeft_mean, xtLeft_relstd,xtRight_mean, xtRight_relstd

        histos['ly_mean_'+prod].Fill(ly_mean)
        histos['ly_relstd_'+prod].Fill(ly_relstd*100)
        histos['lyNorm_mean_'+prod].Fill(lyNorm_mean)
        histos['lyNorm_relstd_'+prod].Fill(lyNorm_relstd*100)

        histos['sigmat_mean_'+prod].Fill(sigmat_mean)
        histos['sigmat_relstd_'+prod].Fill(sigmat_relstd*100)
        histos['sigmatNorm_mean_'+prod].Fill(sigmatNorm_mean)
        histos['sigmatNorm_relstd_'+prod].Fill(sigmatNorm_relstd*100)
        
        histos['xt_mean_'+prod].Fill(xt_mean*100)
        histos['xt_relstd_'+prod].Fill(xt_relstd*100)
        histos['xtLeft_mean_'+prod].Fill(xtLeft_mean*100)
        histos['xtLeft_relstd_'+prod].Fill(xtLeft_relstd*100)
        histos['xtRight_mean_'+prod].Fill(xtRight_mean*100)
        histos['xtRight_relstd_'+prod].Fill(xtRight_relstd*100)

    #-- Draw plots --#

    #== plots for each producers
    for var, values in graphNames.items():

        histos[var+'_'+prod].GetXaxis().SetTitle(values["xtitle"])    
        histos[var+'_'+prod].Draw("hist")
        for ext in ['.pdf','.png']:
            c1.SaveAs(outputdir+"/"+var+'_'+prod+ext)

        histos[var+'_VsProd'].SetPoint(iprod,prodN,histos[var+'_'+prod].GetMean())
        histos[var+'_VsProd'].SetPointError(iprod,0.,histos[var+'_'+prod].GetRMS())

# Summary plots vs producer

for var, values in graphNames.items():

    histos[var+'_VsProd'].SetMarkerStyle(20)
    histos[var+'_VsProd'].GetXaxis().SetNdivisions(505)
    histos[var+'_VsProd'].GetXaxis().SetTitle("Vendor ID")
    histos[var+'_VsProd'].GetYaxis().SetTitle(values["xtitleVsProd"])
    histos[var+'_VsProd'].GetYaxis().SetLimits(values["minPlot"],values["maxPlot"])
    histos[var+'_VsProd'].GetYaxis().SetRangeUser(values["minPlot"],values["maxPlot"])
    histos[var+'_VsProd'].GetYaxis().SetTitleOffset(1.4)
    histos[var+'_VsProd'].Draw("ape")

    if( ("relstd" in var) or ("xt_mean" in var) or ("xtLeft_mean" in var) or ("xtRight_mean" in var) 
        or ("sigmat_mean" in var) ):
        minX = histos[var+'_VsProd'].GetXaxis().GetXmin()
        maxX = histos[var+'_VsProd'].GetXaxis().GetXmax()
        line = R.TLine(minX,values["thr"],maxX,values["thr"]);
        line.SetLineColor(2)
        line.Draw("same")

    for ext in ['.pdf','.png']:
        c1.SaveAs(outputdir+"/"+var+'_VsProd'+ext)


