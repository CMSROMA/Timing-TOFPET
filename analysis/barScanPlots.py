import ROOT as R
R.gROOT.SetBatch(1)

from array import array
import math as mt
import numpy as np

##bar pre irr (test with low stat.)
#label = "BarPreIRR"
#data =[ "/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000655_LastRun000690_BAR000027.root", "/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000583_LastRun000618_BAR000044.root", "/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000619_LastRun000654_BAR000059.root", "/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000691_LastRun000726_BAR000095.root", "/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000727_LastRun000762_BAR000081.root", "/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000799_LastRun000834_BAR000111.root" , "/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000835_LastRun000870_BAR000165.root" ,"/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000871_LastRun000906_BAR000125.root", "/media/cmsdaq/ext/data/LYSOBARS/RESULTS/tree_FirstRun000907_LastRun000942_BAR000150.root"]
#thrValues = [5,10,15,20,25,30,35,40,45,50,55,60]

##---------------------

thrValues = [5,10,15,20,25,30]

##array ref 175
#label = "ArrayRef"
#data =[ "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000022_LastRun000039_BAR001752.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000202_LastRun000219_BAR001752.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000361_LastRun000378_BAR001752.root"]

##array pre irr 
label = "ArrayPreIRR"
data =[ "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000361_LastRun000378_BAR001752.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000253_LastRun000270_BAR001892.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000235_LastRun000252_BAR001862.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000379_LastRun000396_BAR001902.root", "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000397_LastRun000414_BAR001872.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000289_LastRun000306_BAR001852.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000325_LastRun000342_BAR001882.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000307_LastRun000324_BAR001922.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000343_LastRun000360_BAR001912.root" ]

##array post irr
#label = "ArrayPostIRR"
#data = ["/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000040_LastRun000057_BAR001762.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000058_LastRun000075_BAR001822.root", "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000076_LastRun000093_BAR001792.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000094_LastRun000111_BAR001772.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000112_LastRun000129_BAR001802.root", "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000130_LastRun000147_BAR001782.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000148_LastRun000165_BAR001812.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000166_LastRun000183_BAR001832.root" , "/media/cmsdaq/ext/data/LYSOBARSINARRAY/RESULTS/tree_FirstRun000184_LastRun000201_BAR001842.root"]

##---------------------

c1=R.TCanvas("c1","c1",800,800)
    
g_time_vs_th1 = []

gCorr=R.TGraphErrors(len(data))
slopeByProd=R.TGraphErrors(len(data))
timeOffsetByProd=R.TGraphErrors(len(data))

for ip,prod in enumerate(data):
    print ip, prod

    firstRun = int(prod.split("/")[-1].split("_")[1].strip("FirstRun").lstrip("0"))
    print firstRun

    thisFile = R.TFile(prod)
    thisFile.Print()
    thisTree = thisFile.Get("results")

    g_time_vs_th1.append(R.TGraphErrors(thisTree.GetEntries()))
    g_time_vs_th1[ip].SetName('g_time_vs_th1_prod%d'%ip)
    g_time_vs_th1[ip].SetTitle('g_time_vs_th1_pro%d'%ip)

    for idx, thr in enumerate(thisTree):
        t1 = ((thr.runNumber-firstRun)-1)/3
        #print idx, thr.CTR_mean_barCoinc, thrValues[t1]
        g_time_vs_th1[ip].SetPoint(idx,thrValues[t1],thr.CTR_mean_barCoinc)
        g_time_vs_th1[ip].SetPointError(idx,0,thr.err_CTR_mean_barCoinc)

    g_time_vs_th1[ip].SetMarkerStyle(20)
    g_time_vs_th1[ip].SetMarkerColor(R.kBlack+ip)
    g_time_vs_th1[ip].Print()
    if ip==0:
        g_time_vs_th1[ip].Draw("ap")
    else:
        g_time_vs_th1[ip].Draw("psame")

    xL,yL,xR,yR=R.Double(0.),R.Double(0.),R.Double(0.),R.Double(0.)
    g_time_vs_th1[ip].GetPoint(0,xL,yL)
    g_time_vs_th1[ip].GetPoint(5,xR,yR)
    g_time_vs_th1[ip].Fit("pol1","RQ","",xL,xR)
    g_time_vs_th1[ip].GetFunction("pol1").SetLineColor(R.kBlack+ip)

    dVdT=1/g_time_vs_th1[ip].GetFunction("pol1").GetParameter(1)
    eRel_dVdT=g_time_vs_th1[ip].GetFunction("pol1").GetParError(1)/g_time_vs_th1[ip].GetFunction("pol1").GetParameter(1) #rel error on 1/x equal to rel error on x

    gCorr.SetPoint(ip,yL,dVdT)
    gCorr.SetPointError(ip,g_time_vs_th1[ip].GetErrorY(0),dVdT*eRel_dVdT)

    slopeByProd.SetPoint(ip,ip+1,dVdT)
    slopeByProd.SetPointError(ip,0,dVdT*eRel_dVdT)

    timeOffsetByProd.SetPoint(ip,ip+1,yL)
    timeOffsetByProd.SetPointError(ip,0,g_time_vs_th1[ip].GetErrorY(0))
c1.SaveAs("TimeVsAmpl"+"_"+label+".png")

R.gStyle.SetOptFit(111111)

gCorr.Draw("AP*")
gCorr.Fit('pol1',"FEX0")
gCorr.SetName("gcorr")
c1.SaveAs("corr"+"_"+label+".png")

#slopeByProd.Print()
#for i in range(0,len(data)):
#    xP,yP,xT,yT=R.Double(0),R.Double(0),R.Double(0),R.Double(0)
#    slopeByProd.GetPoint(i,xP,yP)
#    timeOffsetByProd.GetPoint(i,xT,yT)
#    yAV=(yP+gCorr.GetFunction("pol1").Eval(yT))/2.
#    slopeByProd.SetPoint(i,i+1,yAV)
#    slopeByProd.SetPointError(i,0,slopeByProd.GetErrorY(i)/R.TMath.Sqrt(2))
#slopeByProd.Print()

slopeByProd.Draw("AP*")
slopeByProd.SetName("slopeByProd")
#slopeByProdr.Fit('pol1',"FEX0")
c1.SaveAs("slopeByProd"+"_"+label+".png")
slopeByProd.SaveAs("slopeByProd"+"_"+label+".root")
