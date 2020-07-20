import os
import threading
import time
import sys
import datetime
from airtable import Airtable

sys.path.insert(1, os.path.join(sys.path[0], '/home/cmsdaq/AutoProcess'))
import runDB

import logging
logging.basicConfig(format='%(asctime)s  %(filename)s  %(levelname)s: %(message)s',
                    level=logging.INFO)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--db',dest='db')
parser.add_argument('--start',dest='start')
parser.add_argument('--end',dest='end')

args = parser.parse_args()

import measDB
f=measDB.MeasDB(args.db)

runs=runDB.airtables['RUNS'].get_all()
xtals=runDB.airtables['Crystals'].get_all()

if (args.start == None):
    start=datetime.datetime.now().replace(minute=0, hour=0, second=0)
else:
    start=datetime.datetime.strptime(args.start,'%Y-%m-%d')

if (args.end == None):
    end=start + datetime.timedelta(days=1)
else:
    end=datetime.datetime.strptime(args.end,'%Y-%m-%d')

logging.info('Looking for runs from %s to %s'%(start.date(),end.date()))

from collections import defaultdict
refRuns={}
refRuns['BARS']=defaultdict(list)
refRuns['ARRAYS']=defaultdict(list)

for r in runs:
    if r['fields']['Processing status'] != 'VALIDATED':
        continue
    tR=datetime.datetime.strptime(r['fields']['Created'],'%Y-%m-%dT%H:%M:%S.%fZ')
    if  (tR<start or tR>end):
        continue
    if(r['fields']['Type']=='PHYS'):
        tags=r['fields']['TAG'].split('_')
        if ('BAR000028' in r['fields']['TAG']):
            refRuns['BARS'][tR.date()].append('tree_%s_%s'%(tags[0],tags[2]))
        if (('ARRAY000175' in tags[2]) and (tags[3] == 'POS1')):
            firstRun=int(tags[0].replace('Run',''))
            lastRun=firstRun+12 #assuming 5 measurements x array
            for r1 in runs:
                if ( int(r1['fields']['RunID'].replace('Run','')) == lastRun):
                    lastTags=r1['fields']['TAG'].split('_')
                    if ((r1['fields']['Processing status'] == 'VALIDATED' and lastTags[3] == 'POS5' and r['fields']['Crystal'] == r1['fields']['Crystal'])):
                        refRuns['ARRAYS'][tR.date()].append('tree_First%s_Last%s_%s'%(r['fields']['RunID'],r1['fields']['RunID'],tags[2]))
                        break

measurements=defaultdict(dict)

for r in runs:
    if r['fields']['Processing status'] != 'VALIDATED':
        continue
    tR=datetime.datetime.strptime(r['fields']['Created'],'%Y-%m-%dT%H:%M:%S.%fZ')
    if  (tR<start or tR>end):
        continue

    if(r['fields']['Type']=='PHYS'):
        tags=r['fields']['TAG'].split('_')
        if('BAR' in tags[2] and tags[2] != 'BAR000028'):
            xtalID=next((x['fields']['ID'] for x in xtals if x['id'] == (r['fields']['Crystal'])[0]), None)
            if (xtalID is None):
                logging.error('Xtal not found in Crystals table')
                continue

            if (xtalID == 'BAR000028'):
                logging.warning('Skip REF measurement %s not tagged as REF_DAILY'%r['fields']['RunID'])
                continue

            if (not tR.date() in measurements[xtalID].keys()):
                measurements[xtalID][tR.date()]=[{'id':'tree_%s_%s'%(tags[0],tags[2]),'tag':r['fields']['TAG'],'bars':'1','type':'xtal'}]
            else:
                measurements[xtalID][tR.date()].append({'id':'tree_%s_%s'%(tags[0],tags[2]),'tag':r['fields']['TAG'],'bars':'1','type':'xtal'})
        if('ARRAY' in tags[2] and tags[2] != 'ARRAY000175' and tags[3] == 'POS1'):
            xtalID=next((x['fields']['ID'] for x in xtals if x['id'] == (r['fields']['Crystal'])[0]), None)
            if (xtalID is None):
                logging.error('Array not found in Crystals table')
                continue

            if (xtalID == 'ARRAY000175'):
                logging.warning('Skip REF measurement %s not tagged as REF_DAILY'%r['fields']['RunID'])
                continue

            firstRun=int(tags[0].replace('Run',''))
            lastRun=firstRun+12 #assuming 5 measurements x array
            for r1 in runs:
                if ( int(r1['fields']['RunID'].replace('Run','')) == lastRun):
                    lastTags=r1['fields']['TAG'].split('_')
                    if ((r1['fields']['Processing status'] == 'VALIDATED' and lastTags[3] == 'POS5' and r['fields']['Crystal'] == r1['fields']['Crystal'])):
                        if (not tR.date() in measurements[xtalID].keys()):
                            measurements[xtalID][tR.date()]=[{'id':'tree_First%s_Last%s_%s'%(r['fields']['RunID'],r1['fields']['RunID'],tags[2]),'tag':r['fields']['TAG'],'bars':'1,2,3,4,5','type':'array'}]
                        else:
                            measurements[xtalID][tR.date()].append({'id':'tree_First%s_Last%s_%s'%(r['fields']['RunID'],r1['fields']['RunID'],tags[2]),'tag':r['fields']['TAG'],'bars':'1,2,3,4,5','type':'array'})
                        break

for xt,runs in measurements.items():
    prod,geo=next(( ['prod%d'%x['fields']['VendorID'],x['fields']['Type'].lower()] for x in xtals if x['fields']['ID'] == xt), None)
    for day,rr in runs.items():
        runs=[ r['id'] for r in rr ]
        if ('BAR' in xt):
            xtalID=int((xt.split('BAR'))[1])
            tag=rr[0]['tag']
            print(xt,prod,geo,xtalID,runs,refRuns['BARS'][day],tag)
            f.insertMeas(xt,prod,geo,rr[0]['type'],xtalID,runs,rr[0]['bars'],refRuns['BARS'][day],tag)
        elif ('ARRAY' in xt):
            xtalID=int((xt.split('ARRAY'))[1])
            tag=rr[0]['tag']
            print(xt,prod,geo,xtalID,runs,refRuns['ARRAYS'][day],tag)
            f.insertMeas(xt,prod,geo,rr[0]['type'],xtalID,runs,rr[0]['bars'],refRuns['ARRAYS'][day],tag)

f.save()
