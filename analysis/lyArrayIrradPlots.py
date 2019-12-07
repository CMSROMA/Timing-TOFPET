import ROOT as R
R.gROOT.SetBatch(1)

from array import array
import math as mt
import numpy as np

outputdir = "/afs/cern.ch/user/s/santanas/www/TOFPET2/LYSOARRAYS_Casaccia"
pixelRes = 90 #ps

#read Tgraphs from single bars file
fileSingleBars = "LYMergedPlots.root" 
tfileSingleBars = R.TFile(fileSingleBars)
#
dt_ByProd=R.TGraphErrors()
dt_IRR9K_ByProd=R.TGraphErrors()
R.gDirectory.GetObject("dt_ByProd",dt_ByProd)
R.gDirectory.GetObject("dt_IRR9K_ByProd",dt_IRR9K_ByProd)
#
tfileSingleBars.Close()

npoints = dt_ByProd.GetN() 
print "npoints:", npoints
x=R.Double()
y=R.Double()
dtPreIRR={}
dtPostIRR={}
for point in range(0,npoints):
    dt_ByProd.GetPoint(point,x,y)
    dtPreIRR[int(x)]=float(y)
    dt_IRR9K_ByProd.GetPoint(point,x,y)
    dtPostIRR[int(x)]=float(y)
print dtPreIRR
print dtPostIRR

#==============================================================================

crystalsData = R.TTree("crystalsData","crystalsData")
crystalsData.ReadFile("arraysDB_Casaccia_Nov2019.csv","key/C:prod/C:type/C:ID/I:geo/C:tag/C:temp/F:bar/I:posX/F:posY/F:ly/F:ctr/F:lyRef/F:ctrRef/F")

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
                             , 'sigmatPreIRR': mt.sqrt(crys.ctr**2-pixelRes**2), 'sigmatNormPreIRR': mt.sqrt(crys.ctr**2-pixelRes**2)/mt.sqrt(crys.ctrRef**2-pixelRes**2)}
        
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
    myDose = dose[doseTag]
    #print doseTag, myDose
    data[prod].append({'barID':barID,'dose':myDose
                       ,'lyPreIRR':lyPreIRR,'lyNormPreIRR':lyNormPreIRR,'sigmatPreIRR':sigmatPreIRR,'sigmatNormPreIRR':sigmatNormPreIRR
                       ,'lyPostIRR':lyPostIRR,'lyNormPostIRR':lyNormPostIRR,'sigmatPostIRR':sigmatPostIRR,'sigmatNormPostIRR':sigmatNormPostIRR})

#print data

###########
#Make plots
###########

#Create graphs
graphs=['lyPreIRR','lyNormPreIRR','sigmatPreIRR','sigmatNormPreIRR'
        ,'lyPostIRR','lyNormPostIRR','sigmatPostIRR','sigmatNormPostIRR'
        ,'lyRatioIRR','lyNormRatioIRR','sigmatRatioIRR','sigmatNormRatioIRR']
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
              ,'sigmatNormVsLONormOverDtPreIRR','sigmatNormVsLONormOverDtPostIRR']
for g in scatterPlots:
    histos[g]=R.TGraphErrors(len(producers)) 
    histos[g].SetName(g)
    histos[g].SetTitle(g)
    histos[g].SetMarkerSize(1.4)

#Loop over producers
for iprod,prod in enumerate(producers): 

    print("#### %s ####"%prod)
    prodN = float(prod.strip('prod'))

    #create arrays with measurements to be averaged

    #Pre
    lyPreIRR=array('d')    
    lyNormPreIRR=array('d')    
    sigmatPreIRR=array('d')    
    sigmatNormPreIRR=array('d')    

    #Post
    lyPostIRR=array('d')    
    lyNormPostIRR=array('d')    
    sigmatPostIRR=array('d')    
    sigmatNormPostIRR=array('d')    

    #Post/Pre
    lyRatioIRR=array('d')    
    lyNormRatioIRR=array('d')    
    sigmatRatioIRR=array('d')    
    sigmatNormRatioIRR=array('d')    

    for i,meas in enumerate(data[prod]):

        #Pre
        lyPreIRR.append(meas['lyPreIRR'])
        lyNormPreIRR.append(meas['lyNormPreIRR'])
        sigmatPreIRR.append(meas['sigmatPreIRR'])
        sigmatNormPreIRR.append(meas['sigmatNormPreIRR'])

        #Post
        lyPostIRR.append(meas['lyPostIRR'])
        lyNormPostIRR.append(meas['lyNormPostIRR'])
        sigmatPostIRR.append(meas['sigmatPostIRR'])
        sigmatNormPostIRR.append(meas['sigmatNormPostIRR'])

        #Post/Pre
        lyRatioIRR.append(meas['lyPostIRR']/meas['lyPreIRR'])
        lyNormRatioIRR.append(meas['lyNormPostIRR']/meas['lyNormPreIRR'])
        sigmatRatioIRR.append(meas['sigmatPostIRR']/meas['sigmatPreIRR'])
        sigmatNormRatioIRR.append(meas['sigmatNormPostIRR']/meas['sigmatNormPreIRR'])

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

    mean_lyNormOverDtPreIRR = ( mean_lyNormPreIRR / (dtPreIRR[int(prodN)]/dtPreIRR[1]) ) 
    std_lyNormOverDtPreIRR = 0.
    print "PRE: prodN, meanlyNorm, dt, dtref, dtratio, mean/dt: ", int(prodN), mean_lyNormPreIRR, dtPreIRR[int(prodN)], dtPreIRR[1], dtPreIRR[int(prodN)]/dtPreIRR[1], mean_lyNormOverDtPreIRR

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

    mean_lyNormOverDtPostIRR = ( mean_lyNormPostIRR / (dtPostIRR[int(prodN)]/dtPostIRR[1]) ) 
    std_lyNormOverDtPostIRR = 0.
    print "POST: prodN, meanlyNorm, dt, dtref, dtratio, mean/dt: ", int(prodN), mean_lyNormPostIRR, dtPostIRR[int(prodN)], dtPostIRR[1], dtPostIRR[int(prodN)]/dtPostIRR[1], mean_lyNormOverDtPostIRR

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

    #Pre
    print lyPreIRR_np, mean_lyPreIRR, std_lyPreIRR
    print lyNormPreIRR_np, mean_lyNormPreIRR, std_lyNormPreIRR
    print sigmatPreIRR_np, mean_sigmatPreIRR, std_sigmatPreIRR
    print sigmatNormPreIRR_np, mean_sigmatNormPreIRR, std_sigmatNormPreIRR

    histos['lyPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyPreIRR)
    histos['lyPreIRR'+'VsProd'].SetPointError(iprod,0.,std_lyPreIRR)

    histos['lyNormPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormPreIRR)
    histos['lyNormPreIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormPreIRR)

    histos['sigmatPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatPreIRR)
    histos['sigmatPreIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatPreIRR)

    histos['sigmatNormPreIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormPreIRR)
    histos['sigmatNormPreIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormPreIRR)

    histos['sigmatNormVsLONormPreIRR'].SetPoint(iprod,mean_lyNormPreIRR,mean_sigmatNormPreIRR)
    histos['sigmatNormVsLONormPreIRR'].SetPointError(iprod,std_lyNormPreIRR,std_sigmatNormPreIRR)

    histos['sigmatNormVsLONormOverDtPreIRR'].SetPoint(iprod,mean_lyNormOverDtPreIRR,mean_sigmatNormPreIRR)
    histos['sigmatNormVsLONormOverDtPreIRR'].SetPointError(iprod,std_lyNormOverDtPreIRR,std_sigmatNormPreIRR)

    #Post
    print lyPostIRR_np, mean_lyPostIRR, std_lyPostIRR
    print lyNormPostIRR_np, mean_lyNormPostIRR, std_lyNormPostIRR
    print sigmatPostIRR_np, mean_sigmatPostIRR, std_sigmatPostIRR
    print sigmatNormPostIRR_np, mean_sigmatNormPostIRR, std_sigmatNormPostIRR

    histos['lyPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyPostIRR)
    histos['lyPostIRR'+'VsProd'].SetPointError(iprod,0.,std_lyPostIRR)

    histos['lyNormPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormPostIRR)
    histos['lyNormPostIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormPostIRR)

    histos['sigmatPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatPostIRR)
    histos['sigmatPostIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatPostIRR)

    histos['sigmatNormPostIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormPostIRR)
    histos['sigmatNormPostIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormPostIRR)

    histos['sigmatNormVsLONormPostIRR'].SetPoint(iprod,mean_lyNormPostIRR,mean_sigmatNormPostIRR)
    histos['sigmatNormVsLONormPostIRR'].SetPointError(iprod,std_lyNormPostIRR,std_sigmatNormPostIRR)

    histos['sigmatNormVsLONormOverDtPostIRR'].SetPoint(iprod,mean_lyNormOverDtPostIRR,mean_sigmatNormPostIRR)
    histos['sigmatNormVsLONormOverDtPostIRR'].SetPointError(iprod,std_lyNormOverDtPostIRR,std_sigmatNormPostIRR)

    #Post/Pre
    print lyRatioIRR_np, mean_lyRatioIRR, std_lyRatioIRR
    print lyNormRatioIRR_np, mean_lyNormRatioIRR, std_lyNormRatioIRR
    print sigmatRatioIRR_np, mean_sigmatRatioIRR, std_sigmatRatioIRR
    print sigmatNormRatioIRR_np, mean_sigmatNormRatioIRR, std_sigmatNormRatioIRR

    histos['lyRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyRatioIRR)
    histos['lyRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_lyRatioIRR)

    histos['lyNormRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_lyNormRatioIRR)
    histos['lyNormRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_lyNormRatioIRR)

    histos['sigmatRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatRatioIRR)
    histos['sigmatRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatRatioIRR)

    histos['sigmatNormRatioIRR'+'VsProd'].SetPoint(iprod,prodN,mean_sigmatNormRatioIRR)
    histos['sigmatNormRatioIRR'+'VsProd'].SetPointError(iprod,0.,std_sigmatNormRatioIRR)

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
histos['sigmatNormVsLONormOverDtPreIRR'].GetXaxis().SetTitle("(LO/LO_{ref})/(#tau_{decay}/#tau_{ref}) ")
histos['sigmatNormVsLONormOverDtPreIRR'].GetYaxis().SetTitle("#sigma_{t}/#sigma_{t,ref}")
histos['sigmatNormVsLONormOverDtPreIRR'].Draw("ap")
histos['sigmatNormVsLONormOverDtPostIRR'].Draw("p")
legend2.Clear()
legend2.AddEntry(histos['sigmatNormVsLONormOverDtPreIRR'],"No Irrad.","pe")
legend2.AddEntry(histos['sigmatNormVsLONormOverDtPostIRR'],"Irrad. 45-50 kGy","pe")
legend2.Draw()
text2.DrawLatexNDC(0.11,0.93,"CMS Rome - TOFPET+SiPM Bench")
for ext in ['.pdf','.png']:
    c2.SaveAs(outputdir+"/"+'sigmatNormVsLONormOverDt'+ext)

##################################################################

out=R.TFile(outputdir+"/"+"lyArrayIrradPlots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()
    



