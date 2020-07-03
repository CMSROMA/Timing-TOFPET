import crystalsDB_Casaccia_Nov2019
import arraysDB_Casaccia_Nov2019
import measDB

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--db',dest='db')

args = parser.parse_args()

f=measDB.MeasDB(args.db)

for c,info in crystalsDB_Casaccia_Nov2019.crystalsDB.items():
    for r in info['runs']:
        f.insertMeas(c,info['producer'],info['geometry'],info['type'],info['id'],r['runs'],'1',r['refRuns'],r['tag'])

for c,info in arraysDB_Casaccia_Nov2019.crystalsDB.items():
    for r in info['runs']:
        f.insertMeas(c,info['producer'],info['geometry'],info['type'],info['id'],r['runs'],r['bars'],r['refRuns'],r['tag'])

f.save()
