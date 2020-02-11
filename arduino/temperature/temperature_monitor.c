#include <time.h>
#include <stdio.h>
#include <cmath>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>

#include "TChain.h"
#include <TStyle.h>
#include "TBranch.h"
#include "TBrowser.h"
#include "TChainElement.h"
#include "TClass.h"
#include "TCut.h"
#include "TError.h"
#include "TMath.h"
#include "TFile.h"
//#include "TFileInfo.h"
#include "TFriendElement.h"
#include "TLeaf.h"
//#include "TList.h"
#include "TObjString.h"
#include "TPluginManager.h"
//#include "TROOT.h"
#include "TRegexp.h"
#include "TSelector.h"
#include "TSystem.h"
#include "TTree.h"
#include "TTreeCache.h"
#include "TUrl.h"
#include "TVirtualIndex.h"
#include "TEventList.h"
#include "TEntryList.h"
#include "TEntryListFromFile.h"
#include "TFileStager.h"
#include "TProfile.h"
#include"TLegend.h"
#include"TCanvas.h"
#include"TVector.h"

#include<vector>
#include "TF1.h"
#include "TH2F.h"
#include"TImage.h"
#include"TGraphErrors.h"
#include"TMultiGraph.h"
#include"TPaveText.h"

using namespace std;

////legge file misure////


void temperature_monitor()

{
   string input;
   cout<<"enter 1 for temperature_tmp.txt or 2 temperature_all.txt"<<endl;
    cin  >> input;
    
    
   
    
    
    
   FILE *file_temp;
    if (input=="1"){
        file_temp=fopen("temperature_tmp.txt","r");}
    
    if(input=="2"){
    file_temp=fopen("temperature_all.txt","r");}
    
    
 
   
  
  
    
    char line[1000];
    float temp1,temp2,temp3,temp4,temp5,temp6;
    int64_t unixtime;
    
    TTree *tree = new TTree("data_temp","data_temp");
    tree->Branch("unixtime", &unixtime, "unixtime/L");
    tree->Branch("temp1", &temp1, "temp1/F");
    tree->Branch("temp2", &temp2, "temp2/F");
    tree->Branch("temp3", &temp3, "temp3/F");
    tree->Branch("temp4", &temp4, "temp4/F");
    tree->Branch("temp5", &temp5, "temp5/F");
    tree->Branch("temp6", &temp6, "temp6/F");
    

        
    
      
      
  while (fgets(line, sizeof(line), file_temp) != NULL)
    {
            fgets(line,sizeof(line),file_temp);
        //cout<<line<<endl;
       
          
           // event_timestamp=float(timestamp-1531734538);
            //std::cout << event_timestamp << std::endl;
            
           stringstream ss;
            ss << line;
                int64_t mytime(0.0);
            float myfloat(0.0);
        
        
             ss >> mytime; // legge temp 1
             unixtime=mytime;
                
                ss >> myfloat; // legge temp 1
                temp1=myfloat;
            
                ss >> myfloat; //legge temp2
                temp2=myfloat;
        
                ss >> myfloat; //legge temp3
                temp3=myfloat;
                
                ss >> myfloat; //legge temp4
                temp4=myfloat;
        
                ss >> myfloat; //legge temp5
                temp5=myfloat;
        
                ss >> myfloat; //legge temp6
                temp6=myfloat;
            tree->Fill();
      
        
        
               
     }
       
    


   
   Int_t nentries = (Int_t)tree->GetEntries();
    
   
    TCanvas *c1 = new TCanvas("Temperature Vs Time", "temperature Vs time" , 1400,1000);
    c1->Divide(3,2);
    c1->cd(1);
    gPad->SetTickx(2);
    gPad->SetTicky(2);
    gPad->SetGrid();
    gStyle->SetOptStat(1111);
    tree->Draw("temp1-0.75:unixtime");
     TGraph *gr1 = new TGraph(nentries,tree->GetV2(),tree->GetV1());
    gr1->GetYaxis()->SetRangeUser(20,35);
    gr1->SetTitle("");
    //gr1->SetTitle("BOARD PIX");
    gr1->SetMarkerStyle(21);
    gr1->SetMarkerColor(2);
    gr1->Draw("ap");
    
     c1->cd(2);
    gPad->SetTickx(2);
    gPad->SetTicky(2);
    gPad->SetGrid();
    tree->Draw("temp2+0.16:unixtime");
    TGraph *gr2 = new TGraph(nentries,tree->GetV2(),tree->GetV1());
    gr2->SetTitle("INTERNAL on-air");
    gr2->GetYaxis()->SetRangeUser(20,30);
    gr2->GetXaxis()->SetTimeDisplay(1);
    gr2->GetXaxis()->SetNdivisions(-503);
    gr2->GetXaxis()->SetTimeFormat("%Y/%m/%d %H:%M %F 1970-01-01 00:00:00");
    gr2->SetMarkerStyle(21);
    gr2->SetMarkerColor(3);
    gr2->Draw("ap same");
    
    c1->cd(3);
    gPad->SetTickx(2);
    gPad->SetTicky(2);
    gPad->SetGrid();
    tree->Draw("temp3-0.03:unixtime");
    TGraph *gr3 = new TGraph(nentries,tree->GetV2(),tree->GetV1());
    gr3->GetXaxis()->SetTimeDisplay(1);
    gr3->GetXaxis()->SetNdivisions(-503);
    gr3->GetXaxis()->SetTimeFormat("%Y/%m/%d %H:%M %F 1970-01-01 00:00:00");
    gr3->GetYaxis()->SetRangeUser(20,30);
    gr3->SetTitle("External on-air");
    gr3->SetMarkerStyle(21);
    gr3->SetMarkerColor(4);
    gr3->Draw("ap same");
    
    c1->cd(4);
    gPad->SetTickx(2);
    gPad->SetTicky(2);
    gPad->SetGrid();
    tree->Draw("temp4-0.88:unixtime");
    TGraph *gr4 = new TGraph(nentries,tree->GetV2(),tree->GetV1());
    gr4->GetYaxis()->SetRangeUser(20,30);
    gr4->GetXaxis()->SetTimeDisplay(1);
    gr4->GetXaxis()->SetNdivisions(-503);
    gr4->GetXaxis()->SetTimeFormat("%Y/%m/%d %H:%M %F 1970-01-01 00:00:00");
    gr4->SetTitle("BOARD TEST");
    gr4->SetMarkerStyle(21);
    gr4->SetMarkerColor(6);
    gr4->Draw("ap same");
    
    c1->cd(5);
    gPad->SetTickx(2);
    gPad->SetTicky(2);
    gPad->SetGrid();
    tree->Draw("temp5+0.22:unixtime");
    TGraph *gr5 = new TGraph(nentries,tree->GetV2(),tree->GetV1());
    gr5->GetYaxis()->SetRangeUser(20,30);
    gr5->GetXaxis()->SetTimeDisplay(1);
    gr5->GetXaxis()->SetNdivisions(-503);
    gr5->GetXaxis()->SetTimeFormat("%Y/%m/%d %H:%M %F 1970-01-01 00:00:00");
    gr5->SetTitle("SIPM PIX on-air");
    gr5->SetMarkerStyle(21);
    gr5->SetMarkerColor(7);
    gr5->Draw("ap same");
    
    
    c1->cd(6);
    gPad->SetTickx(2);
    gPad->SetTicky(2);
    gPad->SetGrid();
    tree->Draw("temp6+0.09:unixtime");
    TGraph *gr6 = new TGraph(nentries,tree->GetV2(),tree->GetV1());
    gr6->GetXaxis()->SetTimeDisplay(1);
    gr6->GetXaxis()->SetNdivisions(-503);
    gr6->GetXaxis()->SetTimeFormat("%Y/%m/%d %H:%M %F 1970-01-01 00:00:00");
    gr6->GetYaxis()->SetRangeUser(20,30);
    gr6->SetTitle("SIPM TEST on-air");
    gr6->SetMarkerStyle(21);
    gr6->SetMarkerColor(9);
    gr6->Draw("ap same");
    
    
    
    
    
    TCanvas *c2 = new TCanvas("summary", "summary" , 900, 600);
    c2->cd();
    gPad->SetTickx(2);
    gPad->SetTicky(2);
    gPad->SetGrid();
    gr1->GetYaxis()->SetRangeUser(20,35);
    gr1->GetYaxis()->SetTitle("T(°C)");
    gr1->GetXaxis()->SetTitle("Time");
    gr1->SetMarkerStyle(21);
    gr1->SetMarkerColor(2);
    gr1->GetXaxis()->SetTimeDisplay(1);
    gr1->GetXaxis()->SetNdivisions(-503);
    gr1->GetXaxis()->SetTimeFormat("%Y/%m/%d %H:%M %F 1970-01-01 00:00:00");
    gr1->Draw();
    gr2->SetMarkerStyle(21);
    gr2->SetMarkerColor(3);
    gr2->GetYaxis()->SetTitle("T(°C)");
    gr2->GetXaxis()->SetTitle("Time");
    gr2->Draw("p same");
    gr3->SetMarkerStyle(21);
    gr3->SetMarkerColor(4);
    gr3->GetYaxis()->SetTitle("T(°C)");
    gr3->GetXaxis()->SetTitle("Time");
    gr3->Draw("p same");
    gr4->SetMarkerStyle(21);
    gr4->SetMarkerColor(6);
    gr4->GetYaxis()->SetTitle("T(°C)");
    gr4->GetXaxis()->SetTitle("Time");
    gr4->Draw("p same");
    gr5->SetMarkerStyle(21);
    gr5->SetMarkerColor(7);
    gr5->GetYaxis()->SetTitle("T(°C)");
    gr5->GetXaxis()->SetTitle("Time");
    gr5->Draw("p same");
    gr6->SetMarkerStyle(21);
    gr6->SetMarkerColor(9);
    gr6->GetYaxis()->SetTitle("T(°C)");
    gr6->GetXaxis()->SetTitle("Time");
    gr6->Draw("p same");
    TLegend *leg = new TLegend(0.75,1,1,0.70);
    
    //leg->AddEntry(spectrum,"#175-REF prod #1");
    leg->AddEntry(gr1,"BOARD PIX");
    leg->AddEntry(gr2,"INTERNAL (on-air)");
    leg->AddEntry(gr3,"EXTERNAL (on-air)");
    leg->AddEntry(gr4,"BOARD TEST");
    leg->AddEntry(gr5,"SiPM PIX (on-air)");
    leg->AddEntry(gr6,"SiPM TEST on-air");
    leg->Draw();
    
    
    }

