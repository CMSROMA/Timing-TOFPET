#import ROOT as R
import math as m
import numpy as np
import time
import os
from array import array

from ROOT import *

def LYAnalysis(crystal,runInfo,bar,lenght):
    files={}

    #test crystal
    barN, ly, lyLeft, lyRight, ctr, temp, posX, posY, xtLeft, xtRight = array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d')

    for r in runInfo['runs']:
        files[r]=TFile.Open(args.data+"/"+r+".root")
        treeInput = files[r].Get("results")
        nEntries = treeInput.GetEntries()
        if nEntries != lenght:
            print "Bad Run (entries in the tree different from "+ lenght +"): "+r
            continue        
        for event in range (0,nEntries):
            treeInput.GetEntry(event)        
            if (treeInput.bar == int(bar)):
                barN.append(treeInput.bar)
                ly.append(treeInput.peak1_mean_barCoinc)
                ctr.append(treeInput.CTR_sigma_barCoinc)
                temp.append(treeInput.temp_bar)
                posX.append(treeInput.pos_X)
                posY.append(treeInput.pos_Y)
                if ( treeInput.err_XtalkLeft_mean_barCoinc/treeInput.XtalkLeft_mean_barCoinc < 0.4 and #cut value guessed
                     treeInput.err_XtalkLeft_sigma_barCoinc/treeInput.XtalkLeft_sigma_barCoinc < 0.4):
                    xtLeft.append(treeInput.XtalkLeft_mean_barCoinc)
                if ( treeInput.err_XtalkRight_mean_barCoinc/treeInput.XtalkRight_mean_barCoinc < 0.4 and
                     treeInput.err_XtalkRight_sigma_barCoinc/treeInput.XtalkRight_sigma_barCoinc < 0.4):
                    xtRight.append(treeInput.XtalkRight_mean_barCoinc)

            if ((int(bar)-1)>=0 and treeInput.bar == (int(bar)-1)):
                lyLeft.append(treeInput.peak1_mean_barCoinc)

            if ((int(bar)+1)<16 and treeInput.bar == (int(bar)+1)):
                lyRight.append(treeInput.peak1_mean_barCoinc)

        files[r].Close()

    if len(barN)==0:
        print "No good bar info data for test crystal "+crystal
        barNAvg=-9999.
    else:
        barNAvg=sum(barN)/len(barN)

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

    if len(lyLeft)==0 or len(xtLeft)==0:
        print "No xt data for test crystal "+crystal
        xtLeftAvg=-9999.
    else:
        lyLeftAvg=sum(lyLeft)/len(lyLeft)
        xtLeftAvg=sum(xtLeft)/len(xtLeft)/lyLeftAvg #normalise to ly in given crystal

    if len(lyRight)==0 or len(xtRight)==0:
        print "No xt data for test crystal "+crystal
        xtRightAvg=-9999.
    else:
        lyRightAvg=sum(lyRight)/len(lyRight)
        xtRightAvg=sum(xtRight)/len(xtRight)/lyRightAvg #normalise to ly in given crystal

    #ref crystal
    lyRef, ctrRef = array('d'), array('d')
    for r in runInfo['refRuns']:
        files[r]=TFile.Open(args.data+"/"+r+".root")
        treeInput = files[r].Get("results")
        nEntries = treeInput.GetEntries()
        if nEntries != lenght:
            print "Bad Run (entries in the tree different from "+ lenght +"): "+r
            continue        
        for event in range (0,nEntries):
            treeInput.GetEntry(event)        
            if (treeInput.bar == int(bar)):
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

    return { 'bar': bar, 'ly':lyAvg, 'ctr':ctrAvg, 'temp':tempAvg, 'posX':posXAvg, 'posY':posYAvg, 'lyRef':lyAvgRef, 'ctrRef':ctrAvgRef, 'xtLeft':xtLeftAvg, 'xtRight':xtRightAvg }

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output',dest='output')
parser.add_argument('--db',dest='db')
parser.add_argument('--data',dest='data')
args = parser.parse_args()

exec "from %s import crystalsDB" % args.db
#from crystalsDB_Casaccia_Nov2019 import crystalsDB

crystalsDB_withData = {}

for crystal,crystalInfo in crystalsDB.items():
    print crystal, crystalInfo
    print "Analysing array "+crystal
    for runInfo in crystalInfo['runs']:
        tag=runInfo['tag']
        barList=runInfo['bars'].split(",")
        for bar in barList:
            lyData=LYAnalysis(crystal,runInfo,bar,len(barList))
            lyData.update({'tag':"%s"%tag})
            data={}
            data.update(crystalInfo)
            data.pop('runs',None)
            data.update(lyData)
            crystalsDB_withData['%s_%s_%s'%(crystal,tag,"BAR"+bar)]=data

##Save CSV using Pandas DataFrame
import pandas as pd
df=pd.DataFrame.from_dict(crystalsDB_withData,orient='index')
#df=df.drop(columns=['runs','refRuns'])
#df=df.drop(['runs','refRuns'],axis=1)
df=df[['producer','type','id','geometry','tag','temp','bar','posX','posY','ly','ctr','lyRef','ctrRef','xtLeft','xtRight']]
#df.to_csv('lyAnalysisTOFPET.csv',header=False)
print df
df.to_csv(args.output,header=False)
