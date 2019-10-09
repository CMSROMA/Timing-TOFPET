import ROOT as R
R.gROOT.SetBatch(1)

crystalsData=R.TTree("crystalsData","crystalsData");
crystalsData.ReadFile("crystalsDataTOFPET.csv","id/C:prod/C:geo/C:ly/F:lyCoinc/F:ctr/F:lyRef/F:lyCoincRef/F:ctrRef/F");

producers = [ 'prod'+str(i) for i in range(1,9) ]
geoms = [ 'geo'+str(i) for i in range(1,4) ]

histos = {}
data = {}
for prod in producers: 
    histos['ly_'+prod]=R.TH1F('ly_'+prod,'ly_'+prod,100,0.,60.)
    histos['lyNorm_'+prod]=R.TH1F('lyNorm_'+prod,'lyNorm_'+prod,400,0.5,1.5)
    histos['lyCoinc_'+prod]=R.TH1F('lyCoinc_'+prod,'lyCoinc_'+prod,100,0.,60.)
    histos['lyCoincNorm_'+prod]=R.TH1F('lyCoincNorm_'+prod,'lyCoincNorm_'+prod,400,0.5,1.5)
    histos['ctr_'+prod]=R.TH1F('ctr_'+prod,'ctr_'+prod,100,0.,220.)
    histos['ctrNorm_'+prod]=R.TH1F('ctrNorm_'+prod,'ctrNorm_'+prod,100,0.,220.)
    for geo in geoms:
        histos['ly_'+prod+'_'+geo]=R.TH1F('ly_'+prod+'_'+geo,'ly_'+prod+'_'+geo,100,0.,60.)
        histos['lyNorm_'+prod+'_'+geo]=R.TH1F('lyNorm_'+prod+'_'+geo,'lyNorm_'+prod+'_'+geo,400,0.5,1.5)
        histos['lyCoinc_'+prod+'_'+geo]=R.TH1F('lyCoinc_'+prod+'_'+geo,'lyCoinc_'+prod+'_'+geo,100,0.,60.)
        histos['lyCoincNorm_'+prod+'_'+geo]=R.TH1F('lyCoincNorm_'+prod+'_'+geo,'lyCoincNorm_'+prod+'_'+geo,400,0.5,1.5)
        histos['ctr_'+prod+'_'+geo]=R.TH1F('ctr_'+prod+'_'+geo,'ctr_'+prod+'_'+geo,100,0.,220.)
        histos['ctrNorm_'+prod+'_'+geo]=R.TH1F('ctrNorm_'+prod+'_'+geo,'ctrNorm_'+prod+'_'+geo,100,0.,220.)
        data[prod+'_'+geo] = []

for crys in crystalsData:
    prod=crys.prod.rstrip('\x00')
    geo=crys.geo.rstrip('\x00')
    if ( crys.ly < 0 or crys.lyCoinc < 0 or crys.ctr < 0 or crys.lyRef < 0 or crys.lyCoincRef < 0 or crys.ctrRef < 0):
        continue
    histos['ly_'+prod].Fill(crys.ly)
    histos['ly_'+prod+'_'+geo].Fill(crys.ly)
    histos['lyNorm_'+prod].Fill(crys.ly/crys.lyRef)
    histos['lyNorm_'+prod+'_'+geo].Fill(crys.ly/crys.lyRef)
    histos['lyCoinc_'+prod].Fill(crys.lyCoinc)
    histos['lyCoinc_'+prod+'_'+geo].Fill(crys.lyCoinc)
    histos['lyCoincNorm_'+prod].Fill(crys.lyCoinc/crys.lyCoincRef)
    histos['lyCoincNorm_'+prod+'_'+geo].Fill(crys.lyCoinc/crys.lyCoincRef)
    histos['ctr_'+prod].Fill(crys.ctr)
    histos['ctr_'+prod+'_'+geo].Fill(crys.ctr)
    histos['ctrNorm_'+prod].Fill(crys.ctr/crys.ctrRef)
    histos['ctrNorm_'+prod+'_'+geo].Fill(crys.ctr/crys.ctrRef)
    data[prod+'_'+geo].append({ 'lyNorm': crys.ly/crys.lyRef, 'lyCoincNorm': crys.lyCoinc/crys.lyCoincRef , 'ctr': crys.ctr })

for prod in producers: 
    for geo in geoms:
        histos['ctrVslyNorm_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['ctrVslyNorm_'+prod+'_'+geo].SetName('ctrVslyNorm_'+prod+'_'+geo)
        for i,bar in enumerate(data[prod+'_'+geo]):
            histos['ctrVslyNorm_'+prod+'_'+geo].SetPoint(i,bar['lyNorm'],bar['ctr'])
        histos['ctrVslyCoincNorm_'+prod+'_'+geo]=R.TGraph(len(data[prod+'_'+geo]))
        histos['ctrVslyCoincNorm_'+prod+'_'+geo].SetName('ctrVslyCoincNorm_'+prod+'_'+geo)
        for i,bar in enumerate(data[prod+'_'+geo]):
            histos['ctrVslyCoincNorm_'+prod+'_'+geo].SetPoint(i,bar['lyCoincNorm'],bar['ctr'])

##

c1=R.TCanvas("c1","c1",800,600)
R.gStyle.SetOptTitle(0)

text=R.TLatex()
text.SetTextSize(0.04)

leg=R.TLegend(0.5,0.6,0.92,0.88)
leg.SetBorderSize(0)
leg.SetFillColor(0)
leg.SetTextSize(0.03)

frame=R.TH2F("frame","frame",100,0.75,1.2,100,110,220)
frame.SetStats(0)
frame.GetXaxis().SetTitle("LO Normalised to REF bar")
frame.GetYaxis().SetTitle("Coincidence Time Resolution, CTR [ps]")
frame.Draw()

leg.Clear()
for igeo,geo in enumerate(geoms):
    frame.Draw()
    for iprod,prod in enumerate(producers): 

        histos['ctrVslyCoincNorm_'+prod+'_'+geo].SetMarkerStyle(20+iprod)
        histos['ctrVslyCoincNorm_'+prod+'_'+geo].SetMarkerColor(R.kBlack+iprod)
        histos['ctrVslyCoincNorm_'+prod+'_'+geo].SetMarkerSize(1.2)
        histos['ctrVslyCoincNorm_'+prod+'_'+geo].Draw("PSAME")

        leg.AddEntry(histos['ctrVslyCoincNorm_'+prod+'_'+geo],"%s - %s - Mean LO:%3.2f, CTR: %3.1f ps"%(prod,geo,histos['ctrVslyCoincNorm_'+prod+'_'+geo].GetMean(1),histos['ctrVslyCoincNorm_'+prod+'_'+geo].GetMean(2)),"P")

    leg.Draw()        
    text.DrawLatexNDC(0.12,0.91,"CMS Rome - TOFPET-SiPM Bench")            
    c1.SaveAs("ctrVslyCoincNorm_ProdDifferentColors_"+geo+".png")
    leg.Clear()

##

c2=R.TCanvas("c2","c2",800,600)

histos['lyCoincRatioGeo21_vs_prod'] = R.TGraph(len(producers))
histos['lyCoincRatioGeo21_vs_prod'].SetName('lyCoincRatioGeo21_vs_prod')
for iprod,prod in enumerate(producers): 
    if histos['ctrVslyCoincNorm_'+prod+'_geo1'].GetMean(1):
        histos['lyCoincRatioGeo21_vs_prod'].SetPoint(iprod,float(prod.split('prod')[1]),histos['ctrVslyCoincNorm_'+prod+'_geo2'].GetMean(1)/histos['ctrVslyCoincNorm_'+prod+'_geo1'].GetMean(1))
        print histos['ctrVslyCoincNorm_'+prod+'_geo2'].GetMean(1), histos['ctrVslyCoincNorm_'+prod+'_geo1'].GetMean(1)
histos['lyCoincRatioGeo21_vs_prod'].GetXaxis().SetTitle("Producer ID")
histos['lyCoincRatioGeo21_vs_prod'].GetYaxis().SetTitle("LO_geo2 / LO_geo1")
histos['lyCoincRatioGeo21_vs_prod'].SetMarkerStyle(20)
histos['lyCoincRatioGeo21_vs_prod'].SetMarkerColor(R.kBlack)
histos['lyCoincRatioGeo21_vs_prod'].SetMarkerSize(1.2)
histos['lyCoincRatioGeo21_vs_prod'].Draw("AP")
text.DrawLatexNDC(0.12,0.91,"CMS Rome - TOFPET-SiPM Bench")            
c2.SaveAs("lyCoincRatioGeo21_vs_prod.png")

histos['lyCoincRatioGeo32_vs_prod'] = R.TGraph(len(producers))
histos['lyCoincRatioGeo32_vs_prod'].SetName('lyCoincRatioGeo32_vs_prod')
for iprod,prod in enumerate(producers):
    if histos['ctrVslyCoincNorm_'+prod+'_geo2'].GetMean(1):
        histos['lyCoincRatioGeo32_vs_prod'].SetPoint(iprod,float(prod.split('prod')[1]),histos['ctrVslyCoincNorm_'+prod+'_geo3'].GetMean(1)/histos['ctrVslyCoincNorm_'+prod+'_geo2'].GetMean(1))
histos['lyCoincRatioGeo32_vs_prod'].GetXaxis().SetTitle("Producer ID")
histos['lyCoincRatioGeo32_vs_prod'].GetYaxis().SetTitle("LO_geo3 / LO_geo2")
histos['lyCoincRatioGeo32_vs_prod'].SetMarkerStyle(20)
histos['lyCoincRatioGeo32_vs_prod'].SetMarkerColor(R.kBlack)
histos['lyCoincRatioGeo32_vs_prod'].SetMarkerSize(1.2)
histos['lyCoincRatioGeo32_vs_prod'].Draw("AP")
text.DrawLatexNDC(0.12,0.91,"CMS Rome - TOFPET-SiPM Bench")            
c2.SaveAs("lyCoincRatioGeo32_vs_prod.png")

out=R.TFile("LYplots.root","RECREATE")
for h,histo in histos.items():
    histo.Write()
crystalsData.Write()
out.Write()
out.Close()
