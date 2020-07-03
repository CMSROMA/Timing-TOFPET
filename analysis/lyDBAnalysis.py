#import ROOT as R
import math as m
import numpy as np
import time
import os
from array import array

from ROOT import *

def LYAnalysis(crystal,runInfo):
    files={}

    #test crystal
    ly, ctr, temp, posX, posY = array('d'), array('d'), array('d'), array('d'), array('d')
    for r in runInfo['runs']:
        files[r]=TFile.Open(args.data+"/"+r+".root")
        treeInput = files[r].Get("results")
        nEntries = treeInput.GetEntries()
        if nEntries ==0 or nEntries>1 :
            print "Bad Run (entries in the tree different from 1): "+r
            continue
        treeInput.GetEntry(0)        
        ly.append(treeInput.peak1_mean_barCoinc)
        ctr.append(treeInput.CTR_sigma_barCoinc)
        temp.append(treeInput.temp_bar)
        posX.append(treeInput.pos_X)
        posY.append(treeInput.pos_Y)
        files[r].Close()

    if len(ly)==0:
        print "No good LY data for test crystal "+crystal
        lyAvg=-9999.
    else:
        lyAvg=sum(ly)/len(ly)

    if len(ctr)==0:
        print "No good time resolution for test crystal "+crystal
        ctrAvg=-9999.
    else:
        ctrAvg=sum(ctr)/len(ctr)

    if len(temp)==0:
        print "No good temperature for test crystal "+crystal
        tempAvg=-9999.
    else:
        tempAvg=sum(temp)/len(temp)

    if len(posX)==0:
        print "No good position X for test crystal "+crystal
        posXAvg=-9999.
    else:
        posXAvg=sum(posX)/len(posX)

    if len(posY)==0:
        print "No good position Y for test crystal "+crystal
        posYAvg=-9999.
    else:
        posYAvg=sum(posY)/len(posY)

    #ref crystal
    lyRef, ctrRef = array('d'), array('d')
    for r in runInfo['refRuns']:
        files[r]=TFile.Open(args.data+"/"+r+".root")
        treeInput = files[r].Get("results")
        nEntries = treeInput.GetEntries()
        if nEntries ==0 or nEntries>1 :
            print "Bad Run (entries in the tree different from 1): "+r
            continue
        treeInput.GetEntry(0)        
        lyRef.append(treeInput.peak1_mean_barCoinc)
        ctrRef.append(treeInput.CTR_sigma_barCoinc)
        files[r].Close()

    if len(lyRef)==0:
        print "No good LY data for reference crystal "+crystal
        lyAvgRef=-9999.
    else:
        lyAvgRef=sum(lyRef)/len(lyRef)

    if len(ctrRef)==0:
        print "No good time resolution for reference crystal "+crystal
        ctrAvgRef=-9999.
    else:
        ctrAvgRef=sum(ctrRef)/len(ctrRef)

    return { 'ly':lyAvg, 'ctr':ctrAvg, 'temp':tempAvg, 'posX':posXAvg, 'posY':posYAvg, 'lyRef':lyAvgRef, 'ctrRef':ctrAvgRef }

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output',dest='output')
parser.add_argument('--db',dest='db')
parser.add_argument('--data',dest='data')
args = parser.parse_args()

import json
crystalsDB=json.load(open(args.db))

crystalsDB_withData = {}

for crystal,crystalInfo in crystalsDB.items():
    print crystal, crystalInfo
    if ('BAR' in crystal):
        print "Analysing crystal "+crystal
        for runInfo in crystalInfo['runs']:
            tag=runInfo['tag']
            lyData=LYAnalysis(crystal,runInfo)
            lyData.update({'tag':"%s"%tag})
            data={}
            data.update(crystalInfo)
            data.pop('runs',None)
            data.update(lyData)
            crystalsDB_withData['%s_%s'%(crystal,tag)]=data

##Save CSV using Pandas DataFrame
import pandas as pd
df=pd.DataFrame.from_dict(crystalsDB_withData,orient='index')
#df=df.drop(columns=['runs','refRuns'])
#df=df.drop(['runs','refRuns'],axis=1)
df=df[['producer','type','id','geometry','tag','temp','posX','posY','ly','ctr','lyRef','ctrRef']]
#df.to_csv('lyAnalysisTOFPET.csv',header=False)
#print df
df.to_csv(args.output,header=False)
