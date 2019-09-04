#import ROOT as R
import math as m
import numpy as np
import time
import os
from array import array

from ROOT import *

def LYAnalysis(crystal,crystalInfo):
    files={}

    #test crystal
    ly , lyCoinc, ctr = array('d'), array('d'), array('d')
    for r in crystalInfo['runs']:
        files[r]=TFile.Open("/data/TOFPET/LYSOBARS/RESULTS/"+r+".root")
        treeInput = files[r].Get("results")
        nEntries = treeInput.GetEntries()
        if nEntries ==0 or nEntries>1 :
            print "Bad Run (entries in the tree different from 1): "+r
            continue
        treeInput.GetEntry(0)        
        ly.append(treeInput.peak1_mean_bar)
        lyCoinc.append(treeInput.peak1_mean_barCoinc)
        ctr.append(treeInput.CTR_sigma_barCoinc)
        files[r].Close()

    if len(ly)==0:
        print "No good LY data for test crystal "+crystal
        lyAvg=-9999
    else:
        lyAvg=sum(ly)/len(ly)

    if len(lyCoinc)==0:
        print "No good LY data for test crystal "+crystal
        lyCoincAvg=-9999
    else:
        lyCoincAvg=sum(lyCoinc)/len(lyCoinc)

    if len(ctr)==0:
        print "No good time resolution for test crystal "+crystal
        ctrAvg=-9999
    else:
        ctrAvg=sum(ctr)/len(ctr)

    #ref crystal
    lyRef , lyCoincRef, ctrRef = array('d'), array('d'), array('d')
    for r in crystalInfo['refRuns']:
        files[r]=TFile.Open("/data/TOFPET/LYSOBARS/RESULTS/"+r+".root")
        treeInput = files[r].Get("results")
        nEntries = treeInput.GetEntries()
        if nEntries ==0 or nEntries>1 :
            print "Bad Run (entries in the tree different from 1): "+r
            continue
        treeInput.GetEntry(0)        
        lyRef.append(treeInput.peak1_mean_bar)
        lyCoincRef.append(treeInput.peak1_mean_barCoinc)
        ctrRef.append(treeInput.CTR_sigma_barCoinc)
        files[r].Close()

    if len(lyRef)==0:
        print "No good LY data for reference crystal "+crystal
        lyAvgRef=-9999
    else:
        lyAvgRef=sum(lyRef)/len(lyRef)

    if len(lyCoincRef)==0:
        print "No good LY data for reference crystal "+crystal
        lyCoincAvgRef=-9999
    else:
        lyCoincAvgRef=sum(lyCoincRef)/len(lyCoincRef)

    if len(ctrRef)==0:
        print "No good time resolution for reference crystal "+crystal
        ctrAvgRef=-9999
    else:
        ctrAvgRef=sum(ctrRef)/len(ctrRef)

    return { 'ly':lyAvg, 'lyCoinc':lyCoincAvg, 'ctr':ctrAvg, 'lyRef':lyAvgRef, 'lyCoincRef':lyCoincAvgRef, 'ctrRef':ctrAvgRef  }

from crystalsDB import crystalsDB

crystalsDB_withData = {}

for crystal,crystalInfo in crystalsDB.items():
    print crystal, crystalInfo
    print "Analysing crystal "+crystal
    lyData=LYAnalysis(crystal,crystalInfo)
    crystalInfo.update(lyData)
    crystalsDB_withData[crystal]=crystalInfo

##Save CSV using Pandas DataFrame
import pandas as pd
df=pd.DataFrame.from_dict(crystalsDB_withData,orient='index')
#df=df.drop(columns=['runs','refRuns'])
#df=df.drop(['runs','refRuns'],axis=1)
df=df[['producer','geometry','ly','lyCoinc','ctr','lyRef','lyCoincRef','ctrRef']]
df.to_csv('lyAnalysisTOFPET.csv',header=False)
