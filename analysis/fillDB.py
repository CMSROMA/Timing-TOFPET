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

for xt,runs in measurements.items():
    prod,geo=next(( ['prod%d'%x['fields']['VendorID'],x['fields']['Type'].lower()] for x in xtals if x['fields']['ID'] == xt), None)
    for day,rr in runs.items():
        runs=[ r['id'] for r in rr ]
        xtalID=int((xt.split('BAR'))[1])
        tag=rr[0]['tag']
        print(xt,prod,geo,xtalID,runs,refRuns['BARS'][day],tag)
        f.insertMeas(xt,prod,geo,rr[0]['type'],xtalID,runs,rr[0]['bars'],refRuns['BARS'][day],tag)

f.save()
