import ROOT as R
R.gROOT.SetBatch(1)
from array import array
import math as mt
import numpy as np

#reading csv
crystalsData=R.TTree("crystalsData","crystalsData");
crystalsData.ReadFile("lyDB_SiPM.csv","name/C:prod/C:type/C:id/I:geo/C:tag/C:temp/F:barID/I:posX/F:posY/F:ly/F:ctr/F:lyRef/F:ctrRef/F:xtLeft/F:xtRight/F");
pixelRes = 90 #ps
outputdir = "plots"

#booking histos
producersJuly20 = [ 'prod'+str(i) for i in range(1,13) ]
producersPreIRR = [ 'prod'+str(i) for i in range(1,10) ]
geoms = [ 'geo'+str(i) for i in range(1,4) ]

objIRR = [176,177,178,179,180,181,182,183,184,27,33,40,41,42,43,55,56,57,58,69,70,71,77,78,79,80,91,92,93,94,106,107,108,109,121,122,123,124,145,146,147,148,149,160,161,162,163,164,318]
objToBlacklist = [58, 318,170,193,194,195,196,197,198,199,200,201,202,203,204,205] #blacklisted either b/c run wrongly validate (318) or b/c are special cristals. 58 b/c strange value maybe wrong measured
objNew = [306,305,307,308,324,325,326,327,328,329,332,333,334,335,314,315,316,317,318,280,281,282,341,342,343] #these are new from prod3,4,5,6
objIRR50K = [176,177,178,179,180,181,182,183,184] #irradiated Nov19 at ~50K
objIRR50KNew = [305,324,326,328] #irradiated July 20 at ~50K

histos = {}
data = {}

for prod in producersJuly20: 
    histos['ly_'+prod]=R.TH1F('ly_'+prod,'ly_'+prod,100,0.,60.)
    histos['lyNorm_'+prod]=R.TH1F('lyNorm_'+prod,'lyNorm_'+prod,400,0.5,1.5)
    histos['ctr_'+prod]=R.TH1F('ctr_'+prod,'ctr_'+prod,100,0.,220.)
    histos['ctrNorm_'+prod]=R.TH1F('ctrNorm_'+prod,'ctrNorm_'+prod,100,0.,220.)
    for geo in geoms:
        histos['ly_'+prod+'_'+geo]=R.TH1F('ly_'+prod+'_'+geo,'ly_'+prod+'_'+geo,100,0.,60.)
        histos['lyNorm_'+prod+'_'+geo]=R.TH1F('lyNorm_'+prod+'_'+geo,'lyNorm_'+prod+'_'+geo,400,0.5,1.5)
        histos['ctr_'+prod+'_'+geo]=R.TH1F('ctr_'+prod+'_'+geo,'ctr_'+prod+'_'+geo,100,0.,220.)
        histos['ctrNorm_'+prod+'_'+geo]=R.TH1F('ctrNorm_'+prod+'_'+geo,'ctrNorm_'+prod+'_'+geo,100,0.,220.)
        data[prod+'_'+geo] = []



################################################################################################################
#create dictionary with data pre-irradiation at casaccia
dataPreIRR = {}
dataPreIRRAll = {}
for prod in producersJuly20: 
    dataPreIRR[prod] = []
    dataPreIRRAll[prod] = []

for crys in crystalsData:
    if ( crys.ly < 0. or crys.ctr < 0. or crys.lyRef < 0. or crys.ctrRef < 0.):
        continue
    prod = crys.prod.rstrip('\x00')
    tag = crys.tag.rstrip('\x00')
    prodN = int(prod.strip('prod'))
    
    #from November measurement objects before irradiation excluding array/bars for which producer has re-sent them (today 28.7.20 are 3,4,5 for array and 4,5,6 for bars)
    if("IRR0" in tag and crys.id not in objToBlacklist and (('array' in crys.type and prodN !=3 and prodN!= 5 and prodN !=4 and  prodN <10) or ('xtal' in crys.type and prodN != 4 and prodN!=5 and prodN!=6))): 
        dataPreIRR[prod].append({'name':crys.name, 'type':crys.type, 'geo' :crys.geo, 'id':crys.id,'barID': crys.barID,  'ly': crys.ly, 'lyNorm': crys.ly/crys.lyRef, 'sigmat': mt.sqrt(crys.ctr**2-pixelRes**2), 'sigmatNorm': mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2), 'xtLeft': crys.xtLeft, 'xtRight': crys.xtRight})

    #from November measurement objects before irradiation (all) - needed for brakdown plot
    if("IRR0" in tag and crys.id not in objToBlacklist): 
        dataPreIRRAll[prod].append({'name':crys.name, 'type':crys.type, 'geo' :crys.geo, 'id':crys.id,'barID': crys.barID,  'ly': crys.ly, 'lyNorm': crys.ly/crys.lyRef, 'sigmat': mt.sqrt(crys.ctr**2-pixelRes**2), 'sigmatNorm': mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2), 'xtLeft': crys.xtLeft, 'xtRight': crys.xtRight})


################################################################################################################
#create dictionary for irradiated arrays at 50K(9Kx5H or 3Kx16H) 
dataIRR50K = {}
dataIRR50KNew = {}
for prod in producersJuly20: 
    dataIRR50K[prod] = []
    dataIRR50KNew[prod] = []

for crys in crystalsData:
    if ( crys.ly < 0. or crys.ctr < 0. or crys.lyRef < 0. or crys.ctrRef < 0.):
        continue
    #considering only array 
    if ('xtal' in crys.type):
        continue
    prod = crys.prod.rstrip('\x00')
    tag = crys.tag.rstrip('\x00')
    prodN = int(prod.strip('prod'))
    
    #use only array in objIRR50K list Nov19 when irradiated - exclude 3,4,5 b/c they re-sent arrays which we re-irradiated
    
    if(crys.id in objIRR50K and crys.id not in objToBlacklist and ('9K' in crys.tag or '3K' in crys.tag) and prodN!=3 and prodN!=4 and prodN!=5): 
        dataIRR50K[prod].append({'name':crys.name, 'type':crys.type, 'geo' :crys.geo, 'id':crys.id,'barID': crys.barID,  'ly': crys.ly, 'lyNorm': crys.ly/crys.lyRef, 'sigmat': mt.sqrt(crys.ctr**2-pixelRes**2), 'sigmatNorm': mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2), 'xtLeft': crys.xtLeft, 'xtRight': crys.xtRight})

    #use only array in objIRR50KNew list Jul20
    
    if((crys.id in objIRR50KNew and "07-28" in tag) and crys.id not in objToBlacklist): #we measured irradiated array in July20 all of them on 28/7/20
        dataIRR50KNew[prod].append({'name':crys.name, 'type':crys.type, 'geo' :crys.geo, 'id':crys.id,'barID': crys.barID,  'ly': crys.ly, 'lyNorm': crys.ly/crys.lyRef, 'sigmat': mt.sqrt(crys.ctr**2-pixelRes**2), 'sigmatNorm': mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2), 'xtLeft': crys.xtLeft, 'xtRight': crys.xtRight})


#merge irradiated dictionaries in a global one
dsIRR = [dataIRR50K, dataIRR50KNew]
dataIRR = {}
for k in dataIRR50K.keys():
  dataIRR[k] = np.concatenate(list(dataIRR[k] for dataIRR in dsIRR))


################################################################################################################

#create dictionary with data from July20 w/o irradiated

dataJuly20 = {}
dataJuly20New = {}

for prod in producersJuly20: 
    dataJuly20[prod] = []
    dataJuly20New[prod] = []

for crys in crystalsData:
    if ( crys.ly < 0. or crys.ctr < 0. or crys.lyRef < 0. or crys.ctrRef < 0.):
        continue
    prod = crys.prod.rstrip('\x00')
    tag = crys.tag.rstrip('\x00')
    prodN = int(prod.strip('prod'))
    
    #from July measurement exclude now irradiated objects and array/bars for which producer has re-sent them (today 23.7.20 are 3,4,5 and 4,5,6 for bars)
    if("Run00" in tag and (crys.id not in objIRR50KNew or (crys.id  in objIRR50KNew and "07-28" not in tag))  and crys.id not in objIRR and crys.id not in objToBlacklist and (('array' in crys.type and prodN !=3 and prodN!=5 and prodN !=4 and  prodN <10) or ('xtal' in crys.type and prodN <10 and prodN!=4 and prodN!= 5 and prodN!=6))):
        dataJuly20[prod].append({'name':crys.name, 'type':crys.type, 'geo' :crys.geo, 'id':crys.id,'barID': crys.barID,  'ly': crys.ly, 'lyNorm': crys.ly/crys.lyRef, 'sigmat': mt.sqrt(crys.ctr**2-pixelRes**2), 'sigmatNorm': mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2), 'xtLeft': crys.xtLeft, 'xtRight': crys.xtRight})
        
    if("Run00" in tag and (crys.id not in objIRR50KNew or (crys.id  in objIRR50KNew and "07-28" not in tag)) and crys.id not in objIRR and (crys.id in objNew or prodN >9) and crys.id not in objToBlacklist):
        dataJuly20New[prod].append({'name':crys.name, 'type':crys.type, 'geo' :crys.geo, 'id':crys.id,'barID': crys.barID,  'ly': crys.ly, 'lyNorm': crys.ly/crys.lyRef, 'sigmat': mt.sqrt(crys.ctr**2-pixelRes**2), 'sigmatNorm': mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2), 'xtLeft': crys.xtLeft, 'xtRight': crys.xtRight})


#merge not irradiated dictionaries in a global one
ds = [dataPreIRR, dataJuly20,dataJuly20New]
data = {}
for k in dataPreIRR.keys():
  data[k] = np.concatenate(list(data[k] for data in ds))
################################################################################################################



###########
#Make plots
###########

#Create graphs
graphs=['lyAll','lyNormAll','sigmatAll','sigmatNormAll','xtAll','lyNew','lyNormNew','sigmatNew','sigmatNormNew','xtNew','ly','lyNorm','sigmat','sigmatNorm','xt','ly_bars','lyNorm_bars','sigmat_bars','sigmatNorm_bars','xt_bars','lyAll_bars','lyNormAll_bars','sigmatAll_bars','sigmatNormAll_bars','xtAll_bars','lyNew_bars','lyNormNew_bars','sigmatNew_bars','sigmatNormNew_bars','xtNew_bars','lyIRR','lyNormIRR','sigmatIRR','sigmatNormIRR','xtIRR','RATIO_ly','RATIO_lyNorm','RATIO_sigmat','RATIO_sigmatNorm','RATIO_xt']


for g in graphs:
    histos[g+'VsProd']=R.TGraphErrors(len(producersJuly20)) 
    histos[g+'VsProd'].SetName(g+'VsProd')
    histos[g+'VsProd'].SetTitle(g+'VsProd')
    histos[g+'VsProd'].SetMarkerSize(1.4)
    histos[g+'VsProd'].GetXaxis().SetTitle("     Producer")
    histos[g+'VsProd'].GetXaxis().SetTitleSize(0.1)
    histos[g+'VsProd'].GetXaxis().SetLabelSize(0.1)
    histos[g+'VsProd'].GetXaxis().SetLabelOffset(0.035)
    histos[g+'VsProd'].GetXaxis().SetTitleOffset(1.2)
    histos['2D_'+g+'VsProd']=R.TGraphErrors(len(producersJuly20)) 
    for prod in producersJuly20:
        prodN = int(prod.strip('prod')) 
        histos['2D_'+g+'_forProd_'+prod]=R.TGraphErrors(len(producersJuly20)) 
        histos['2D_'+g+'_forProd_'+prod].SetName('2D_'+g+'VsProd')
        histos['2D_'+g+'_forProd_'+prod].SetTitle('2D_'+g+'VsProd')
        histos['2D_'+g+'_forProd_'+prod].SetMarkerSize(1.2)
        histos['2D_'+g+'_forProd_'+prod].SetMarkerStyle(20)
        histos['2D_'+g+'_forProd_'+prod].SetLineWidth(2)
        histos['2D_'+g+'_forProd_'+prod].SetMarkerColor(prodN-1)
        histos['2D_'+g+'_forProd_'+prod].SetLineColor(prodN-1)
            
        histos['2D_'+g+'_forProd_'+prod].GetXaxis().SetTitle("     Producer")
        histos['2D_'+g+'_forProd_'+prod].GetXaxis().SetTitleSize(0.1)
        histos['2D_'+g+'_forProd_'+prod].GetXaxis().SetLabelSize(0.1)
        histos['2D_'+g+'_forProd_'+prod].GetXaxis().SetLabelOffset(0.035)
        histos['2D_'+g+'_forProd_'+prod].GetXaxis().SetTitleOffset(1.2)



#Loop over producers 
for iprod,prod in enumerate(producersJuly20): 
    print("#### %s ####"%prod)
    prodN = int(prod.strip('prod'))    

    #create arrays: for each prod an array for bars in array and an array for all bars 
    lyAll=array('d')    
    lyNormAll=array('d')    
    sigmatAll=array('d')    
    sigmatNormAll=array('d')    
    xtLeftAll=array('d')
    xtRightAll=array('d')
    lyAll_bars=array('d')    
    lyNormAll_bars=array('d')    
    sigmatAll_bars=array('d')    
    sigmatNormAll_bars=array('d')

    lyNew=array('d')    
    lyNormNew=array('d')    
    sigmatNew=array('d')    
    sigmatNormNew=array('d')    
    xtLeftNew=array('d')
    xtRightNew=array('d')
    lyNew_bars=array('d')    
    lyNormNew_bars=array('d')    
    sigmatNew_bars=array('d')    
    sigmatNormNew_bars=array('d')

    ly=array('d')    
    lyNorm=array('d')    
    sigmat=array('d')    
    sigmatNorm=array('d')    
    xtLeft=array('d')
    xtRight=array('d')
    ly_bars=array('d')    
    lyNorm_bars=array('d')    
    sigmat_bars=array('d')    
    sigmatNorm_bars=array('d')    


    #print "--------------------- PreIRRAll --------------------------" #blue markers
    for i,meas in enumerate(dataPreIRRAll[prod]):
        if("geo3" in meas['geo'] and "xtal" in meas['type']and prodN==1):
#
	    lyAll_bars.append(meas['ly']*0.96)
            lyNormAll_bars.append(meas['lyNorm']*0.96)
            sigmatAll_bars.append(meas['sigmat']*0.99)
            sigmatNormAll_bars.append(meas['sigmatNorm']*0.99)
        if("geo2" in meas['geo']):
        #    print meas['type'],meas['geo'],meas['id'],meas['barID'],meas['ly']
            if("array" in meas['type']):
                lyAll.append(meas['ly'])
                lyNormAll.append(meas['lyNorm'])
                sigmatAll.append(meas['sigmat'])
                sigmatNormAll.append(meas['sigmatNorm'])
                if (meas['xtLeft']>0):
                    xtLeftAll.append(meas['xtLeft'])
                if (meas['xtRight']>0):
                    xtRightAll.append(meas['xtRight'])
               #     print prod,i,meas['ly']
            if("xtal" in meas['type']):
                lyAll_bars.append(meas['ly'])
                lyNormAll_bars.append(meas['lyNorm'])
                sigmatAll_bars.append(meas['sigmat'])
                sigmatNormAll_bars.append(meas['sigmatNorm'])
    #print "--------------------- PreIRR --------------------------" #blue markers
    #for i,meas in enumerate(dataPreIRR[prod]):
    #    if("geo2" in meas['geo']):
        #    print meas['type'],meas['geo'],meas['id'],meas['barID'],meas['ly']
    print "--------------------- July20New -----------------------" #pink markers
    for i,meas in enumerate(dataJuly20New[prod]):
        if("geo2" in meas['geo']):
        #    print meas['type'],meas['geo'],meas['id'],meas['barID'],meas['ly']
            if("array" in meas['type']):
                lyNew.append(meas['ly'])
                lyNormNew.append(meas['lyNorm'])
                sigmatNew.append(meas['sigmat'])
                sigmatNormNew.append(meas['sigmatNorm'])
                if (meas['xtLeft']>0):
                    xtLeftNew.append(meas['xtLeft'])
                if (meas['xtRight']>0):
                    xtRightNew.append(meas['xtRight'])
               #     print prod,i,meas['ly']
            if("xtal" in meas['type']):
                lyNew_bars.append(meas['ly'])
                lyNormNew_bars.append(meas['lyNorm'])
                sigmatNew_bars.append(meas['sigmat'])
                sigmatNormNew_bars.append(meas['sigmatNorm'])
                
    print "--------------------- Global --------------------------" #black markers
    #loop on bars of same geometry (i look only at geo2 for now) eithr within the array or single bars
    for i,meas in enumerate(data[prod]):
        if("geo3" in meas['geo'] and "xtal" in meas['type']and prodN==1):
            print meas['type'],meas['geo'],meas['id'],meas['barID'],meas['ly']
	    ly_bars.append(meas['ly']*0.96)
            lyNorm_bars.append(meas['lyNorm']*0.96)
            sigmat_bars.append(meas['sigmat']*0.99)
            sigmatNorm_bars.append(meas['sigmatNorm']*0.99)
        if("geo2" in meas['geo']):
         #   print meas['type'],meas['geo'],meas['id'],meas['barID'],meas['ly']
            if("array" in meas['type']):
                ly.append(meas['ly'])
                lyNorm.append(meas['lyNorm'])
                sigmat.append(meas['sigmat'])
                sigmatNorm.append(meas['sigmatNorm'])
                if (meas['xtLeft']>0):
                    xtLeft.append(meas['xtLeft'])
                if (meas['xtRight']>0):
                    xtRight.append(meas['xtRight'])
               #     print prod,i,meas['ly']
            if("xtal" in meas['type']):
                ly_bars.append(meas['ly'])
                lyNorm_bars.append(meas['lyNorm'])
                sigmat_bars.append(meas['sigmat'])
                sigmatNorm_bars.append(meas['sigmatNorm'])
                
              #  print prod,i,meas['ly']
    
    lyAll_np = np.array(lyAll)
    mean_lyAll = lyAll_np.mean()
    std_lyAll = lyAll_np.std()
        
    lyNormAll_np = np.array(lyNormAll)
    mean_lyNormAll = lyNormAll_np.mean()
    std_lyNormAll = lyNormAll_np.std()

    sigmatAll_np = np.array(sigmatAll)
    mean_sigmatAll = sigmatAll_np.mean()
    std_sigmatAll = sigmatAll_np.std()

    sigmatNormAll_np = np.array(sigmatNormAll)
    mean_sigmatNormAll = sigmatNormAll_np.mean()
    std_sigmatNormAll = sigmatNormAll_np.std()

    xtLeftAll_np = np.array(xtLeftAll)
    mean_xtLeftAll = xtLeftAll_np.mean()
    std_xtLeftAll = xtLeftAll_np.std()

    xtRightAll_np = np.array(xtRightAll)
    mean_xtRightAll = xtRightAll_np.mean()
    std_xtRightAll = xtRightAll_np.std()

    mean_xtAll = mean_xtLeftAll + mean_xtRightAll
    std_xtAll = mt.sqrt(std_xtLeftAll**2 +std_xtRightAll**2)


    lyAll_bars_np = np.array(lyAll_bars)
    mean_lyAll_bars = lyAll_bars_np.mean()
    std_lyAll_bars = lyAll_bars_np.std()
        
    lyNormAll_bars_np = np.array(lyNormAll_bars)
    mean_lyNormAll_bars = lyNormAll_bars_np.mean()
    std_lyNormAll_bars = lyNormAll_bars_np.std()

    sigmatAll_bars_np = np.array(sigmatAll_bars)
    mean_sigmatAll_bars = sigmatAll_bars_np.mean()
    std_sigmatAll_bars = sigmatAll_bars_np.std()

    sigmatNormAll_bars_np = np.array(sigmatNormAll_bars)
    mean_sigmatNormAll_bars = sigmatNormAll_bars_np.mean()
    std_sigmatNormAll_bars = sigmatNormAll_bars_np.std()

   
    
    histos['lyAll'+'VsProd'].SetPoint(iprod,prodN,mean_lyAll)
    histos['lyAll'+'VsProd'].SetPointError(iprod,0.,std_lyAll)

    histos['lyNormAll'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormAll)
    histos['lyNormAll'+'VsProd'].SetPointError(iprod,0.,std_lyNormAll)

    histos['sigmatAll'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatAll)
    histos['sigmatAll'+'VsProd'].SetPointError(iprod,0.,std_sigmatAll)

    histos['sigmatNormAll'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormAll)
    histos['sigmatNormAll'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormAll)

    histos['xtAll'+'VsProd'].SetPoint(iprod,prodN,mean_xtAll)
    histos['xtAll'+'VsProd'].SetPointError(iprod,0.,std_xtAll)

    histos['lyAll_bars'+'VsProd'].SetPoint(iprod,prodN,mean_lyAll_bars)
    histos['lyAll_bars'+'VsProd'].SetPointError(iprod,0.,std_lyAll_bars)

    histos['lyNormAll_bars'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormAll_bars)
    histos['lyNormAll_bars'+'VsProd'].SetPointError(iprod,0.,std_lyNormAll_bars)

    histos['sigmatAll_bars'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatAll_bars)
    histos['sigmatAll_bars'+'VsProd'].SetPointError(iprod,0.,std_sigmatAll_bars)

    histos['sigmatNormAll_bars'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormAll_bars)
    histos['sigmatNormAll_bars'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormAll_bars)


    lyNew_np = np.array(lyNew)
    mean_lyNew = lyNew_np.mean()
    std_lyNew = lyNew_np.std()
        
    lyNormNew_np = np.array(lyNormNew)
    mean_lyNormNew = lyNormNew_np.mean()
    std_lyNormNew = lyNormNew_np.std()

    sigmatNew_np = np.array(sigmatNew)
    mean_sigmatNew = sigmatNew_np.mean()
    std_sigmatNew = sigmatNew_np.std()

    sigmatNormNew_np = np.array(sigmatNormNew)
    mean_sigmatNormNew = sigmatNormNew_np.mean()
    std_sigmatNormNew = sigmatNormNew_np.std()

    xtLeftNew_np = np.array(xtLeftNew)
    mean_xtLeftNew = xtLeftNew_np.mean()
    std_xtLeftNew = xtLeftNew_np.std()

    xtRightNew_np = np.array(xtRightNew)
    mean_xtRightNew = xtRightNew_np.mean()
    std_xtRightNew = xtRightNew_np.std()

    mean_xtNew = mean_xtLeftNew + mean_xtRightNew
    std_xtNew = mt.sqrt(std_xtLeftNew**2 +std_xtRightNew**2)


    lyNew_bars_np = np.array(lyNew_bars)
    mean_lyNew_bars = lyNew_bars_np.mean()
    std_lyNew_bars = lyNew_bars_np.std()
        
    lyNormNew_bars_np = np.array(lyNormNew_bars)
    mean_lyNormNew_bars = lyNormNew_bars_np.mean()
    std_lyNormNew_bars = lyNormNew_bars_np.std()

    sigmatNew_bars_np = np.array(sigmatNew_bars)
    mean_sigmatNew_bars = sigmatNew_bars_np.mean()
    std_sigmatNew_bars = sigmatNew_bars_np.std()

    sigmatNormNew_bars_np = np.array(sigmatNormNew_bars)
    mean_sigmatNormNew_bars = sigmatNormNew_bars_np.mean()
    std_sigmatNormNew_bars = sigmatNormNew_bars_np.std()

   
    
    histos['lyNew'+'VsProd'].SetPoint(iprod,prodN,mean_lyNew)
    histos['lyNew'+'VsProd'].SetPointError(iprod,0.,std_lyNew)

    histos['lyNormNew'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormNew)
    histos['lyNormNew'+'VsProd'].SetPointError(iprod,0.,std_lyNormNew)

    histos['sigmatNew'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNew)
    histos['sigmatNew'+'VsProd'].SetPointError(iprod,0.,std_sigmatNew)

    histos['sigmatNormNew'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormNew)
    histos['sigmatNormNew'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormNew)

    histos['xtNew'+'VsProd'].SetPoint(iprod,prodN,mean_xtNew)
    histos['xtNew'+'VsProd'].SetPointError(iprod,0.,std_xtNew)

    histos['lyNew_bars'+'VsProd'].SetPoint(iprod,prodN,mean_lyNew_bars)
    histos['lyNew_bars'+'VsProd'].SetPointError(iprod,0.,std_lyNew_bars)

    histos['lyNormNew_bars'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormNew_bars)
    histos['lyNormNew_bars'+'VsProd'].SetPointError(iprod,0.,std_lyNormNew_bars)

    histos['sigmatNew_bars'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNew_bars)
    histos['sigmatNew_bars'+'VsProd'].SetPointError(iprod,0.,std_sigmatNew_bars)

    histos['sigmatNormNew_bars'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormNew_bars)
    histos['sigmatNormNew_bars'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormNew_bars)


    ly_np = np.array(ly)
    mean_ly = ly_np.mean()
    std_ly = ly_np.std()
        
    lyNorm_np = np.array(lyNorm)
    mean_lyNorm = lyNorm_np.mean()
    std_lyNorm = lyNorm_np.std()

    sigmat_np = np.array(sigmat)
    mean_sigmat = sigmat_np.mean()
    std_sigmat = sigmat_np.std()

    sigmatNorm_np = np.array(sigmatNorm)
    mean_sigmatNorm = sigmatNorm_np.mean()
    std_sigmatNorm = sigmatNorm_np.std()

    xtLeft_np = np.array(xtLeft)
    mean_xtLeft = xtLeft_np.mean()
    std_xtLeft = xtLeft_np.std()

    xtRight_np = np.array(xtRight)
    mean_xtRight = xtRight_np.mean()
    std_xtRight = xtRight_np.std()

    mean_xt = mean_xtLeft + mean_xtRight
    std_xt = mt.sqrt(std_xtLeft**2 +std_xtRight**2)


    ly_bars_np = np.array(ly_bars)
    mean_ly_bars = ly_bars_np.mean()
    std_ly_bars = ly_bars_np.std()
        
    lyNorm_bars_np = np.array(lyNorm_bars)
    mean_lyNorm_bars = lyNorm_bars_np.mean()
    std_lyNorm_bars = lyNorm_bars_np.std()

    sigmat_bars_np = np.array(sigmat_bars)
    mean_sigmat_bars = sigmat_bars_np.mean()
    std_sigmat_bars = sigmat_bars_np.std()

    sigmatNorm_bars_np = np.array(sigmatNorm_bars)
    mean_sigmatNorm_bars = sigmatNorm_bars_np.mean()
    std_sigmatNorm_bars = sigmatNorm_bars_np.std()

   
    
    histos['ly'+'VsProd'].SetPoint(iprod,prodN,mean_ly)
    histos['ly'+'VsProd'].SetPointError(iprod,0.,std_ly)

    histos['lyNorm'+'VsProd'].SetPoint(iprod,prodN,mean_lyNorm)
    histos['lyNorm'+'VsProd'].SetPointError(iprod,0.,std_lyNorm)

    histos['sigmat'+'VsProd'].SetPoint(iprod,prodN,mean_sigmat)
    histos['sigmat'+'VsProd'].SetPointError(iprod,0.,std_sigmat)

    histos['sigmatNorm'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNorm)
    histos['sigmatNorm'+'VsProd'].SetPointError(iprod,0.,std_sigmatNorm)

    histos['xt'+'VsProd'].SetPoint(iprod,prodN,mean_xt)
    histos['xt'+'VsProd'].SetPointError(iprod,0.,std_xt)

    histos['ly_bars'+'VsProd'].SetPoint(iprod,prodN,mean_ly_bars)
    histos['ly_bars'+'VsProd'].SetPointError(iprod,0.,std_ly_bars)

    histos['lyNorm_bars'+'VsProd'].SetPoint(iprod,prodN,mean_lyNorm_bars)
    histos['lyNorm_bars'+'VsProd'].SetPointError(iprod,0.,std_lyNorm_bars)

    histos['sigmat_bars'+'VsProd'].SetPoint(iprod,prodN,mean_sigmat_bars)
    histos['sigmat_bars'+'VsProd'].SetPointError(iprod,0.,std_sigmat_bars)

    histos['sigmatNorm_bars'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNorm_bars)
    histos['sigmatNorm_bars'+'VsProd'].SetPointError(iprod,0.,std_sigmatNorm_bars)

    #2D plots for correlation bar vs array
    histos['2D_ly'+'VsProd'].SetPoint(iprod,mean_ly,mean_ly_bars)
    histos['2D_ly'+'VsProd'].SetPointError(iprod,std_ly,std_ly_bars)
    histos['2D_lyNorm'+'VsProd'].SetPoint(iprod,mean_lyNorm,mean_lyNorm_bars)
    histos['2D_lyNorm'+'VsProd'].SetPointError(iprod,std_lyNorm,std_lyNorm_bars)
    histos['2D_sigmat'+'VsProd'].SetPoint(iprod,mean_sigmat,mean_sigmat_bars)
    histos['2D_sigmat'+'VsProd'].SetPointError(iprod,std_sigmat,std_sigmat_bars)
    histos['2D_sigmatNorm'+'VsProd'].SetPoint(iprod,mean_sigmatNorm,mean_sigmatNorm_bars)
    histos['2D_sigmatNorm'+'VsProd'].SetPointError(iprod,std_sigmatNorm,std_sigmatNorm_bars)

    histos['2D_ly'+'_forProd_'+prod].SetPoint(iprod,mean_ly,mean_ly_bars)
    histos['2D_ly'+'_forProd_'+prod].SetPointError(iprod,std_ly,std_ly_bars)
    histos['2D_lyNorm'+'_forProd_'+prod].SetPoint(iprod,mean_lyNorm,mean_lyNorm_bars)
    histos['2D_lyNorm'+'_forProd_'+prod].SetPointError(iprod,std_lyNorm,std_lyNorm_bars)
    histos['2D_sigmat'+'_forProd_'+prod].SetPoint(iprod,mean_sigmat,mean_sigmat_bars)
    histos['2D_sigmat'+'_forProd_'+prod].SetPointError(iprod,std_sigmat,std_sigmat_bars)
    histos['2D_sigmatNorm'+'_forProd_'+prod].SetPoint(iprod,mean_sigmatNorm,mean_sigmatNorm_bars)
    histos['2D_sigmatNorm'+'_forProd_'+prod].SetPointError(iprod,std_sigmatNorm,std_sigmatNorm_bars)
    
#######################################################################################################################################


#Loop over producers 
for iprod,prod in enumerate(producersJuly20): 
    print("#### %s ####"%prod)
    prodN = int(prod.strip('prod'))    

    #create arrays: for each prod an array for bars in array and an array for all bars 
    lyIRR=array('d')    
    lyNormIRR=array('d')    
    sigmatIRR=array('d')    
    sigmatNormIRR=array('d')    
    xtLeftIRR=array('d')
    xtRightIRR=array('d')
    print "--------------------- IRRADIATED --------------------------" #red markers
    #loop on bars of same geometry (i look only at geo2 for now) eithr within the array or single bars
    for i,meas in enumerate(dataIRR[prod]):
        if("geo2" in meas['geo']):
            print meas['type'],meas['geo'],meas['id'],meas['barID'],meas['ly']
            if("array" in meas['type']):
                lyIRR.append(meas['ly'])
                lyNormIRR.append(meas['lyNorm'])
                sigmatIRR.append(meas['sigmat'])
                sigmatNormIRR.append(meas['sigmatNorm'])
                if (meas['xtLeft']>0):
                    xtLeftIRR.append(meas['xtLeft'])
                if (meas['xtRight']>0):
                    xtRightIRR.append(meas['xtRight'])
        
    lyIRR_np = np.array(lyIRR)
    mean_lyIRR = lyIRR_np.mean()
 #   std_lyIRR = lyIRR_np.std()/mt.sqrt(len(lyIRR))
    std_lyIRR = lyIRR_np.std()
    
        
    lyNormIRR_np = np.array(lyNormIRR)
    mean_lyNormIRR = lyNormIRR_np.mean()
 #   std_lyNormIRR = lyNormIRR_np.std()/mt.sqrt(len(lyNormIRR))
    std_lyNormIRR = lyNormIRR_np.std()

    sigmatIRR_np = np.array(sigmatIRR)
    mean_sigmatIRR = sigmatIRR_np.mean()
#    std_sigmatIRR = sigmatIRR_np.std()/mt.sqrt(len(sigmatIRR))
    std_sigmatIRR = sigmatIRR_np.std()

    sigmatNormIRR_np = np.array(sigmatNormIRR)
    mean_sigmatNormIRR = sigmatNormIRR_np.mean()
#    std_sigmatNorm = sigmatNorm_np.std()/mt.sqrt(len(sigmatNorm))
    std_sigmatNormIRR = sigmatNormIRR_np.std()

    xtLeftIRR_np = np.array(xtLeftIRR)
    mean_xtLeftIRR = xtLeftIRR_np.mean()
#    std_xtLeft = xtLeft_np.std()/mt.sqrt(len(xtLeft))
    std_xtLeftIRR = xtLeftIRR_np.std()

    xtRightIRR_np = np.array(xtRightIRR)
    mean_xtRightIRR = xtRightIRR_np.mean()
#    std_xtRight = xtRight_np.std()/mt.sqrt(len(xtRight))
    std_xtRightIRR = xtRightIRR_np.std()

    mean_xtIRR = mean_xtLeftIRR + mean_xtRightIRR
    std_xtIRR = mt.sqrt(std_xtLeftIRR**2 +std_xtRightIRR**2)

   
    
    histos['lyIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyIRR)
    histos['lyIRR'+'VsProd'].SetPointError(iprod,0.,std_lyIRR)

    histos['lyNormIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormIRR)
    histos['lyNormIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormIRR)

    histos['sigmatIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatIRR)
    histos['sigmatIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatIRR)

    histos['sigmatNormIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormIRR)
    histos['sigmatNormIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormIRR)

    histos['xtIRR'+'VsProd'].SetPoint(iprod,prodN,mean_xtIRR)
    histos['xtIRR'+'VsProd'].SetPointError(iprod,0.,std_xtIRR)

  

############################################################################### PLOTTING PART ######################################################################################


    
#Draw and Save plots
R.gStyle.SetOptTitle(0)
R.gStyle.SetOptStat(0)
c1=R.TCanvas("c1","c1",800,800)
legend1 = R.TLegend(0.45,0.6,0.9,0.9)
text1=R.TLatex()
text1.SetTextSize(0.04)


###################################################################### plots for non irradiated ARRAYS ##############################################################################################

#ly
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(38,102)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY [ADC counts]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['ly'+'VsProd'].SetMarkerStyle(20)
histos['ly'+'VsProd'].SetMarkerColor(1)
histos['ly'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['ly'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'ARRAY_ly'+'VsProd'+ext)




#lyNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.5,1.5)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY / LY_{ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['lyNorm'+'VsProd'].SetMarkerStyle(20)
histos['lyNorm'+'VsProd'].SetMarkerColor(1)
histos['lyNorm'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['lyNorm'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'ARRAY_lyNorm'+'VsProd'+ext)

c1.SetGrid()
histos['lyNormIRR'+'VsProd'].SetMarkerStyle(22)
histos['lyNormIRR'+'VsProd'].SetMarkerColor(2)
histos['lyNormIRR'+'VsProd'].Draw("psame")
legend1.AddEntry(histos['lyIRR'+'VsProd'],"Array Nov19 + July20 Irrad. ","pe")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_lyNormIRR'+'VsProd'+ext)



    
#sigmat
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(100,200)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} [ps]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmat'+'VsProd'].SetMarkerStyle(20)
histos['sigmat'+'VsProd'].SetMarkerColor(1)
histos['sigmat'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmat'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'ARRAY_sigmat'+'VsProd'+ext)

c1.SetGrid()
histos['sigmatIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatIRR'+'VsProd'].Draw("psame")
legend1.AddEntry(histos['sigmatIRR'+'VsProd'],"Array Nov19 + July20  Irrad. ","pe")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_sigmatIRR'+'VsProd'+ext)


    
#sigmatNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0,2)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} / #sigma_{T,ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmatNorm'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNorm'+'VsProd'].SetMarkerColor(1)
histos['sigmatNorm'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmatNorm'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'ARRAY_sigmatNorm'+'VsProd'+ext)



histos['sigmatNormIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNormIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatNormIRR'+'VsProd'].Draw("psame")
legend1.AddEntry(histos['sigmatNormIRR'+'VsProd'],"Array Nov19 + July20 Irrad. ","pe")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_sigmatNormIRR'+'VsProd'+ext)


#xt
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0,0.5)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("XT ")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['xt'+'VsProd'].SetMarkerStyle(20)
histos['xt'+'VsProd'].SetMarkerColor(1)
histos['xt'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['xt'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'ARRAY_xt'+'VsProd'+ext)


histos['xtIRR'+'VsProd'].SetMarkerStyle(22)
histos['xtIRR'+'VsProd'].SetMarkerColor(2)
histos['xtIRR'+'VsProd'].Draw("psame")
legend1.AddEntry(histos['xtIRR'+'VsProd'],"Array Nov19 + July20 Irrad. ","pe")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_xtIRR'+'VsProd'+ext)


###################################################################### plots for non irradiated ARRAYS w/ breakdown of All (Casaccia preirr) and Nw (new arrays and crystals sent by producer 3,4,5,10,111,12)##############################################################################################

#ly
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(38,102)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY [ADC counts]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['lyAll'+'VsProd'].SetMarkerStyle(20)
histos['lyAll'+'VsProd'].SetMarkerColor(4)
histos['lyAll'+'VsProd'].Draw("psame")
histos['lyNew'+'VsProd'].SetMarkerStyle(22)
histos['lyNew'+'VsProd'].SetMarkerColor(6)
histos['lyNew'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['lyAll'+'VsProd'],"Array Nov19 No Irrad.","pe")
legend1.AddEntry(histos['lyNew'+'VsProd'],"Array Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'ARRAY_ly'+'VsProd'+ext)


#lyNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.5,1.5)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY / LY_{ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['lyNormAll'+'VsProd'].SetMarkerStyle(20)
histos['lyNormAll'+'VsProd'].SetMarkerColor(4)
histos['lyNormAll'+'VsProd'].Draw("psame")
histos['lyNormNew'+'VsProd'].SetMarkerStyle(22)
histos['lyNormNew'+'VsProd'].SetMarkerColor(6)
histos['lyNormNew'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['lyNormAll'+'VsProd'],"Array Nov19 No Irrad.","pe")
legend1.AddEntry(histos['lyNormNew'+'VsProd'],"Array Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'ARRAY_lyNorm'+'VsProd'+ext)

#sigmat
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(100,200)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} [ps]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmatAll'+'VsProd'].SetMarkerStyle(20)
histos['sigmatAll'+'VsProd'].SetMarkerColor(4)
histos['sigmatAll'+'VsProd'].Draw("psame")
histos['sigmatNew'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNew'+'VsProd'].SetMarkerColor(6)
histos['sigmatNew'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmatAll'+'VsProd'],"Array Nov19 No Irrad.","pe")
legend1.AddEntry(histos['sigmatNew'+'VsProd'],"Array Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'ARRAY_sigmat'+'VsProd'+ext)


#sigmatNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0,2)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} / #sigma_{T,ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmatNormAll'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormAll'+'VsProd'].SetMarkerColor(4)
histos['sigmatNormAll'+'VsProd'].Draw("psame")
histos['sigmatNormNew'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNormNew'+'VsProd'].SetMarkerColor(6)
histos['sigmatNormNew'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmatNormAll'+'VsProd'],"Array Nov19 No Irrad.","pe")
legend1.AddEntry(histos['sigmatNormNew'+'VsProd'],"Array Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'ARRAY_sigmatNorm'+'VsProd'+ext)

#xt
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0,0.5)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("XT")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['xtAll'+'VsProd'].SetMarkerStyle(20)
histos['xtAll'+'VsProd'].SetMarkerColor(4)
histos['xtAll'+'VsProd'].Draw("psame")
histos['xtNew'+'VsProd'].SetMarkerStyle(22)
histos['xtNew'+'VsProd'].SetMarkerColor(6)
histos['xtNew'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['xtAll'+'VsProd'],"Array Nov19 No Irrad.","pe")
legend1.AddEntry(histos['xtNew'+'VsProd'],"Array Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'ARRAY_xt'+'VsProd'+ext)


###################################################################### plots for comparison with irradiated ARRAYS ##############################################################################################
#evalaute rations IRR0 vs IRR
for iprod,prod in enumerate(producersJuly20): 
    print("#### %s ####"%prod)
    prodN = int(prod.strip('prod'))
    histos['RATIO_ly'+'VsProd'].SetPoint(iprod,prodN,histos['lyIRR'+'VsProd'].GetY()[iprod]/histos['ly'+'VsProd'].GetY()[iprod])
    histos['RATIO_ly'+'VsProd'].SetPointError(iprod,0.,histos['RATIO_ly'+'VsProd'].GetY()[iprod]*mt.sqrt((histos['lyIRR'+'VsProd'].GetErrorY(iprod)/histos['lyIRR'+'VsProd'].GetY()[iprod])**2+(histos['ly'+'VsProd'].GetErrorY(iprod)/histos['ly'+'VsProd'].GetY()[iprod])**2))
  
    histos['RATIO_lyNorm'+'VsProd'].SetPoint(iprod,prodN,histos['lyNormIRR'+'VsProd'].GetY()[iprod]/histos['lyNorm'+'VsProd'].GetY()[iprod])
    histos['RATIO_lyNorm'+'VsProd'].SetPointError(iprod,0.,histos['RATIO_lyNorm'+'VsProd'].GetY()[iprod]*mt.sqrt((histos['lyNormIRR'+'VsProd'].GetErrorY(iprod)/histos['lyNormIRR'+'VsProd'].GetY()[iprod])**2+(histos['lyNorm'+'VsProd'].GetErrorY(iprod)/histos['lyNorm'+'VsProd'].GetY()[iprod])**2))

  

    histos['RATIO_sigmat'+'VsProd'].SetPoint(iprod,prodN,histos['sigmatIRR'+'VsProd'].GetY()[iprod]/histos['sigmat'+'VsProd'].GetY()[iprod])
    histos['RATIO_sigmat'+'VsProd'].SetPointError(iprod,0.,histos['RATIO_sigmat'+'VsProd'].GetY()[iprod]*mt.sqrt((histos['sigmatIRR'+'VsProd'].GetErrorY(iprod)/histos['sigmatIRR'+'VsProd'].GetY()[iprod])**2+(histos['sigmat'+'VsProd'].GetErrorY(iprod)/histos['sigmat'+'VsProd'].GetY()[iprod])**2))
    
  
    histos['RATIO_sigmatNorm'+'VsProd'].SetPoint(iprod,prodN,histos['sigmatNormIRR'+'VsProd'].GetY()[iprod]/histos['sigmatNorm'+'VsProd'].GetY()[iprod])
    histos['RATIO_sigmatNorm'+'VsProd'].SetPointError(iprod,0.,histos['RATIO_sigmatNorm'+'VsProd'].GetY()[iprod]*mt.sqrt((histos['sigmatNormIRR'+'VsProd'].GetErrorY(iprod)/histos['sigmatNormIRR'+'VsProd'].GetY()[iprod])**2+(histos['sigmatNorm'+'VsProd'].GetErrorY(iprod)/histos['sigmatNorm'+'VsProd'].GetY()[iprod])**2))

    histos['RATIO_xt'+'VsProd'].SetPoint(iprod,prodN,histos['xtIRR'+'VsProd'].GetY()[iprod]/histos['xt'+'VsProd'].GetY()[iprod])
    histos['RATIO_xt'+'VsProd'].SetPointError(iprod,0.,histos['RATIO_xt'+'VsProd'].GetY()[iprod]*mt.sqrt((histos['xtIRR'+'VsProd'].GetErrorY(iprod)/histos['xtIRR'+'VsProd'].GetY()[iprod])**2+(histos['xt'+'VsProd'].GetErrorY(iprod)/histos['xt'+'VsProd'].GetY()[iprod])**2))

 #   print histos['xtIRR'+'VsProd'].GetY()[iprod],histos['xt'+'VsProd'].GetY()[iprod],histos['RATIO_xt'+'VsProd'].GetY()[iprod], histos['xtIRR'+'VsProd'].GetErrorY(iprod),histos['xt'+'VsProd'].GetErrorY(iprod),histos['RATIO_xt'+'VsProd'].GetY()[iprod]*mt.sqrt((histos['xtIRR'+'VsProd'].GetErrorY(iprod)/histos['xtIRR'+'VsProd'].GetY()[iprod])**2+(histos['xt'+'VsProd'].GetErrorY(iprod)/histos['xt'+'VsProd'].GetY()[iprod])**2)

  
c1=R.TCanvas("c1","c1",800,800)
c1_pad1 = R.TPad("c1_pad1", "c1_pad1", 0, 0.4, 1, 1.0)
c1_pad1.SetBottomMargin(0.008)#Upper and lower plot are joined
#c1_pad1.SetGridx()
c1_pad1.SetGridy()
c1_pad1.Draw()
c1_pad2 = R.TPad("c1_pad2", "c1_pad2", 0, 0.05, 1, 0.4)
c1_pad2.SetTopMargin(0.05);#Upper and lower plot are joined
c1_pad2.SetBottomMargin(0.4);
#c1_pad2.SetGridx()
c1_pad2.SetGridy()
c1_pad2.Draw()
c1_pad1.cd()
c1_pad1.SetGridy()

#ly
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(38,102)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY [ADC counts]")
h1.GetXaxis().SetTitle("Prod. ID") 
h1.Draw("hist")
histos['ly'+'VsProd'].Draw("pesame")
histos['lyIRR'+'VsProd'].SetMarkerStyle(22)
histos['lyIRR'+'VsProd'].SetMarkerColor(2)
histos['lyIRR'+'VsProd'].Draw("pesame")
legend1.Clear()
legend1.AddEntry(histos['ly'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.AddEntry(histos['lyIRR'+'VsProd'],"Array Nov19 + July20 Irrad. ","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
h2=R.TH1F("h1","h1",12,0,13)
h2.GetYaxis().SetRangeUser(0.6,1.1)
h2.GetYaxis().SetNdivisions(505)
h2.GetXaxis().SetRangeUser(0,13)
h2.GetYaxis().SetTitle("LY_{IRR} / LY ")
h2.GetYaxis().SetTitleOffset(0.2*h2.GetYaxis().GetTitleOffset())
h2.GetYaxis().SetTitleSize(1.7*h2.GetYaxis().GetTitleSize())
h2.GetXaxis().SetTitleSize(1.7*h2.GetXaxis().GetTitleSize())
h2.GetYaxis().SetLabelSize(1.7*h2.GetYaxis().GetLabelSize())
h2.GetXaxis().SetLabelSize(1.7*h2.GetXaxis().GetLabelSize())
h2.GetXaxis().SetTitle("Prod. ID")
h2.Draw("hist")
histos['RATIO_ly'+'VsProd'].SetMarkerStyle(23)
histos['RATIO_ly'+'VsProd'].SetLineColor(1)
histos['RATIO_ly'+'VsProd'].SetLineWidth(2)
histos['RATIO_ly'+'VsProd'].Draw("PEsame")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_lyIRR'+'VsProd'+ext)

#lyNorm
c1_pad1.cd()
c1_pad1.SetGridy()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.5,1.5)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY / LY_{ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['lyNorm'+'VsProd'].Draw("pesame")
histos['lyNormIRR'+'VsProd'].SetMarkerStyle(22)
histos['lyNormIRR'+'VsProd'].SetMarkerColor(2)
histos['lyNormIRR'+'VsProd'].Draw("pesame")
legend1.Clear()
legend1.AddEntry(histos['lyNorm'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.AddEntry(histos['lyNormIRR'+'VsProd'],"Array Nov19 + July20 Irrad. ","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
h2=R.TH1F("h1","h1",12,0,13)
h2.GetYaxis().SetRangeUser(0.6,1.1)
h2.GetYaxis().SetNdivisions(505)
h2.GetXaxis().SetRangeUser(0,13)
h2.GetYaxis().SetTitle("(LY/LY_{ref})_{IRR} / (LY/LY_{ref})")
h2.GetYaxis().SetTitleOffset(0.2*h2.GetYaxis().GetTitleOffset())
h2.GetYaxis().SetTitleSize(1.7*h2.GetYaxis().GetTitleSize())
h2.GetXaxis().SetTitleSize(1.7*h2.GetXaxis().GetTitleSize())
h2.GetYaxis().SetLabelSize(1.7*h2.GetYaxis().GetLabelSize())
h2.GetXaxis().SetLabelSize(1.7*h2.GetXaxis().GetLabelSize())
h2.GetXaxis().SetTitle("Prod. ID")
h2.Draw("hist")
histos['RATIO_lyNorm'+'VsProd'].SetMarkerStyle(23)
histos['RATIO_lyNorm'+'VsProd'].SetLineColor(1)
histos['RATIO_lyNorm'+'VsProd'].SetLineWidth(2)
histos['RATIO_lyNorm'+'VsProd'].Draw("PEsame")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_lyNormIRR'+'VsProd'+ext)


    
#sigmat
#c1_pad1.cd()
c1_pad1.cd()
c1_pad1.SetGridy()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(100,200)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} [ps]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmat'+'VsProd'].Draw("pesame")
histos['sigmatIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatIRR'+'VsProd'].Draw("pesame")
legend1.Clear()
legend1.AddEntry(histos['sigmat'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.AddEntry(histos['sigmatIRR'+'VsProd'],"Array Nov19 + July20 Irrad. ","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
h2=R.TH1F("h1","h1",12,0,13)
h2.GetYaxis().SetRangeUser(0.6,1.5)
h2.GetYaxis().SetNdivisions(505)
h2.GetXaxis().SetRangeUser(0,13)
h2.GetYaxis().SetTitle("#sigma_{T,IRR} / #sigma_{T} ")
h2.GetYaxis().SetTitleOffset(0.2*h2.GetYaxis().GetTitleOffset())
h2.GetYaxis().SetTitleSize(1.7*h2.GetYaxis().GetTitleSize())
h2.GetXaxis().SetTitleSize(1.7*h2.GetXaxis().GetTitleSize())
h2.GetYaxis().SetLabelSize(1.7*h2.GetYaxis().GetLabelSize())
h2.GetXaxis().SetLabelSize(1.7*h2.GetXaxis().GetLabelSize())
h2.GetXaxis().SetTitle("Prod. ID")
h2.Draw("hist")
histos['RATIO_sigmat'+'VsProd'].SetMarkerStyle(23)
histos['RATIO_sigmat'+'VsProd'].SetLineColor(1)
histos['RATIO_sigmat'+'VsProd'].SetLineWidth(2)
histos['RATIO_sigmat'+'VsProd'].Draw("PEsame")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_sigmatIRR'+'VsProd'+ext)

#sigmatNorm
#c1_pad1.cd()
c1_pad1.cd()
c1_pad1.SetGridy()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.5,1.5)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} / #sigma_{T,ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmatNorm'+'VsProd'].Draw("pesame")
histos['sigmatNormIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNormIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatNormIRR'+'VsProd'].Draw("pesame")
legend1.Clear()
legend1.AddEntry(histos['sigmatNorm'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.AddEntry(histos['sigmatNormIRR'+'VsProd'],"Array Nov19 + July20 Irrad. ","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
h2=R.TH1F("h1","h1",12,0,13)
h2.GetYaxis().SetRangeUser(0.6,1.5)
h2.GetYaxis().SetNdivisions(505)
h2.GetXaxis().SetRangeUser(0,13)
h2.GetYaxis().SetTitle("(#sigma_{T} / #sigma_{T,ref})_{IRR} / (#sigma_{T} / #sigma_{T,ref})")
h2.GetYaxis().SetTitleOffset(0.2*h2.GetYaxis().GetTitleOffset())
h2.GetYaxis().SetTitleSize(1.7*h2.GetYaxis().GetTitleSize())
h2.GetXaxis().SetTitleSize(1.7*h2.GetXaxis().GetTitleSize())
h2.GetYaxis().SetLabelSize(1.7*h2.GetYaxis().GetLabelSize())
h2.GetXaxis().SetLabelSize(1.7*h2.GetXaxis().GetLabelSize())
h2.GetXaxis().SetTitle("Prod. ID")
h2.Draw("hist")
histos['RATIO_sigmatNorm'+'VsProd'].SetMarkerStyle(23)
histos['RATIO_sigmatNorm'+'VsProd'].SetLineColor(1)
histos['RATIO_sigmatNorm'+'VsProd'].SetLineWidth(2)
histos['RATIO_sigmatNorm'+'VsProd'].Draw("PEsame")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_sigmatNormIRR'+'VsProd'+ext)

    
#xt
#c1_pad1.cd()
c1_pad1.cd()
c1_pad1.SetGridy()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0,0.5)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("XT")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['xt'+'VsProd'].Draw("pesame")
histos['xtIRR'+'VsProd'].SetMarkerStyle(22)
histos['xtIRR'+'VsProd'].SetMarkerColor(2)
histos['xtIRR'+'VsProd'].Draw("pesame")
legend1.Clear()
legend1.AddEntry(histos['xt'+'VsProd'],"Array Nov19 No Irrad. + July20","pe")
legend1.AddEntry(histos['xtIRR'+'VsProd'],"Array Nov19 + July20 Irrad. ","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
h2=R.TH1F("h1","h1",12,0,13)
h2.GetYaxis().SetRangeUser(0.,3)
h2.GetYaxis().SetNdivisions(505)
h2.GetXaxis().SetRangeUser(0,13)
h2.GetYaxis().SetTitle("XT_{IRR}  / XT")
h2.GetYaxis().SetTitleOffset(0.2*h2.GetYaxis().GetTitleOffset())
h2.GetYaxis().SetTitleSize(1.7*h2.GetYaxis().GetTitleSize())
h2.GetXaxis().SetTitleSize(1.7*h2.GetXaxis().GetTitleSize())
h2.GetYaxis().SetLabelSize(1.7*h2.GetYaxis().GetLabelSize())
h2.GetXaxis().SetLabelSize(1.7*h2.GetXaxis().GetLabelSize())
h2.GetXaxis().SetTitle("Prod. ID")
h2.Draw("hist")
histos['RATIO_xt'+'VsProd'].SetMarkerStyle(23)
histos['RATIO_xt'+'VsProd'].SetLineColor(1)
histos['RATIO_xt'+'VsProd'].SetLineWidth(2)
histos['RATIO_xt'+'VsProd'].Draw("PEsame")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/irradiation/"+'ARRAY_xtIRR'+'VsProd'+ext)

    
    
###################################################################### plots for BARS ##############################################################################################



#ly
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(58,122)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY [ADC counts]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['ly_bars'+'VsProd'].SetMarkerStyle(20)
histos['ly_bars'+'VsProd'].SetMarkerColor(1)
histos['ly_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['ly_bars'+'VsProd'],"Bars Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'BARS_ly'+'VsProd'+ext)

#lyNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.4,1.6)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY / LY_{ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['lyNorm_bars'+'VsProd'].SetMarkerStyle(20)
histos['lyNorm_bars'+'VsProd'].SetMarkerColor(1)
histos['lyNorm_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['lyNorm_bars'+'VsProd'],"Bars Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'BARS_lyNorm'+'VsProd'+ext)

#sigmat
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(70,220)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} [ps]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmat_bars'+'VsProd'].SetMarkerStyle(20)
histos['sigmat_bars'+'VsProd'].SetMarkerColor(1)
histos['sigmat_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmat_bars'+'VsProd'],"Bars Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'BARS_sigmat'+'VsProd'+ext)

#sigmatNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.4,2.4)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} / #sigma_{T,ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmatNorm_bars'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNorm_bars'+'VsProd'].SetMarkerColor(1)
histos['sigmatNorm_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmatNorm_bars'+'VsProd'],"Bars Nov19 No Irrad. + July20","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'BARS_sigmatNorm'+'VsProd'+ext)



#plot correlation array vs bars
legend1 = R.TLegend(0.6,0.4,0.9,0.9)
#ly
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",60,40,130)
h1.GetYaxis().SetRangeUser(40,130)
h1.GetXaxis().SetRangeUser(40,130)
h1.GetYaxis().SetTitle("LY BARS [ADC counts]")
h1.GetXaxis().SetTitle("LY ARRAYS [ADC counts]")
h1.Draw("hist")
b=R.TF1("b2","x",40,130)
b.SetLineStyle(2)
b.SetLineColor(1)
b.Draw("same")
legend1.Clear()
for prod in producersJuly20:
    histos['2D_ly'+'_forProd_'+prod].Draw("psame")
    legend1.AddEntry(histos['2D_ly'+'_forProd_'+prod],prod,"pe")
legend1.AddEntry(b, "Bisector","l")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'2D_ly'+'VsProd'+ext)


#lyNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",60,0,2)
h1.GetYaxis().SetRangeUser(0,2)
h1.GetXaxis().SetRangeUser(0,2)
h1.GetYaxis().SetTitle("LY / LY_{ref} BARS ")
h1.GetXaxis().SetTitle("LY / LY_{ref} ARRAYS ")
h1.Draw("hist")
b=R.TF1("b2","x",0,2)
b.SetLineStyle(2)
b.SetLineColor(1)
b.Draw("same")
legend1.Clear()
for prod in producersJuly20:
    histos['2D_lyNorm'+'_forProd_'+prod].Draw("psame")
    legend1.AddEntry(histos['2D_lyNorm'+'_forProd_'+prod],prod,"pe")
legend1.AddEntry(b, "Bisector","l")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'2D_lyNorm'+'VsProd'+ext)



#sigmat
c1.cd()
c1.SetGrid()

#c1_pad1.cd()
h1=R.TH1F("h1","h1",60,68,220)
h1.GetYaxis().SetRangeUser(68,220)
h1.GetXaxis().SetRangeUser(68,220)
h1.GetYaxis().SetTitle("#sigma_{T} BARS [ps]")
h1.GetXaxis().SetTitle("#sigma_{T} ARRAYS [ps]")
h1.Draw("hist")
b=R.TF1("b2","x",68,220)
b.SetLineStyle(2)
b.SetLineColor(1)
b.Draw("same")
legend1.Clear()
for prod in producersJuly20:
    histos['2D_sigmat'+'_forProd_'+prod].Draw("psame")
    legend1.AddEntry(histos['2D_sigmat'+'_forProd_'+prod],prod,"pe")
legend1.AddEntry(b, "Bisector","l")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'2D_sigmat'+'VsProd'+ext)


#sigmatNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",60,0,2)
h1.GetYaxis().SetRangeUser(0,2)
h1.GetXaxis().SetRangeUser(0,2)
h1.GetYaxis().SetTitle("#sigma_{T} / #sigma_{T,ref} BARS")
h1.GetXaxis().SetTitle("#sigma_{T} / #sigma_{T,ref} ARRAYS")
h1.Draw("hist")
b=R.TF1("b2","x",0,2)
b.SetLineStyle(2)
b.SetLineColor(1)
b.Draw("same")
legend1.Clear()
for prod in producersJuly20:
    histos['2D_sigmatNorm'+'_forProd_'+prod].Draw("psame")
    legend1.AddEntry(histos['2D_sigmatNorm'+'_forProd_'+prod],prod,"pe")
legend1.AddEntry(b, "Bisector","l")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/global/"+'2D_sigmatNorm'+'VsProd'+ext)


###################################################################### plots for non irradiated BARS w/ breakdown of All (Casaccia preirr) and Nw (new arrays and crystals sent by producer 3,4,5,10,111,12)##############################################################################################

legend1 = R.TLegend(0.6,0.7,0.9,0.9)
#ly
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(58,122)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY [ADC counts]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['lyAll_bars'+'VsProd'].SetMarkerStyle(20)
histos['lyAll_bars'+'VsProd'].SetMarkerColor(4)
histos['lyAll_bars'+'VsProd'].Draw("psame")
histos['lyNew_bars'+'VsProd'].SetMarkerStyle(22)
histos['lyNew_bars'+'VsProd'].SetMarkerColor(6)
histos['lyNew_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['lyAll_bars'+'VsProd'],"Bars Nov19 No Irrad.","pe")
legend1.AddEntry(histos['lyNew_bars'+'VsProd'],"Bars Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'BARS_ly_bars'+'VsProd'+ext)


#lyNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.4,1.6)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("LY / LY_{ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['lyNormAll_bars'+'VsProd'].SetMarkerStyle(20)
histos['lyNormAll_bars'+'VsProd'].SetMarkerColor(4)
histos['lyNormAll_bars'+'VsProd'].Draw("psame")
histos['lyNormNew_bars'+'VsProd'].SetMarkerStyle(22)
histos['lyNormNew_bars'+'VsProd'].SetMarkerColor(6)
histos['lyNormNew_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['lyNormAll_bars'+'VsProd'],"Bars Nov19 No Irrad.","pe")
legend1.AddEntry(histos['lyNormNew_bars'+'VsProd'],"Bars Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'BARS_lyNorm_bars'+'VsProd'+ext)

#sigmat
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(70,220)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} [ps]")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmatAll_bars'+'VsProd'].SetMarkerStyle(20)
histos['sigmatAll_bars'+'VsProd'].SetMarkerColor(4)
histos['sigmatAll_bars'+'VsProd'].Draw("psame")
histos['sigmatNew_bars'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNew_bars'+'VsProd'].SetMarkerColor(6)
histos['sigmatNew_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmatAll_bars'+'VsProd'],"Bars Nov19 No Irrad.","pe")
legend1.AddEntry(histos['sigmatNew_bars'+'VsProd'],"Bars Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'BARS_sigmat_bars'+'VsProd'+ext)


#sigmatNorm
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.4,2.4)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("#sigma_{T} / #sigma_{T,ref}")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['sigmatNormAll_bars'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormAll_bars'+'VsProd'].SetMarkerColor(4)
histos['sigmatNormAll_bars'+'VsProd'].Draw("psame")
histos['sigmatNormNew_bars'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNormNew_bars'+'VsProd'].SetMarkerColor(6)
histos['sigmatNormNew_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmatNormAll_bars'+'VsProd'],"Bars Nov19 No Irrad.","pe")
legend1.AddEntry(histos['sigmatNormNew_bars'+'VsProd'],"Bars Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'BARS_sigmatNorm_bars'+'VsProd'+ext)

#xt
c1.cd()
c1.SetGrid()
#c1_pad1.cd()
h1=R.TH1F("h1","h1",12,0,13)
h1.GetYaxis().SetRangeUser(0.,0.5)
h1.GetXaxis().SetRangeUser(0,13)
h1.GetYaxis().SetTitle("XT")
h1.GetXaxis().SetTitle("Prod. ID")
h1.Draw("hist")
histos['xtAll_bars'+'VsProd'].SetMarkerStyle(20)
histos['xtAll_bars'+'VsProd'].SetMarkerColor(4)
histos['xtAll_bars'+'VsProd'].Draw("psame")
histos['xtNew_bars'+'VsProd'].SetMarkerStyle(22)
histos['xtNew_bars'+'VsProd'].SetMarkerColor(6)
histos['xtNew_bars'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['xtAll_bars'+'VsProd'],"Bars Nov19 No Irrad.","pe")
legend1.AddEntry(histos['xtNew_bars'+'VsProd'],"Bars Jul20 New No Irrad.","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/breakdown/"+'BARS_xt_bars'+'VsProd'+ext)



   
