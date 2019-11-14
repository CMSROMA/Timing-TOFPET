#define coincidenceAnalysisBar_cxx
#include "coincidenceAnalysisBar.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>

void coincidenceAnalysisBar::LoadPedestals(TString pedestalFile)
{
  TFile* f=new TFile(pedestalFile);
  f->ls();
  pedMean = (TH1F*) f->Get("h1_pedTotMean");
  pedRms = (TH1F*) f->Get("h1_pedTotRms");
  
  if (!pedMean or !pedRms)
    std::cout << "Pedestal histograms not found in " << pedestalFile << std::endl;

  // return;
}

void coincidenceAnalysisBar::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L coincidenceAnalysisBar.C
//      Root > coincidenceAnalysisBar t
//      Root > t.GetEntry(12); // Fill t data members with entry number 12
//      Root > t.Show();       // Show values of entry 12
//      Root > t.Show(16);     // Read and show values of entry 16
//      Root > t.Loop();       // Loop on all entries
//

//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch

  channels[0]=59;
  channels[1]=315;
  channels[2]=291;

  TH1F* h1_energyTot_bar;
  TH1F* h1_energy1_bar;
  TH1F* h1_energy2_bar;
  TH1F* h1_energyDiff_bar;
  TH2F* h2_energy1VSenergy2_bar;
  TH1F* h1_energyTot_bar_coinc;
  TH1F* h1_energy1_bar_coinc;
  TH1F* h1_energy2_bar_coinc;
  TH1F* h1_energyDiff_bar_coinc;
  TH2F* h2_energy1VSenergy2_bar_coinc;
  TH1F* h1_energy_pixel_coinc;
  TH2F* h2_energyPixelVSenergyBar_coinc;

  std::vector<TObject*> objectsToStore;
  h1_energyTot_bar=new TH1F(Form("h1_energyTot_bar"), "", 250, 0, 250);
  objectsToStore.push_back(h1_energyTot_bar); 
  h1_energy1_bar=new TH1F(Form("h1_energy1_bar"), "", 250, 0, 250);
  objectsToStore.push_back(h1_energy1_bar); 
  h1_energy2_bar=new TH1F(Form("h1_energy2_bar"), "", 250, 0, 250);
  objectsToStore.push_back(h1_energy2_bar); 
  h1_energyDiff_bar=new TH1F(Form("h1_energyDiff_bar"), "", 100, -50, 50);
  objectsToStore.push_back(h1_energyDiff_bar); 
  h2_energy1VSenergy2_bar=new TH2F(Form("h2_energy1VSenergy2_bar"), "", 250, 0, 250, 250, 0, 250);
  objectsToStore.push_back(h2_energy1VSenergy2_bar); 
  h1_energyTot_bar_coinc=new TH1F(Form("h1_energyTot_bar_coinc"), "", 250, 0, 250);
  objectsToStore.push_back(h1_energyTot_bar_coinc); 
  h1_energy1_bar_coinc=new TH1F(Form("h1_energy1_bar_coinc"), "", 250, 0, 250);
  objectsToStore.push_back(h1_energy1_bar_coinc); 
  h1_energy2_bar_coinc=new TH1F(Form("h1_energy2_bar_coinc"), "", 250, 0, 250);
  objectsToStore.push_back(h1_energy2_bar_coinc); 
  h1_energyDiff_bar_coinc=new TH1F(Form("h1_energyDiff_bar_coinc"), "", 100, -50, 50);
  objectsToStore.push_back(h1_energyDiff_bar_coinc); 
  h1_energy_pixel_coinc=new TH1F(Form("h1_energy_pixel_coinc"), "", 250, 0, 250);
  objectsToStore.push_back(h1_energy_pixel_coinc); 
  h2_energy1VSenergy2_bar_coinc=new TH2F(Form("h2_energy1VSenergy2_bar_coinc"), "", 250, 0, 250, 250, 0, 250);
  objectsToStore.push_back(h2_energy1VSenergy2_bar_coinc); 
  h2_energyPixelVSenergyBar_coinc=new TH2F(Form("h2_energyPixelVSenergyBar_coinc"), "", 250, 0, 250, 250, 0, 250);
  objectsToStore.push_back(h2_energyPixelVSenergyBar_coinc); 
  
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
     if (jentry % 100000 == 0) 
       std::cout << "Processing event " << jentry << std::endl;
     
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;

      float energyPixel = energy[0]-pedMean->GetBinContent(channels[0]*4+tacID[0]+1);

      if( energy[1]==-9. || energy[2]==-9. )
	continue;

      float energy1 = energy[1]-pedMean->GetBinContent(channels[1]*4+tacID[1]+1);
      float energy2 = energy[2]-pedMean->GetBinContent(channels[2]*4+tacID[2]+1);
      float energyBar =  energy1 + energy2;
      h1_energyTot_bar->Fill(energyBar);
      h1_energy1_bar->Fill(energy1);
      h1_energy2_bar->Fill(energy2);
      h1_energyDiff_bar->Fill(energy1-energy2);
      h2_energy1VSenergy2_bar->Fill(energy1,energy2);

      if( energy[0] == -9 )
	continue;

      h1_energyTot_bar_coinc->Fill(energyBar);
      h1_energy1_bar_coinc->Fill(energy1);
      h1_energy2_bar_coinc->Fill(energy2);
      h1_energyDiff_bar_coinc->Fill(energy1-energy2);
      h1_energy_pixel_coinc->Fill(energyPixel);
      h2_energy1VSenergy2_bar_coinc->Fill(energy1,energy2);
      h2_energyPixelVSenergyBar_coinc->Fill(energyBar,energyPixel);
   }
   
   TFile *fOut=new TFile(outputFile,"UPDATE");
   fOut->cd();
   
   for ( auto &obj : objectsToStore)
     obj->Write();
   // fOut->Write();
   fOut->ls();
   fOut->Close();
}
