import ROOT as R
R.gROOT.SetBatch(1)

from array import array
import math as mt
import numpy as np

#outputdir = "LYSOArrays"
outputdir = "/afs/cern.ch/user/s/santanas/www/TOFPET2/LYSOARRAYS_Casaccia"
pixelRes = 90 #ps

## Read Tgraphs from single bars file
fileSingleBars = "LYMergedPlots.root" 
nbars = 4
tfileSingleBars = R.TFile(fileSingleBars)
#decay time
dt_ByProd=R.TGraphErrors()
dt_IRR9K_ByProd=R.TGraphErrors()
R.gDirectory.GetObject("dt_ByProd",dt_ByProd)
R.gDirectory.GetObject("dt_IRR9K_ByProd",dt_IRR9K_ByProd)
#ly
ly_ByProd=R.TGraphErrors()
ly_IRR9K_ByProd=R.TGraphErrors()
R.gDirectory.GetObject("lyNormAbs_TOFPET_ByProd",ly_ByProd)
R.gDirectory.GetObject("lyNormAbs_TOFPET_IRR9K_ByProd",ly_IRR9K_ByProd)
#sigmat
sigmat_ByProd=R.TGraphErrors()
sigmat_IRR9K_ByProd=R.TGraphErrors()
R.gDirectory.GetObject("ctr_ByProd",sigmat_ByProd)
R.gDirectory.GetObject("ctr_IRR9K_ByProd",sigmat_IRR9K_ByProd)
#
tfileSingleBars.Close()

npoints = dt_ByProd.GetN() 
print "npoints:", npoints
x=R.Double()
y=R.Double()
dtPreIRRbar={}
dtPostIRRbar={}
lyPreIRRbar={}
lyPostIRRbar={}
sigmatPreIRRbar={}
sigmatPostIRRbar={}
for point in range(0,npoints):
    #decay time
    dt_ByProd.GetPoint(point,x,y)    
    dtPreIRRbar[int(x)]=(float(y),dt_ByProd.GetErrorY(point))
    dt_IRR9K_ByProd.GetPoint(point,x,y)
    if dt_IRR9K_ByProd.GetErrorY(point)==0.:
        dtPostIRRbar[int(x)]=(float(y),dtPreIRRbar[int(x)][1])
    else:
        dtPostIRRbar[int(x)]=(float(y),dt_IRR9K_ByProd.GetErrorY(point))
    #ly
    ly_ByProd.GetPoint(point,x,y)    
    lyPreIRRbar[int(x)]=(float(y),ly_ByProd.GetErrorY(point))
    ly_IRR9K_ByProd.GetPoint(point,x,y)
    if ly_IRR9K_ByProd.GetErrorY(point)==0.:
        lyPostIRRbar[int(x)]=(float(y),lyPreIRRbar[int(x)][1])
    else:
        lyPostIRRbar[int(x)]=(float(y),ly_IRR9K_ByProd.GetErrorY(point))
    #sigmat
    sigmat_ByProd.GetPoint(point,x,y)    
    sigmatPreIRRbar[int(x)]=(float(y),sigmat_ByProd.GetErrorY(point))
    sigmat_IRR9K_ByProd.GetPoint(point,x,y)
    if sigmat_IRR9K_ByProd.GetErrorY(point)==0.:
        sigmatPostIRRbar[int(x)]=(float(y),sigmatPreIRRbar[int(x)][1])
    else:
        sigmatPostIRRbar[int(x)]=(float(y),sigmat_IRR9K_ByProd.GetErrorY(point))
print "dtPreIRRbar:", dtPreIRRbar
print "dtPostIRRbar:", dtPostIRRbar
print "lyPreIRRbar:", lyPreIRRbar
print "lyPostIRRbar:", lyPostIRRbar
print "sigmatPreIRRbar:", sigmatPreIRRbar
print "sigmatPostIRRbar:", sigmatPostIRRbar

## Read Tgraphs from t1 threshold scans (dV/dT by prod)
fileT1ScanPreIRR = "slopeByProd_ArrayPreIRR.root" 
fileT1ScanPostIRR = "slopeByProd_ArrayPostIRR.root" 
#PreIRR
tfileT1ScanPreIRR = R.TFile(fileT1ScanPreIRR)
slope_ByProd_PreIRR=R.TGraphErrors()
R.gDirectory.GetObject("slopeByProd",slope_ByProd_PreIRR)
tfileT1ScanPreIRR.Close()
#PostIRR
tfileT1ScanPostIRR = R.TFile(fileT1ScanPostIRR)
slope_ByProd_PostIRR=R.TGraphErrors()
R.gDirectory.GetObject("slopeByProd",slope_ByProd_PostIRR)
tfileT1ScanPostIRR.Close()
#

npoints2 = slope_ByProd_PreIRR.GetN() 
if (npoints2 != npoints):
    print "Different number of producers for the two input files"
    exit(0)
print "npoints2:", npoints2
x=R.Double()
y=R.Double()
dVdTPreIRR={}
dVdTPostIRR={}
for point in range(0,npoints2):
    #PreIRR
    slope_ByProd_PreIRR.GetPoint(point,x,y)    
    dVdTPreIRR[int(x)]=(float(y),slope_ByProd_PreIRR.GetErrorY(point))
    #PostIRR
    slope_ByProd_PostIRR.GetPoint(point,x,y)    
    dVdTPostIRR[int(x)]=(float(y),slope_ByProd_PostIRR.GetErrorY(point))
print "dVdTPreIRR:", dVdTPreIRR
print "dVdTPostIRR:", dVdTPostIRR

#==============================================================================

crystalsData = R.TTree("crystalsData","crystalsData")
#producer   type   id geometry          tag       temp bar  posX  posY         ly         ctr      lyRef      ctrRef       xtLeft      xtRight
crystalsData.ReadFile("arraysDB_Casaccia_Nov2019.csv","key/C:prod/C:type/C:ID/I:geo/C:tag/C:temp/F:bar/I:posX/F:posY/F:ly/F:ctr/F:lyRef/F:ctrRef/F:xtLeft/F:xtRight/F")

producers = [ 'prod'+str(i) for i in range(1,10) ]
#geoms = [ 'geo'+str(i) for i in range(1,4) ]

#Declare histograms
histos = {}

#Declare dose levels
dose={
    'IRR0':0,
    'IRR3K_16H':50125,
    'IRR9K_5H':45202
}

#Fill histograms and create dictionary with data pre-irradiation
dataPreIRR = {}
for crys in crystalsData:

    if ( crys.ly < 0. or crys.ctr < 0. or crys.lyRef < 0. or crys.ctrRef < 0.):
        continue

    prod = crys.prod.rstrip('\x00').rstrip('\n')
    tag = crys.tag.rstrip('\x00').rstrip('\n')
    barID = str(crys.ID)+"_"+str(crys.bar)

    if("IRR0" in tag):
        dataPreIRR[barID] = {'lyPreIRR': crys.ly, 'lyNormPreIRR': crys.ly/crys.lyRef
                             , 'sigmatPreIRR': mt.sqrt(crys.ctr**2-pixelRes**2), 'sigmatNormPreIRR': mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2)
                             , 'xtLeftPreIRR': crys.xtLeft, 'xtRightPreIRR': crys.xtRight 
        }
        
#Create dictionary with final data 
data = {}
for prod in producers: 
    data[prod] = []

for crys in crystalsData:

    if ( crys.ly < 0. or crys.ctr < 0. or crys.lyRef < 0. or crys.ctrRef < 0.):
        continue

    prod = crys.prod.rstrip('\x00').rstrip('\n')
    tag = crys.tag.rstrip('\x00').rstrip('\n')
    tagSplit = tag.split('_')
    doseTag = tagSplit[0]+"_"+tagSplit[1]
    barID = str(crys.ID)+"_"+str(crys.bar)    

    irr = ""
    if("IRR0" in tag):
        continue

    lyPreIRR = dataPreIRR[barID]['lyPreIRR']
    lyNormPreIRR = dataPreIRR[barID]['lyNormPreIRR']
    sigmatPreIRR = dataPreIRR[barID]['sigmatPreIRR']
    sigmatNormPreIRR = dataPreIRR[barID]['sigmatNormPreIRR']
    
    lyPostIRR = crys.ly 
    lyNormPostIRR = (crys.ly/crys.lyRef) 
    sigmatPostIRR = mt.sqrt(crys.ctr**2-pixelRes**2)
    sigmatNormPostIRR = mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2)
    xtLeftPostIRR = crys.xtLeft
    xtRightPostIRR = crys.xtRight
    
    myDose = dose[doseTag]
    #print doseTag, myDose
    data[prod].append({'barID':barID,'dose':myDose
                       ,'lyPreIRR':lyPreIRR,'lyNormPreIRR':lyNormPreIRR,'sigmatPreIRR':sigmatPreIRR,'sigmatNormPreIRR':sigmatNormPreIRR
                       ,'lyPostIRR':lyPostIRR,'lyNormPostIRR':lyNormPostIRR,'sigmatPostIRR':sigmatPostIRR,'sigmatNormPostIRR':sigmatNormPostIRR
                       , 'xtLeftPreIRR':dataPreIRR[barID]['xtLeftPreIRR'], 'xtLeftPostIRR':xtLeftPostIRR
                       , 'xtRightPreIRR':dataPreIRR[barID]['xtRightPreIRR'], 'xtRightPostIRR':xtRightPostIRR
                   })

#print data

###########
#Make plots
###########

#Create graphs
graphs=['lyPreIRR','lyNormPreIRR','sigmatPreIRR','sigmatNormPreIRR'
        ,'lyPostIRR','lyNormPostIRR','sigmatPostIRR','sigmatNormPostIRR'
        ,'lyRatioIRR','lyNormRatioIRR','sigmatRatioIRR','sigmatNormRatioIRR'
        ,'xtPreIRR','xtPostIRR','xtRatioIRR'
        ,'lyNormBarOverArrayPreIRR','sigmatNormBarOverArrayPreIRR'
        ,'lyNormBarOverArrayPostIRR','sigmatNormBarOverArrayPostIRR'
        ,'lyNormBarOverArrayRatioIRR','sigmatNormBarOverArrayRatioIRR'
        #,'sigmatNormOverLONormOverDtPreIRR','sigmatNormOverdVdTNormPreIRR'
        #,'sigmatNormOverLONormOverDtPostIRR','sigmatNormOverdVdTNormPostIRR'
        #,'sigmatNormOverLONormOverDtRatioIRR','sigmatNormOverdVdTNormRatioIRR'
]
for g in graphs:
    histos[g+'VsProd']=R.TGraphErrors(len(producers)) 
    histos[g+'VsProd'].SetName(g+'VsProd')
    histos[g+'VsProd'].SetTitle(g+'VsProd')
    histos[g+'VsProd'].SetMarkerSize(1.4)
    histos[g+'VsProd'].GetXaxis().SetTitle("     Producer")
    histos[g+'VsProd'].GetXaxis().SetTitleSize(0.1)
    histos[g+'VsProd'].GetXaxis().SetLabelSize(0.1)
    histos[g+'VsProd'].GetXaxis().SetLabelOffset(0.035)
    histos[g+'VsProd'].GetXaxis().SetTitleOffset(1.2)

scatterPlots=['sigmatNormVsLONormPreIRR','sigmatNormVsLONormPostIRR'
              ,'sigmatNormVsLONormOverDtPreIRR','sigmatNormVsLONormOverDtPostIRR'
              ,'LONormBarVsArrayPreIRR','LONormBarVsArrayPostIRR'
              ,'sigmatNormBarVsArrayPreIRR','sigmatNormBarVsArrayPostIRR'
              ,'sigmatNormVsdVdTNormPreIRR','sigmatNormVsdVdTNormPostIRR'
]
for g in scatterPlots:
    histos[g]=R.TGraphErrors(len(producers)) 
    histos[g].SetName(g)
    histos[g].SetTitle(g)
    histos[g].SetMarkerSize(1.4)

#Loop over producers
for iprod,prod in enumerate(producers): 

    print("#### %s ####"%prod)
    prodN = int(prod.strip('prod'))

    #create arrays with measurements to be averaged

    #Pre
    lyPreIRR=array('d')    
    lyNormPreIRR=array('d')    
    sigmatPreIRR=array('d')    
    sigmatNormPreIRR=array('d')    
    xtLeftPreIRR=array('d')
    xtRightPreIRR=array('d')

    #Post
    lyPostIRR=array('d')    
    lyNormPostIRR=array('d')    
    sigmatPostIRR=array('d')    
    sigmatNormPostIRR=array('d')    
    xtLeftPostIRR=array('d')
    xtRightPostIRR=array('d')

    #Post/Pre
    lyRatioIRR=array('d')    
    lyNormRatioIRR=array('d')    
    sigmatRatioIRR=array('d')    
    sigmatNormRatioIRR=array('d')    
    xtLeftRatioIRR=array('d')
    xtRightRatioIRR=array('d')
 
    for i,meas in enumerate(data[prod]):

        #Pre
        lyPreIRR.append(meas['lyPreIRR'])
        lyNormPreIRR.append(meas['lyNormPreIRR'])
        sigmatPreIRR.append(meas['sigmatPreIRR'])
        sigmatNormPreIRR.append(meas['sigmatNormPreIRR'])
        if (meas['xtLeftPreIRR']>0):
            xtLeftPreIRR.append(meas['xtLeftPreIRR'])
        if (meas['xtRightPreIRR']>0):
            xtRightPreIRR.append(meas['xtRightPreIRR'])
        
        #Post
        lyPostIRR.append(meas['lyPostIRR'])
        lyNormPostIRR.append(meas['lyNormPostIRR'])
        sigmatPostIRR.append(meas['sigmatPostIRR'])
        sigmatNormPostIRR.append(meas['sigmatNormPostIRR'])
        if (meas['xtLeftPostIRR']>0):
            xtLeftPostIRR.append(meas['xtLeftPostIRR'])
        if (meas['xtRightPostIRR']>0):
            xtRightPostIRR.append(meas['xtRightPostIRR'])

        #Post/Pre
        lyRatioIRR.append(meas['lyPostIRR']/meas['lyPreIRR'])
        lyNormRatioIRR.append(meas['lyNormPostIRR']/meas['lyNormPreIRR'])
        sigmatRatioIRR.append(meas['sigmatPostIRR']/meas['sigmatPreIRR'])
        sigmatNormRatioIRR.append(meas['sigmatNormPostIRR']/meas['sigmatNormPreIRR'])
        if (meas['xtLeftPostIRR']>0 and meas['xtLeftPreIRR']>0 ):
            xtLeftRatioIRR.append(meas['xtLeftPostIRR']/meas['xtLeftPreIRR'])
        if (meas['xtRightPostIRR']>0 and meas['xtRightPreIRR']>0 ):
            xtRightRatioIRR.append(meas['xtRightPostIRR']/meas['xtRightPreIRR'])


    #Pre
    lyPreIRR_np = np.array(lyPreIRR)
    mean_lyPreIRR = lyPreIRR_np.mean()
    std_lyPreIRR = lyPreIRR_np.std()/mt.sqrt(len(lyPreIRR))

    lyNormPreIRR_np = np.array(lyNormPreIRR)
    mean_lyNormPreIRR = lyNormPreIRR_np.mean()
    std_lyNormPreIRR = lyNormPreIRR_np.std()/mt.sqrt(len(lyNormPreIRR))

    sigmatPreIRR_np = np.array(sigmatPreIRR)
    mean_sigmatPreIRR = sigmatPreIRR_np.mean()
    std_sigmatPreIRR = sigmatPreIRR_np.std()/mt.sqrt(len(sigmatPreIRR))

    sigmatNormPreIRR_np = np.array(sigmatNormPreIRR)
    mean_sigmatNormPreIRR = sigmatNormPreIRR_np.mean()
    std_sigmatNormPreIRR = sigmatNormPreIRR_np.std()/mt.sqrt(len(sigmatNormPreIRR))

    xtLeftPreIRR_np = np.array(xtLeftPreIRR)
    mean_xtLeftPreIRR = xtLeftPreIRR_np.mean()
    std_xtLeftPreIRR = xtLeftPreIRR_np.std()/mt.sqrt(len(xtLeftPreIRR))

    xtRightPreIRR_np = np.array(xtRightPreIRR)
    mean_xtRightPreIRR = xtRightPreIRR_np.mean()
    std_xtRightPreIRR = xtRightPreIRR_np.std()/mt.sqrt(len(xtRightPreIRR))

    mean_xtPreIRR = mean_xtLeftPreIRR + mean_xtRightPreIRR
    std_xtPreIRR = mt.sqrt(std_xtLeftPreIRR**2 +std_xtRightPreIRR**2)

    mean_lyNormOverDtPreIRR = ( mean_lyNormPreIRR / (dtPreIRRbar[int(prodN)][0]/dtPreIRRbar[1][0]) ) 
    stdRel_lyNormOverDtPreIRR = (std_lyNormPreIRR/mean_lyNormPreIRR)**2 + ((dtPreIRRbar[int(prodN)][1]/mt.sqrt(nbars))/dtPreIRRbar[int(prodN)][0])**2 + ((dtPreIRRbar[1][1]/mt.sqrt(nbars))/dtPreIRRbar[1][0])**2 #/sqrt(N) since it is an average of N meas.
    stdRel_lyNormOverDtPreIRR = mt.sqrt(stdRel_lyNormOverDtPreIRR)
    std_lyNormOverDtPreIRR = stdRel_lyNormOverDtPreIRR * mean_lyNormOverDtPreIRR
    print "PRE: prodN, meanlyNorm, dt, dtref, dtratio, mean/dt, sigma_mean/dt: ", int(prodN), mean_lyNormPreIRR, dtPreIRRbar[int(prodN)][0], dtPreIRRbar[1][0], dtPreIRRbar[int(prodN)][0]/dtPreIRRbar[1][0], mean_lyNormOverDtPreIRR, std_lyNormOverDtPreIRR

    mean_lyNormPreIRRbar = lyPreIRRbar[int(prodN)][0]
    std_lyNormPreIRRbar = lyPreIRRbar[int(prodN)][1]/mt.sqrt(nbars) #/sqrt(N) since it is an average of N meas.

    mean_sigmatNormPreIRRbar = sigmatPreIRRbar[int(prodN)][0]/sigmatPreIRRbar[1][0]
    stdRel_sigmatNormPreIRRbar = ((sigmatPreIRRbar[int(prodN)][1]/mt.sqrt(nbars))/sigmatPreIRRbar[int(prodN)][0])**2 + ((sigmatPreIRRbar[1][1]/mt.sqrt(nbars))/sigmatPreIRRbar[1][0])**2 #/sqrt(N) since it is an average of N meas.
    stdRel_sigmatNormPreIRRbar = mt.sqrt(stdRel_sigmatNormPreIRRbar)
    std_sigmatNormPreIRRbar = stdRel_sigmatNormPreIRRbar * mean_sigmatNormPreIRRbar

    mean_lyNormBarOverArrayPreIRR = mean_lyNormPreIRRbar / mean_lyNormPreIRR
    stdRel_lyNormBarOverArrayPreIRR = (std_lyNormPreIRRbar/mean_lyNormPreIRRbar)**2 + (std_lyNormPreIRR/mean_lyNormPreIRR)**2
    stdRel_lyNormBarOverArrayPreIRR = mt.sqrt(stdRel_lyNormBarOverArrayPreIRR)
    std_lyNormBarOverArrayPreIRR = stdRel_lyNormBarOverArrayPreIRR * mean_lyNormBarOverArrayPreIRR

    mean_sigmatNormBarOverArrayPreIRR = mean_sigmatNormPreIRRbar / mean_sigmatNormPreIRR
    stdRel_sigmatNormBarOverArrayPreIRR = (std_sigmatNormPreIRRbar/mean_sigmatNormPreIRRbar)**2 + (std_sigmatNormPreIRR/mean_sigmatNormPreIRR)**2
    stdRel_sigmatNormBarOverArrayPreIRR = mt.sqrt(stdRel_sigmatNormBarOverArrayPreIRR)
    std_sigmatNormBarOverArrayPreIRR = stdRel_sigmatNormBarOverArrayPreIRR * mean_sigmatNormBarOverArrayPreIRR

    mean_dVdTNormPreIRR = dVdTPreIRR[int(prodN)][0]/dVdTPreIRR[1][0]
    stdRel_dVdTNormPreIRR = ( dVdTPreIRR[int(prodN)][1]/dVdTPreIRR[int(prodN)][0] )**2 + ( dVdTPreIRR[1][1]/dVdTPreIRR[1][0] )**2
    stdRel_dVdTNormPreIRR = mt.sqrt(stdRel_dVdTNormPreIRR)
    std_dVdTNormPreIRR = stdRel_dVdTNormPreIRR * mean_dVdTNormPreIRR

    #mean_sigmatNormOverLONormOverDtPreIRR = mean_sigmatNormPreIRR / mean_lyNormOverDtPreIRR
    #stdRel_sigmatNormOverLONormOverDtPreIRR = (std_sigmatNormPreIRR/mean_sigmatNormPreIRR)**2 + (std_lyNormOverDtPreIRR/mean_lyNormOverDtPreIRR)**2
    #stdRel_sigmatNormOverLONormOverDtPreIRR = mt.sqrt(stdRel_sigmatNormOverLONormOverDtPreIRR)
    #std_sigmatNormOverLONormOverDtPreIRR = stdRel_sigmatNormOverLONormOverDtPreIRR * mean_sigmatNormOverLONormOverDtPreIRR

    #mean_sigmatNormOverdVdTNormPreIRR = mean_sigmatNormPreIRR / mean_dVdTNormPreIRR
    #stdRel_sigmatNormOverdVdTNormPreIRR = (std_sigmatNormPreIRR/mean_sigmatNormPreIRR)**2 + (std_dVdTNormPreIRR/mean_dVdTNormPreIRR)**2
    #stdRel_sigmatNormOverdVdTNormPreIRR = mt.sqrt(stdRel_sigmatNormOverdVdTNormPreIRR)
    #std_sigmatNormOverdVdTNormPreIRR = stdRel_sigmatNormOverdVdTNormPreIRR * mean_sigmatNormOverdVdTNormPreIRR

    #Post
    lyPostIRR_np = np.array(lyPostIRR) 
    mean_lyPostIRR = lyPostIRR_np.mean()
    std_lyPostIRR = lyPostIRR_np.std()/mt.sqrt(len(lyPostIRR))

    lyNormPostIRR_np = np.array(lyNormPostIRR)
    mean_lyNormPostIRR = lyNormPostIRR_np.mean()
    std_lyNormPostIRR = lyNormPostIRR_np.std()/mt.sqrt(len(lyNormPostIRR))

    sigmatPostIRR_np = np.array(sigmatPostIRR)
    mean_sigmatPostIRR = sigmatPostIRR_np.mean()
    std_sigmatPostIRR = sigmatPostIRR_np.std()/mt.sqrt(len(sigmatPostIRR))

    sigmatNormPostIRR_np = np.array(sigmatNormPostIRR)
    mean_sigmatNormPostIRR = sigmatNormPostIRR_np.mean()
    std_sigmatNormPostIRR = sigmatNormPostIRR_np.std()/mt.sqrt(len(sigmatNormPostIRR))

    xtLeftPostIRR_np = np.array(xtLeftPostIRR)
    mean_xtLeftPostIRR = xtLeftPostIRR_np.mean()
    std_xtLeftPostIRR = xtLeftPostIRR_np.std()/mt.sqrt(len(xtLeftPostIRR))

    xtRightPostIRR_np = np.array(xtRightPostIRR)
    mean_xtRightPostIRR = xtRightPostIRR_np.mean()
    std_xtRightPostIRR = xtRightPostIRR_np.std()/mt.sqrt(len(xtRightPostIRR))

    mean_xtPostIRR = mean_xtLeftPostIRR + mean_xtRightPostIRR
    std_xtPostIRR = mt.sqrt(std_xtLeftPostIRR**2 +std_xtRightPostIRR**2)

    mean_lyNormOverDtPostIRR = ( mean_lyNormPostIRR / (dtPostIRRbar[int(prodN)][0]/dtPreIRRbar[1][0]) ) 
    stdRel_lyNormOverDtPostIRR = (std_lyNormPostIRR/mean_lyNormPostIRR)**2 + (dtPreIRRbar[int(prodN)][1]/dtPostIRRbar[int(prodN)][0])**2 + (dtPreIRRbar[1][1]/dtPreIRRbar[1][0])**2 #using std pre-irradiation since only 1 meas. post-irradiation available
    stdRel_lyNormOverDtPostIRR = mt.sqrt(stdRel_lyNormOverDtPostIRR)
    std_lyNormOverDtPostIRR = stdRel_lyNormOverDtPostIRR * mean_lyNormOverDtPostIRR
    print "POST: prodN, meanlyNorm, dt, dtref, dtratio, mean/dt, sigma_mean/dt: ", int(prodN), mean_lyNormPostIRR, dtPostIRRbar[int(prodN)][0], dtPreIRRbar[1][0], dtPostIRRbar[int(prodN)][0]/dtPreIRRbar[1][0], mean_lyNormOverDtPostIRR, std_lyNormOverDtPostIRR

    mean_lyNormPostIRRbar = lyPostIRRbar[int(prodN)][0]
    std_lyNormPostIRRbar = lyPreIRRbar[int(prodN)][1] #using std pre-irradiation since only 1 meas. post-irradiation available

    mean_sigmatNormPostIRRbar = sigmatPostIRRbar[int(prodN)][0]/sigmatPreIRRbar[1][0]
    stdRel_sigmatNormPostIRRbar = (sigmatPreIRRbar[int(prodN)][1]/sigmatPostIRRbar[int(prodN)][0])**2 + ((sigmatPreIRRbar[1][1]/mt.sqrt(nbars))/sigmatPreIRRbar[1][0])**2  #using std pre-irradiation since only 1 meas. post-irradiation available
    stdRel_sigmatNormPostIRRbar = mt.sqrt(stdRel_sigmatNormPostIRRbar)
    std_sigmatNormPostIRRbar = stdRel_sigmatNormPostIRRbar * mean_sigmatNormPostIRRbar

    mean_lyNormBarOverArrayPostIRR = mean_lyNormPostIRRbar / mean_lyNormPostIRR
    stdRel_lyNormBarOverArrayPostIRR = (std_lyNormPostIRRbar/mean_lyNormPostIRRbar)**2 + (std_lyNormPostIRR/mean_lyNormPostIRR)**2
    stdRel_lyNormBarOverArrayPostIRR = mt.sqrt(stdRel_lyNormBarOverArrayPostIRR)
    std_lyNormBarOverArrayPostIRR = stdRel_lyNormBarOverArrayPostIRR * mean_lyNormBarOverArrayPostIRR

    mean_sigmatNormBarOverArrayPostIRR = mean_sigmatNormPostIRRbar / mean_sigmatNormPostIRR
    stdRel_sigmatNormBarOverArrayPostIRR = (std_sigmatNormPostIRRbar/mean_sigmatNormPostIRRbar)**2 + (std_sigmatNormPostIRR/mean_sigmatNormPostIRR)**2
    stdRel_sigmatNormBarOverArrayPostIRR = mt.sqrt(stdRel_sigmatNormBarOverArrayPostIRR)
    std_sigmatNormBarOverArrayPostIRR = stdRel_sigmatNormBarOverArrayPostIRR * mean_sigmatNormBarOverArrayPostIRR

    mean_dVdTNormPostIRR = dVdTPostIRR[int(prodN)][0]/dVdTPreIRR[1][0]
    stdRel_dVdTNormPostIRR = ( dVdTPostIRR[int(prodN)][1]/dVdTPostIRR[int(prodN)][0] )**2 + ( dVdTPreIRR[1][1]/dVdTPreIRR[1][0] )**2
    stdRel_dVdTNormPostIRR = mt.sqrt(stdRel_dVdTNormPostIRR)
    std_dVdTNormPostIRR = stdRel_dVdTNormPostIRR * mean_dVdTNormPostIRR

    #mean_sigmatNormOverLONormOverDtPostIRR = mean_sigmatNormPostIRR / mean_lyNormOverDtPostIRR
    #stdRel_sigmatNormOverLONormOverDtPostIRR = (std_sigmatNormPostIRR/mean_sigmatNormPostIRR)**2 + (std_lyNormOverDtPostIRR/mean_lyNormOverDtPostIRR)**2
    #stdRel_sigmatNormOverLONormOverDtPostIRR = mt.sqrt(stdRel_sigmatNormOverLONormOverDtPostIRR)
    #std_sigmatNormOverLONormOverDtPostIRR = stdRel_sigmatNormOverLONormOverDtPostIRR * mean_sigmatNormOverLONormOverDtPostIRR

    #mean_sigmatNormOverdVdTNormPostIRR = mean_sigmatNormPostIRR / mean_dVdTNormPostIRR
    #stdRel_sigmatNormOverdVdTNormPostIRR = (std_sigmatNormPostIRR/mean_sigmatNormPostIRR)**2 + (std_dVdTNormPostIRR/mean_dVdTNormPostIRR)**2
    #stdRel_sigmatNormOverdVdTNormPostIRR = mt.sqrt(stdRel_sigmatNormOverdVdTNormPostIRR)
    #std_sigmatNormOverdVdTNormPostIRR = stdRel_sigmatNormOverdVdTNormPostIRR * mean_sigmatNormOverdVdTNormPostIRR

    #Post/Pre
    lyRatioIRR_np = np.array(lyRatioIRR) 
    mean_lyRatioIRR = lyRatioIRR_np.mean()
    std_lyRatioIRR = lyRatioIRR_np.std()/mt.sqrt(len(lyRatioIRR))

    lyNormRatioIRR_np = np.array(lyNormRatioIRR)
    mean_lyNormRatioIRR = lyNormRatioIRR_np.mean()
    std_lyNormRatioIRR = lyNormRatioIRR_np.std()/mt.sqrt(len(lyNormRatioIRR))

    sigmatRatioIRR_np = np.array(sigmatRatioIRR)
    mean_sigmatRatioIRR = sigmatRatioIRR_np.mean()
    std_sigmatRatioIRR = sigmatRatioIRR_np.std()/mt.sqrt(len(sigmatRatioIRR))

    sigmatNormRatioIRR_np = np.array(sigmatNormRatioIRR)
    mean_sigmatNormRatioIRR = sigmatNormRatioIRR_np.mean()
    std_sigmatNormRatioIRR = sigmatNormRatioIRR_np.std()/mt.sqrt(len(sigmatNormRatioIRR))

    xtLeftRatioIRR_np = np.array(xtLeftRatioIRR)
    mean_xtLeftRatioIRR = xtLeftRatioIRR_np.mean()
    std_xtLeftRatioIRR = xtLeftRatioIRR_np.std()/mt.sqrt(len(xtLeftRatioIRR))

    xtRightRatioIRR_np = np.array(xtRightRatioIRR)
    mean_xtRightRatioIRR = xtRightRatioIRR_np.mean()
    std_xtRightRatioIRR = xtRightRatioIRR_np.std()/mt.sqrt(len(xtRightRatioIRR))

    mean_xtRatioIRR = (mean_xtLeftRatioIRR + mean_xtRightRatioIRR)/2.
    std_xtRatioIRR = 0.5*mt.sqrt(std_xtLeftRatioIRR**2 +std_xtRightRatioIRR**2)

    mean_lyNormBarOverArrayRatioIRR = mean_lyNormBarOverArrayPostIRR/mean_lyNormBarOverArrayPreIRR
    stdRel_lyNormBarOverArrayRatioIRR = (std_lyNormBarOverArrayPostIRR/mean_lyNormBarOverArrayPostIRR)**2 + (std_lyNormBarOverArrayPreIRR/mean_lyNormBarOverArrayPreIRR)**2
    stdRel_lyNormBarOverArrayRatioIRR = mt.sqrt(stdRel_lyNormBarOverArrayRatioIRR)
    std_lyNormBarOverArrayRatioIRR = stdRel_lyNormBarOverArrayRatioIRR * mean_lyNormBarOverArrayRatioIRR

    mean_sigmatNormBarOverArrayRatioIRR = mean_sigmatNormBarOverArrayPostIRR/mean_sigmatNormBarOverArrayPreIRR
    stdRel_sigmatNormBarOverArrayRatioIRR = (std_sigmatNormBarOverArrayPostIRR/mean_sigmatNormBarOverArrayPostIRR)**2 + (std_sigmatNormBarOverArrayPreIRR/mean_sigmatNormBarOverArrayPreIRR)**2
    stdRel_sigmatNormBarOverArrayRatioIRR = mt.sqrt(stdRel_sigmatNormBarOverArrayRatioIRR)
    std_sigmatNormBarOverArrayRatioIRR = stdRel_sigmatNormBarOverArrayRatioIRR * mean_sigmatNormBarOverArrayRatioIRR

    #mean_sigmatNormOverLONormOverDtRatioIRR = mean_sigmatNormOverLONormOverDtPostIRR / mean_sigmatNormOverLONormOverDtPreIRR 
    #stdRel_sigmatNormOverLONormOverDtRatioIRR = (std_sigmatNormOverLONormOverDtPostIRR/mean_sigmatNormOverLONormOverDtPostIRR)**2 +(std_sigmatNormOverLONormOverDtPreIRR/mean_sigmatNormOverLONormOverDtPreIRR)**2
    #stdRel_sigmatNormOverLONormOverDtRatioIRR = mt.sqrt(stdRel_sigmatNormOverLONormOverDtRatioIRR)
    #std_sigmatNormOverLONormOverDtRatioIRR = stdRel_sigmatNormOverLONormOverDtRatioIRR * mean_sigmatNormOverLONormOverDtRatioIRR

    #mean_sigmatNormOverdVdTNormRatioIRR = mean_sigmatNormOverdVdTNormPostIRR / mean_sigmatNormOverdVdTNormPreIRR
    #stdRel_sigmatNormOverdVdTNormRatioIRR = (std_sigmatNormOverdVdTNormPostIRR/mean_sigmatNormOverdVdTNormPostIRR)**2 + (std_sigmatNormOverdVdTNormPreIRR/mean_sigmatNormOverdVdTNormPreIRR)**2
    #stdRel_sigmatNormOverdVdTNormRatioIRR = mt.sqrt(stdRel_sigmatNormOverdVdTNormRatioIRR)
    #std_sigmatNormOverdVdTNormRatioIRR = stdRel_sigmatNormOverdVdTNormRatioIRR * mean_sigmatNormOverdVdTNormRatioIRR


    #Pre
    print lyPreIRR_np, mean_lyPreIRR, std_lyPreIRR
    print lyNormPreIRR_np, mean_lyNormPreIRR, std_lyNormPreIRR
    print sigmatPreIRR_np, mean_sigmatPreIRR, std_sigmatPreIRR
    print sigmatNormPreIRR_np, mean_sigmatNormPreIRR, std_sigmatNormPreIRR
    print xtLeftPreIRR_np, mean_xtLeftPreIRR, std_xtLeftPreIRR
    print xtRightPreIRR_np, mean_xtRightPreIRR, std_xtRightPreIRR
    print mean_xtPreIRR, std_xtPreIRR

    histos['lyPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyPreIRR)
    histos['lyPreIRR'+'VsProd'].SetPointError(iprod,0.,std_lyPreIRR)

    histos['lyNormPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormPreIRR)
    histos['lyNormPreIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormPreIRR)

    histos['sigmatPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatPreIRR)
    histos['sigmatPreIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatPreIRR)

    histos['sigmatNormPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormPreIRR)
    histos['sigmatNormPreIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormPreIRR)

    histos['xtPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_xtPreIRR)
    histos['xtPreIRR'+'VsProd'].SetPointError(iprod,0.,std_xtPreIRR)

    histos['lyNormBarOverArrayPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormBarOverArrayPreIRR)
    histos['lyNormBarOverArrayPreIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormBarOverArrayPreIRR)

    histos['sigmatNormBarOverArrayPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormBarOverArrayPreIRR)
    histos['sigmatNormBarOverArrayPreIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormBarOverArrayPreIRR)

    #histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormOverLONormOverDtPreIRR)
    #histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormOverLONormOverDtPreIRR)

    #histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormOverdVdTNormPreIRR)
    #histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormOverdVdTNormPreIRR)

    histos['sigmatNormVsLONormPreIRR'].SetPoint(iprod,mean_lyNormPreIRR,mean_sigmatNormPreIRR)
    histos['sigmatNormVsLONormPreIRR'].SetPointError(iprod,std_lyNormPreIRR,std_sigmatNormPreIRR)

    histos['sigmatNormVsLONormOverDtPreIRR'].SetPoint(iprod,mean_lyNormOverDtPreIRR,mean_sigmatNormPreIRR)
    histos['sigmatNormVsLONormOverDtPreIRR'].SetPointError(iprod,std_lyNormOverDtPreIRR,std_sigmatNormPreIRR)

    histos['sigmatNormVsdVdTNormPreIRR'].SetPoint(iprod,mean_dVdTNormPreIRR,mean_sigmatNormPreIRR)
    histos['sigmatNormVsdVdTNormPreIRR'].SetPointError(iprod,std_dVdTNormPreIRR,std_sigmatNormPreIRR)

    histos['LONormBarVsArrayPreIRR'].SetPoint(iprod,mean_lyNormPreIRR,mean_lyNormPreIRRbar)
    histos['LONormBarVsArrayPreIRR'].SetPointError(iprod,std_lyNormPreIRR,std_lyNormPreIRRbar)

    histos['sigmatNormBarVsArrayPreIRR'].SetPoint(iprod,mean_sigmatNormPreIRR,mean_sigmatNormPreIRRbar)
    histos['sigmatNormBarVsArrayPreIRR'].SetPointError(iprod,std_sigmatNormPreIRR,std_sigmatNormPreIRRbar)

    #Post
    print lyPostIRR_np, mean_lyPostIRR, std_lyPostIRR
    print lyNormPostIRR_np, mean_lyNormPostIRR, std_lyNormPostIRR
    print sigmatPostIRR_np, mean_sigmatPostIRR, std_sigmatPostIRR
    print sigmatNormPostIRR_np, mean_sigmatNormPostIRR, std_sigmatNormPostIRR
    print xtLeftPostIRR_np, mean_xtLeftPostIRR, std_xtLeftPostIRR
    print xtRightPostIRR_np, mean_xtRightPostIRR, std_xtRightPostIRR
    print mean_xtPostIRR, std_xtPostIRR

    histos['lyPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyPostIRR)
    histos['lyPostIRR'+'VsProd'].SetPointError(iprod,0.,std_lyPostIRR)

    histos['lyNormPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormPostIRR)
    histos['lyNormPostIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormPostIRR)

    histos['sigmatPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatPostIRR)
    histos['sigmatPostIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatPostIRR)

    histos['sigmatNormPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormPostIRR)
    histos['sigmatNormPostIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormPostIRR)

    histos['xtPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_xtPostIRR)
    histos['xtPostIRR'+'VsProd'].SetPointError(iprod,0.,std_xtPostIRR)

    histos['lyNormBarOverArrayPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormBarOverArrayPostIRR)
    histos['lyNormBarOverArrayPostIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormBarOverArrayPostIRR)

    histos['sigmatNormBarOverArrayPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormBarOverArrayPostIRR)
    histos['sigmatNormBarOverArrayPostIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormBarOverArrayPostIRR)

    #histos['sigmatNormOverLONormOverDtPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormOverLONormOverDtPostIRR)
    #histos['sigmatNormOverLONormOverDtPostIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormOverLONormOverDtPostIRR)

    #histos['sigmatNormOverdVdTNormPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormOverdVdTNormPostIRR)
    #histos['sigmatNormOverdVdTNormPostIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormOverdVdTNormPostIRR)

    histos['sigmatNormVsLONormPostIRR'].SetPoint(iprod,mean_lyNormPostIRR,mean_sigmatNormPostIRR)
    histos['sigmatNormVsLONormPostIRR'].SetPointError(iprod,std_lyNormPostIRR,std_sigmatNormPostIRR)

    histos['sigmatNormVsLONormOverDtPostIRR'].SetPoint(iprod,mean_lyNormOverDtPostIRR,mean_sigmatNormPostIRR)
    histos['sigmatNormVsLONormOverDtPostIRR'].SetPointError(iprod,std_lyNormOverDtPostIRR,std_sigmatNormPostIRR)

    histos['sigmatNormVsdVdTNormPostIRR'].SetPoint(iprod,mean_dVdTNormPostIRR,mean_sigmatNormPostIRR)
    histos['sigmatNormVsdVdTNormPostIRR'].SetPointError(iprod,std_dVdTNormPostIRR,std_sigmatNormPostIRR)

    histos['LONormBarVsArrayPostIRR'].SetPoint(iprod,mean_lyNormPostIRR,mean_lyNormPostIRRbar)
    histos['LONormBarVsArrayPostIRR'].SetPointError(iprod,std_lyNormPostIRR,std_lyNormPostIRRbar)

    histos['sigmatNormBarVsArrayPostIRR'].SetPoint(iprod,mean_sigmatNormPostIRR,mean_sigmatNormPostIRRbar)
    histos['sigmatNormBarVsArrayPostIRR'].SetPointError(iprod,std_sigmatNormPostIRR,std_sigmatNormPostIRRbar)


    #Post/Pre
    print lyRatioIRR_np, mean_lyRatioIRR, std_lyRatioIRR
    print lyNormRatioIRR_np, mean_lyNormRatioIRR, std_lyNormRatioIRR
    print sigmatRatioIRR_np, mean_sigmatRatioIRR, std_sigmatRatioIRR
    print sigmatNormRatioIRR_np, mean_sigmatNormRatioIRR, std_sigmatNormRatioIRR
    print xtLeftRatioIRR_np, mean_xtLeftRatioIRR, std_xtLeftRatioIRR
    print xtRightRatioIRR_np, mean_xtRightRatioIRR, std_xtRightRatioIRR
    print mean_xtRatioIRR, std_xtRatioIRR

    histos['lyRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyRatioIRR)
    histos['lyRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_lyRatioIRR)

    histos['lyNormRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormRatioIRR)
    histos['lyNormRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormRatioIRR)

    histos['sigmatRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatRatioIRR)
    histos['sigmatRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatRatioIRR)

    histos['sigmatNormRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormRatioIRR)
    histos['sigmatNormRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormRatioIRR)

    histos['xtRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_xtRatioIRR)
    histos['xtRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_xtRatioIRR)

    histos['lyNormBarOverArrayRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormBarOverArrayRatioIRR)
    histos['lyNormBarOverArrayRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormBarOverArrayRatioIRR)

    histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormBarOverArrayRatioIRR)
    histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormBarOverArrayRatioIRR)

    #histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormOverLONormOverDtRatioIRR)
    #histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormOverLONormOverDtRatioIRR)

    #histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormOverdVdTNormRatioIRR)
    #histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormOverdVdTNormRatioIRR)



#Draw and Save plots
R.gStyle.SetOptTitle(0)
c1=R.TCanvas("c1","c1",800,800)
c1_pad1 = R.TPad("c1_pad1", "c1_pad1", 0, 0.4, 1, 1.0)
c1_pad1.SetBottomMargin(0.008)#Upper and lower plot are joined
c1_pad1.SetGridx()
c1_pad1.SetGridy()
c1_pad1.Draw()
c1_pad2 = R.TPad("c1_pad2", "c1_pad2", 0, 0.05, 1, 0.4)
c1_pad2.SetTopMargin(0.05);#Upper and lower plot are joined
c1_pad2.SetBottomMargin(0.4);
c1_pad2.SetGridx()
c1_pad2.SetGridy()
c1_pad2.Draw()

legend1 = R.TLegend(0.6,0.7,0.9,0.9)

text1=R.TLatex()
text1.SetTextSize(0.04)

#ly
c1_pad1.cd()
histos['lyPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['lyPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['lyPreIRR'+'VsProd'].SetMarkerColor(1)
histos['lyPostIRR'+'VsProd'].SetMarkerColor(2)
histos['lyPreIRR'+'VsProd'].GetYaxis().SetLimits(35.,90.)
histos['lyPreIRR'+'VsProd'].GetYaxis().SetRangeUser(35.,90.)
histos['lyPreIRR'+'VsProd'].GetYaxis().SetTitle("LO [ADC counts]")
histos['lyPreIRR'+'VsProd'].Draw("ap")
histos['lyPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['lyPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['lyPostIRR'+'VsProd'],"Irrad. 45-50 kGy","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['lyRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['lyRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['lyRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.6,1.1)
histos['lyRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.6,1.1)
histos['lyRatioIRR'+'VsProd'].GetYaxis().SetTitle("LO_{Irr}/LO")
histos['lyRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['lyRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['lyRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['lyRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['lyRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'ly'+'VsProd'+ext)

#lyNorm
c1_pad1.cd()
histos['lyNormPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['lyNormPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['lyNormPreIRR'+'VsProd'].SetMarkerColor(1)
histos['lyNormPostIRR'+'VsProd'].SetMarkerColor(2)
histos['lyNormPreIRR'+'VsProd'].GetYaxis().SetLimits(0.5,1.5)
histos['lyNormPreIRR'+'VsProd'].GetYaxis().SetRangeUser(0.5,1.5)
histos['lyNormPreIRR'+'VsProd'].GetYaxis().SetTitle("LO/LO_{ref}")
histos['lyNormPreIRR'+'VsProd'].Draw("ap")
histos['lyNormPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['lyNormPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['lyNormPostIRR'+'VsProd'],"Irrad. 45-50 kGy","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['lyNormRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['lyNormRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['lyNormRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.6,1.1)
histos['lyNormRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.6,1.1)
histos['lyNormRatioIRR'+'VsProd'].GetYaxis().SetTitle("LO_{Irr}/LO normalized to reference")
histos['lyNormRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['lyNormRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['lyNormRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['lyNormRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['lyNormRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'lyNorm'+'VsProd'+ext)

#sigmat
c1_pad1.cd()
histos['sigmatPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatPreIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatPostIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatPreIRR'+'VsProd'].GetYaxis().SetLimits(100.,200.)
histos['sigmatPreIRR'+'VsProd'].GetYaxis().SetRangeUser(100.,200.)
histos['sigmatPreIRR'+'VsProd'].GetYaxis().SetTitle("#sigma_{t} [ps]")
histos['sigmatPreIRR'+'VsProd'].Draw("ap")
histos['sigmatPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmatPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['sigmatPostIRR'+'VsProd'],"Irrad. 45-50 kGy","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['sigmatRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.8,1.3)
histos['sigmatRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.8,1.3)
histos['sigmatRatioIRR'+'VsProd'].GetYaxis().SetTitle("#sigma_{t,Irr}/#sigma_{t}")
histos['sigmatRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['sigmatRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['sigmatRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['sigmatRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['sigmatRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'sigmat'+'VsProd'+ext)

#sigmatNorm
c1_pad1.cd()
histos['sigmatNormPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNormPreIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatNormPostIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatNormPreIRR'+'VsProd'].GetYaxis().SetLimits(0.7,1.4)
histos['sigmatNormPreIRR'+'VsProd'].GetYaxis().SetRangeUser(0.7,1.4)
histos['sigmatNormPreIRR'+'VsProd'].GetYaxis().SetTitle("#sigma_{t}/#sigma_{t,ref}")
histos['sigmatNormPreIRR'+'VsProd'].Draw("ap")
histos['sigmatNormPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['sigmatNormPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['sigmatNormPostIRR'+'VsProd'],"Irrad. 45-50 kGy","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['sigmatNormRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatNormRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.8,1.3)
histos['sigmatNormRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.8,1.3)
histos['sigmatNormRatioIRR'+'VsProd'].GetYaxis().SetTitle("#sigma_{t,Irr}/#sigma_{t} normalized to reference")
histos['sigmatNormRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['sigmatNormRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['sigmatNormRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['sigmatNormRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['sigmatNormRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'sigmatNorm'+'VsProd'+ext)

#xt
c1_pad1.cd()
histos['xtPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['xtPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['xtPreIRR'+'VsProd'].SetMarkerColor(1)
histos['xtPostIRR'+'VsProd'].SetMarkerColor(2)
histos['xtPreIRR'+'VsProd'].GetYaxis().SetLimits(0.,0.5)
histos['xtPreIRR'+'VsProd'].GetYaxis().SetRangeUser(0.,0.5)
histos['xtPreIRR'+'VsProd'].GetYaxis().SetTitle("XT (Left+Right)")
histos['xtPreIRR'+'VsProd'].Draw("ap")
histos['xtPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.AddEntry(histos['xtPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['xtPostIRR'+'VsProd'],"Irrad. 45-50 kGy","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['xtRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['xtRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['xtRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.,2.)
histos['xtRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.,2.)
histos['xtRatioIRR'+'VsProd'].GetYaxis().SetTitle("XT_{Irr}/XT")
histos['xtRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['xtRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['xtRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['xtRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['xtRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'xt'+'VsProd'+ext)

#lyNormBarOverArray
c1_pad1.cd()
histos['lyNormBarOverArrayPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['lyNormBarOverArrayPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['lyNormBarOverArrayPreIRR'+'VsProd'].SetMarkerColor(1)
histos['lyNormBarOverArrayPostIRR'+'VsProd'].SetMarkerColor(2)
histos['lyNormBarOverArrayPreIRR'+'VsProd'].GetYaxis().SetLimits(0.,2.0)
histos['lyNormBarOverArrayPreIRR'+'VsProd'].GetYaxis().SetRangeUser(0.,2.0)
histos['lyNormBarOverArrayPreIRR'+'VsProd'].GetYaxis().SetTitle("(LO/LO_{ref})_{bar}/(LO/LO_{ref})_{array}")
histos['lyNormBarOverArrayPreIRR'+'VsProd'].Draw("ap")
histos['lyNormBarOverArrayPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.SetX1NDC(0.4)
legend1.SetX2NDC(0.9)
legend1.SetY1NDC(0.7)
legend1.SetY2NDC(0.9)
legend1.AddEntry(histos['lyNormBarOverArrayPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['lyNormBarOverArrayPostIRR'+'VsProd'],"Irrad. 45-50 kGy (ARRAY)\n 9-10 kGy (BAR)","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.5,1.5)
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.5,1.5)
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetTitle("Ratio Post/Pre Irr.")
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['lyNormBarOverArrayRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'lyNormBarOverArray'+'VsProd'+ext)

#sigmatNormBarOverArray
c1_pad1.cd()
histos['sigmatNormBarOverArrayPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormBarOverArrayPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNormBarOverArrayPreIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatNormBarOverArrayPostIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatNormBarOverArrayPreIRR'+'VsProd'].GetYaxis().SetLimits(0.4,2.4)
histos['sigmatNormBarOverArrayPreIRR'+'VsProd'].GetYaxis().SetRangeUser(0.4,2.4)
histos['sigmatNormBarOverArrayPreIRR'+'VsProd'].GetYaxis().SetTitle("(#sigma_{t}/#sigma_{t,ref})_{bar}/(#sigma_{t}/#sigma_{t,ref})_{array}")
histos['sigmatNormBarOverArrayPreIRR'+'VsProd'].Draw("ap") 
histos['sigmatNormBarOverArrayPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.SetX1NDC(0.4)
legend1.SetX2NDC(0.9)
legend1.SetY1NDC(0.7)
legend1.SetY2NDC(0.9)
legend1.AddEntry(histos['sigmatNormBarOverArrayPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['sigmatNormBarOverArrayPostIRR'+'VsProd'],"Irrad. 45-50 kGy (ARRAY)\n 9-10 kGy (BAR)","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.5,1.5)
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.5,1.5)
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetTitle("Ratio Post/Pre Irr.")
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['sigmatNormBarOverArrayRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'sigmatNormBarOverArray'+'VsProd'+ext)

'''
#sigmatNormOverLONormOverDt
c1_pad1.cd()
histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormOverLONormOverDtPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatNormOverLONormOverDtPostIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'].GetYaxis().SetLimits(0.,2.)
histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'].GetYaxis().SetRangeUser(0.,2.)
histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'].GetYaxis().SetTitle("(#sigma_{t}/#sigma_{t,ref})/[(LO/LO_{ref})/(#tau_{decay}/#tau_{ref})]") 
histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'].Draw("ap") 
histos['sigmatNormOverLONormOverDtPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.SetX1NDC(0.6)
legend1.SetX2NDC(0.9)
legend1.SetY1NDC(0.7)
legend1.SetY2NDC(0.9)
legend1.AddEntry(histos['sigmatNormOverLONormOverDtPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['sigmatNormOverLONormOverDtPostIRR'+'VsProd'],"Irrad. 45-50 kGy","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.5,1.5)
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.5,1.5)
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].GetYaxis().SetTitle("Ratio Post/Pre Irr.")
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['sigmatNormOverLONormOverDtRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'sigmatNormOverLONormOverDt'+'VsProd'+ext)

#sigmatNormOverdVdTNorm
c1_pad1.cd()
histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormOverdVdTNormPostIRR'+'VsProd'].SetMarkerStyle(22)
histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatNormOverdVdTNormPostIRR'+'VsProd'].SetMarkerColor(2)
histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'].GetYaxis().SetLimits(0.,2.)
histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'].GetYaxis().SetRangeUser(0.,2.)
histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'].GetYaxis().SetTitle("(#sigma_{t}/#sigma_{t,ref}) / [(dV/dT)/(dV/dT)_{ref}]") 
histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'].Draw("ap") 
histos['sigmatNormOverdVdTNormPostIRR'+'VsProd'].Draw("psame")
legend1.Clear()
legend1.SetX1NDC(0.6)
legend1.SetX2NDC(0.9)
legend1.SetY1NDC(0.7)
legend1.SetY2NDC(0.9)
legend1.AddEntry(histos['sigmatNormOverdVdTNormPreIRR'+'VsProd'],"No Irrad.","pe")
legend1.AddEntry(histos['sigmatNormOverdVdTNormPostIRR'+'VsProd'],"Irrad. 45-50 kGy","pe")
legend1.Draw()
text1.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
c1_pad2.cd()
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].SetMarkerStyle(20)
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].SetMarkerColor(1)
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].GetYaxis().SetLimits(0.5,1.5)
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].GetYaxis().SetRangeUser(0.5,1.5)
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].GetYaxis().SetTitle("Ratio Post/Pre Irr.")
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].GetYaxis().SetNdivisions(505)
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].GetYaxis().SetLabelSize(0.06)
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].GetYaxis().SetTitleSize(0.06)
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].GetYaxis().SetTitleOffset(0.6)
histos['sigmatNormOverdVdTNormRatioIRR'+'VsProd'].Draw("ap")
for ext in ['.pdf','.png']:
    c1.SaveAs(outputdir+"/"+'sigmatNormOverdVdTNorm'+'VsProd'+ext)
'''

#-----------------------------------------------------------

c2=R.TCanvas("c2","c2",800,800)
c2.SetGridx()
c2.SetGridy()

legend2 = R.TLegend(0.6,0.7,0.9,0.9)

text2=R.TLatex()
text2.SetTextSize(0.025)

#sigmatNorm vs lyNorm  
histos['sigmatNormVsLONormPreIRR'].SetMarkerStyle(20)
histos['sigmatNormVsLONormPostIRR'].SetMarkerStyle(22)
histos['sigmatNormVsLONormPreIRR'].SetMarkerColor(1)
histos['sigmatNormVsLONormPostIRR'].SetMarkerColor(2)
histos['sigmatNormVsLONormPreIRR'].GetXaxis().SetLimits(0.4,1.6)
histos['sigmatNormVsLONormPreIRR'].GetXaxis().SetRangeUser(0.4,1.6)
histos['sigmatNormVsLONormPreIRR'].GetYaxis().SetLimits(0.7,1.4)
histos['sigmatNormVsLONormPreIRR'].GetYaxis().SetRangeUser(0.7,1.4)
histos['sigmatNormVsLONormPreIRR'].GetXaxis().SetTitle("LO/LO_{ref}")
histos['sigmatNormVsLONormPreIRR'].GetYaxis().SetTitle("#sigma_{t}/#sigma_{t,ref}")
histos['sigmatNormVsLONormPreIRR'].Draw("ap")
histos['sigmatNormVsLONormPostIRR'].Draw("p")
legend2.Clear()
legend2.AddEntry(histos['sigmatNormVsLONormPreIRR'],"No Irrad.","pe")
legend2.AddEntry(histos['sigmatNormVsLONormPostIRR'],"Irrad. 45-50 kGy","pe")
legend2.Draw()
text2.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c2.SaveAs(outputdir+"/"+'sigmatNormVsLONorm'+ext)

#sigmatNorm vs lyNorm/Dt  
histos['sigmatNormVsLONormOverDtPreIRR'].SetMarkerStyle(20)
histos['sigmatNormVsLONormOverDtPostIRR'].SetMarkerStyle(22)
histos['sigmatNormVsLONormOverDtPreIRR'].SetMarkerColor(1)
histos['sigmatNormVsLONormOverDtPostIRR'].SetMarkerColor(2)
histos['sigmatNormVsLONormOverDtPreIRR'].GetXaxis().SetLimits(0.4,1.6)
histos['sigmatNormVsLONormOverDtPreIRR'].GetXaxis().SetRangeUser(0.4,1.6)
histos['sigmatNormVsLONormOverDtPreIRR'].GetYaxis().SetLimits(0.7,1.4)
histos['sigmatNormVsLONormOverDtPreIRR'].GetYaxis().SetRangeUser(0.7,1.4)
histos['sigmatNormVsLONormOverDtPreIRR'].GetXaxis().SetTitle("(LO/LO_{ref})/(#tau_{decay}/#tau_{ref})")
histos['sigmatNormVsLONormOverDtPreIRR'].GetYaxis().SetTitle("#sigma_{t}/#sigma_{t,ref}")
histos['sigmatNormVsLONormOverDtPreIRR'].Draw("ap")
histos['sigmatNormVsLONormOverDtPostIRR'].Draw("p")
legend2.Clear()
legend2.AddEntry(histos['sigmatNormVsLONormOverDtPreIRR'],"No Irrad.","pe")
legend2.AddEntry(histos['sigmatNormVsLONormOverDtPostIRR'],"Irrad. 45-50 kGy","pe")
legend2.Draw()
text2.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM and PMT Benches")
for ext in ['.pdf','.png']:
    c2.SaveAs(outputdir+"/"+'sigmatNormVsLONormOverDt'+ext)

#sigmatNorm vs dV/dT
histos['sigmatNormVsdVdTNormPreIRR'].SetMarkerStyle(20)
histos['sigmatNormVsdVdTNormPostIRR'].SetMarkerStyle(22)
histos['sigmatNormVsdVdTNormPreIRR'].SetMarkerColor(1)
histos['sigmatNormVsdVdTNormPostIRR'].SetMarkerColor(2)
histos['sigmatNormVsdVdTNormPreIRR'].GetXaxis().SetLimits(0.4,1.6)
histos['sigmatNormVsdVdTNormPreIRR'].GetXaxis().SetRangeUser(0.4,1.6)
histos['sigmatNormVsdVdTNormPreIRR'].GetYaxis().SetLimits(0.7,1.4)
histos['sigmatNormVsdVdTNormPreIRR'].GetYaxis().SetRangeUser(0.7,1.4)
histos['sigmatNormVsdVdTNormPreIRR'].GetXaxis().SetTitle("(dV/dT) / (dV/dT)_{ref}")
histos['sigmatNormVsdVdTNormPreIRR'].GetYaxis().SetTitle("#sigma_{t}/#sigma_{t,ref}")
histos['sigmatNormVsdVdTNormPreIRR'].Draw("ap")
histos['sigmatNormVsdVdTNormPostIRR'].Draw("p")
legend2.Clear()
legend2.AddEntry(histos['sigmatNormVsdVdTNormPreIRR'],"No Irrad.","pe")
legend2.AddEntry(histos['sigmatNormVsdVdTNormPostIRR'],"Irrad. 45-50 kGy","pe")
legend2.Draw()
text2.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c2.SaveAs(outputdir+"/"+'sigmatNormVsdVdTNorm'+ext)

legend3 = R.TLegend(0.4,0.7,0.9,0.9)

#lyNorm bar vs array  
histos['LONormBarVsArrayPreIRR'].SetMarkerStyle(20)
histos['LONormBarVsArrayPostIRR'].SetMarkerStyle(22)
histos['LONormBarVsArrayPreIRR'].SetMarkerColor(1)
histos['LONormBarVsArrayPostIRR'].SetMarkerColor(2)
histos['LONormBarVsArrayPreIRR'].GetXaxis().SetLimits(0.6,1.4)
histos['LONormBarVsArrayPreIRR'].GetXaxis().SetRangeUser(0.6,1.4)
histos['LONormBarVsArrayPreIRR'].GetYaxis().SetLimits(0.6,1.4)
histos['LONormBarVsArrayPreIRR'].GetYaxis().SetRangeUser(0.6,1.4)
histos['LONormBarVsArrayPreIRR'].GetXaxis().SetTitle("LO/LO_{ref} Array")
histos['LONormBarVsArrayPreIRR'].GetYaxis().SetTitle("LO/LO_{ref} Bar")
histos['LONormBarVsArrayPreIRR'].Draw("ap")
histos['LONormBarVsArrayPostIRR'].Draw("p")
legend3.Clear()
legend3.AddEntry(histos['LONormBarVsArrayPreIRR'],"No Irrad.","pe")
legend3.AddEntry(histos['LONormBarVsArrayPostIRR'],"Irrad. 45-50 kGy (ARRAY)\n 9-10 kGy (BAR)","pe")
legend3.Draw()
text2.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c2.SaveAs(outputdir+"/"+'LONormBarVsArray'+ext)

#sigmat bar vs array   'sigmatNormBarVsArrayPreIRR'
histos['sigmatNormBarVsArrayPreIRR'].SetMarkerStyle(20)
histos['sigmatNormBarVsArrayPostIRR'].SetMarkerStyle(22)
histos['sigmatNormBarVsArrayPreIRR'].SetMarkerColor(1)
histos['sigmatNormBarVsArrayPostIRR'].SetMarkerColor(2)
histos['sigmatNormBarVsArrayPreIRR'].GetXaxis().SetLimits(0.8,2.2)
histos['sigmatNormBarVsArrayPreIRR'].GetXaxis().SetRangeUser(0.8,2.2)
histos['sigmatNormBarVsArrayPreIRR'].GetYaxis().SetLimits(0.8,2.2)
histos['sigmatNormBarVsArrayPreIRR'].GetYaxis().SetRangeUser(0.8,2.2)
histos['sigmatNormBarVsArrayPreIRR'].GetXaxis().SetTitle("#sigma_{t}/#sigma_{t,ref} Array")
histos['sigmatNormBarVsArrayPreIRR'].GetYaxis().SetTitle("#sigma_{t}/#sigma_{t,ref} Bar")
histos['sigmatNormBarVsArrayPreIRR'].Draw("ap")
histos['sigmatNormBarVsArrayPostIRR'].Draw("p")
legend3.Clear()
legend3.AddEntry(histos['sigmatNormBarVsArrayPreIRR'],"No Irrad.","pe")
legend3.AddEntry(histos['sigmatNormBarVsArrayPostIRR'],"Irrad. 45-50 kGy (ARRAY)\n 9-10 kGy (BAR)","pe")
legend3.Draw()
text2.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c2.SaveAs(outputdir+"/"+'sigmatNormBarVsArray'+ext)

##################################################################

out=R.TFile(outputdir+"/"+"lyArrayIrradPlots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()
    



