import io
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--crys',dest='crys')
parser.add_argument('--runs',dest='runs')
parser.add_argument('--tag',dest='tag')
parser.add_argument('--id',dest='xtalid')
parser.add_argument('--refruns',dest='refRuns')
parser.add_argument('--prod',dest='producer')
parser.add_argument('--geom',dest='geometry')
parser.add_argument('--db',dest='db')

args = parser.parse_args()

crys=str(args.crys)
tag=str(args.tag)
xtalid=int(args.xtalid)
runs=str(args.runs).split(',')
refRuns=str(args.refRuns).split(',')
prod=str(args.producer)
geo=str(args.geometry)

if (int(crys.split('BAR0')[1]) != xtalid):
     print('ERROR. Check that ID %s matches crystal number %d'%(crys,xtalid))
     exit(-1)

import measDB
f=measDB.MeasDB(args.db)
f.insertMeas(crys,prod,geo,runs,refRuns,ledRuns,tag)

print('Runs for this xtal %s'%str(f.getMeas(crys)))
print('------ Number of crystals in DB %d ------'%len(f.getXtals()))

f.save()

