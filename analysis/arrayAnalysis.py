#import ROOT as R
import math as m
import numpy as np
import time
import os
from array import array

from ROOT import *

def Analysis(myarray,runInfo,bar,lenght):
    #print "analyze myarray " + str(myarray) + " bar " + str(bar)+ " ..."
    files={}

    #test crystal
    barN, ly, ctr, temp, posX, posY, xtLeft, xtRight, xt = array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d')

    for r in runInfo['runs']:
        files[r]=TFile.Open(args.data+"/"+r+".root")
        treeInput = files[r].Get("results")
        nEntries = treeInput.GetEntries()
        if nEntries != 1:
            print "Bad Run (entries in the tree different from 1): "+r
            continue        

        treeInput.GetEntry(0)        

        barN.append(bar)
        ly.append(treeInput.peak1_mean_barCoinc[bar])
        ctr.append(treeInput.deltaT12_sigma_barCoinc[bar])
        temp.append(treeInput.temp_bar)
        posX.append(treeInput.pos_X)
        posY.append(treeInput.pos_Y)
        xtLeft.append(treeInput.XtalkLeft_median_barCoinc[bar])
        xtRight.append(treeInput.XtalkRight_median_barCoinc[bar])
        xt.append(treeInput.Xtalk_median_barCoinc[bar])

        files[r].Close()

    if len(barN)==0:
        print "No good bar info data for test array "+myarray+" bar "+bar
        barNAvg=-999.
    else:
        barNAvg=sum(barN)/len(barN)

    if len(ly)==0:
        print "No good LY data for test array "+myarray+" bar "+bar
        lyAvg=-999.
    else:
        lyAvg=sum(ly)/len(ly)

    if len(ctr)==0:
        print "No good time resolution for test array "+myarray+" bar "+bar
        ctrAvg=-999.
    else:
        ctrAvg=sum(ctr)/len(ctr)

    if len(temp)==0:
        print "No good temperature for test array "+myarray+" bar "+bar
        tempAvg=-999.
    else:
        tempAvg=sum(temp)/len(temp)

    if len(posX)==0:
        print "No good position X for test array "+myarray+" bar "+bar
        posXAvg=-999.
    else:
        posXAvg=sum(posX)/len(posX)

    if len(posY)==0:
        print "No good position Y for test array "+myarray+" bar "+bar
        posYAvg=-999.
    else:
        posYAvg=sum(posY)/len(posY)

    if len(xtLeft)==0:
        print "No xt left data for test array "+myarray+" bar "+bar
        xtLeftAvg=-999.
    else:
        xtLeftAvg=sum(xtLeft)/len(xtLeft)

    if len(xtRight)==0:
        print "No xt right data for test array "+myarray+" bar "+bar
        xtRightAvg=-999.
    else:
        xtRightAvg=sum(xtRight)/len(xtRight)

    if len(xt)==0:
        print "No xt data for test array "+myarray+" bar "+bar
        xtAvg=-999.
    else:
        xtAvg=sum(xt)/len(xt)


    #ref crystal
    lyRef, ctrRef = array('d'), array('d')
    for r in runInfo['refRuns']:
        files[r]=TFile.Open(args.data+"/"+r+".root")
        treeInput = files[r].Get("results")
        nEntries = treeInput.GetEntries()
        if nEntries != 1:
            print "Bad Run (entries in the tree different from 1): "+r
            continue        

        treeInput.GetEntry(0)        
        lyRef.append(treeInput.peak1_mean_barCoinc[bar])
        ctrRef.append(treeInput.deltaT12_sigma_barCoinc[bar])
        files[r].Close()

    if len(lyRef)==0:
        print "No good LY data for reference array "+myarray+" bar "+bar
        lyAvgRef=-999.
    else:
        lyAvgRef=sum(lyRef)/len(lyRef)

    if len(ctrRef)==0:
        print "No good time resolution for reference array "+myarray+" bar "+bar
        ctrAvgRef=-999.
    else:
        ctrAvgRef=sum(ctrRef)/len(ctrRef)

    #print "... DONE"

    return { 'bar': bar, 'ly':lyAvg, 'ctr':ctrAvg, 'temp':tempAvg, 'posX':posXAvg, 'posY':posYAvg, 'lyRef':lyAvgRef, 'ctrRef':ctrAvgRef, 'xtLeft':xtLeftAvg, 'xtRight':xtRightAvg, 'xt':xtAvg }

#--------------------------------------------------------

#use: python arrayAnalysis.py --output arraysDB_Milano_Sep2019.csv --db arraysDB_Milano_Sep2019 --data Results_ArrayMilano_08_09_2020/

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output',dest='output')
parser.add_argument('--db',dest='db')
parser.add_argument('--data',dest='data')
args = parser.parse_args()

exec "from %s import arraysDB" % args.db
#from arraysDB_Milano_Sep2019 import arraysDB

arraysDB_withData = {}

for myarray,arrayInfo in arraysDB.items():
    print myarray, arrayInfo
    print "Analysing array "+myarray
    for runInfo in arrayInfo['runs']:
        tag=runInfo['tag']
        barList=runInfo['bars'].split(",")
        for bar in barList:
            allData=Analysis(myarray,runInfo,int(bar),len(barList))
            allData.update({'tag':"%s"%tag})
            data={}
            data.update(arrayInfo)
            data.pop('runs',None)
            data.update(allData)
            arraysDB_withData['%s_%s_%s'%(myarray,tag,"BAR"+bar)]=data

##Save CSV using Pandas DataFrame
import pandas as pd
df=pd.DataFrame.from_dict(arraysDB_withData,orient='index')
df=df[['producer','type','id','geometry','tag','temp','bar','posX','posY','ly','ctr','lyRef','ctrRef','xtLeft','xtRight','xt']]
df.to_csv(args.output,header=False)

