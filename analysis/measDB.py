import json
import os

class MeasDB():
    def __init__(self, dbFile):
       self.dbFile=dbFile
       print('Opening '+dbFile)
       if (os.path.isfile(dbFile)):
           self.db=json.load(open(dbFile))
           print('Loaded MeasDB from '+dbFile)
       else:
           self.db=dict()

    def getDB(self):
        return self.db

    def getXtals(self):
        return sorted(self.db.keys())

    def getMeas(self,xtal):
        return [ '%s:%s,'%(str(r['tag']),str(r['runs'])) for r in self.db[xtal]['runs']]

    def insertMeas(self,crys,prod,geo,xtype,xtalid,runs,bars,refRuns,tag):
        if crys in self.db.keys():
            if (tag in [  r['tag'] for r in self.db[crys]['runs'] ]):
                print('ERROR. Tag %s already present'%tag)
            else:
                self.db[crys]['runs'].append({'tag':tag,'runs':runs, 'refRuns':refRuns})
                print('Tag %s for crystal %s inserted correctly. Total runs for this xtal %d'%(tag,crys,len(self.db[crys]['runs'])))
        else:
            self.db[crys]={ 'type':xtype,'producer':prod,'geometry':geo,'id':xtalid,'runs':[ {'tag':tag,'bars':bars,'runs':runs, 'refRuns':refRuns} ] } 
            print('Tag %s for crystal %s inserted correctly. Total runs for this xtal %d'%(tag,crys,len(self.db[crys]['runs'])))

    def save(self,fOut=''):
        if (fOut!=''):
            self.dbFile=fOut
        if(len(self.db)==0):
            return
        with open(self.dbFile, 'w') as file:
           file.write(json.dumps(self.db))
           print('Saved measDB into '+self.dbFile)

