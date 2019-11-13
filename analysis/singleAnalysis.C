#define singleAnalysis_cxx
#include "singleAnalysis.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>

#include <TH1F.h>
#include <vector>

#include <iostream>

void singleAnalysis::LoadPedestals(TString pedestalFile)
{
  TFile* f=new TFile(pedestalFile);
  f->ls();
  pedMean = (TH1F*) f->Get("h1_pedTotMean");
  pedRms = (TH1F*) f->Get("h1_pedTotRms");
  
  if (!pedMean or !pedRms)
    std::cout << "Pedestal histograms not found in " << pedestalFile << std::endl;

  // return;
}

void singleAnalysis::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L singleAnalysis.C
//      Root > singleAnalysis t
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

  // pixelChId = 59;
  // myPedestals.pedMean[std::make_pair< int, int>(59,0)]=250;
  // myPedestals.pedMean[std::make_pair< int, int>(59,1)]=250;
  // myPedestals.pedMean[std::make_pair< int, int>(59,2)]=250;
  // myPedestals.pedMean[std::make_pair< int, int>(59,3)]=250;

  std::vector<TObject*> objectsToStore;
  TH1F* h1_energy_pixel = new TH1F("h1_energy_pixel", "", 200, 0, 200);
  objectsToStore.push_back(h1_energy_pixel);
  TH1F* h1_temp_pixel = new TH1F("h1_temp_pixel", "", 1000, 15, 50);
  objectsToStore.push_back(h1_temp_pixel);
  TH1F* h1_temp_bar = new TH1F("h1_temp_bar", "", 1000, 15, 50);
  objectsToStore.push_back(h1_temp_bar);
  TH1F* h1_temp_int = new TH1F("h1_temp_int", "", 1000, 15, 50);
  objectsToStore.push_back(h1_temp_int);

   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
     if (jentry % 100000 == 0) 
       std::cout << "Processing event " << jentry << std::endl;

      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;

      if( channelID != pixelChId )
	continue;

      h1_energy_pixel->Fill(energy-pedMean->GetBinContent(channelID*4+tacID+1));
      h1_temp_pixel->Fill(tempSiPMRef);
      h1_temp_bar->Fill(tempSiPMTest);
      h1_temp_int->Fill(tempInt);
   }

   TFile *fOut=new TFile(outputFile,"RECREATE");
   fOut->cd();

   for ( auto &obj : objectsToStore)
     obj->Write();
   // fOut->Write();
   fOut->ls();
   fOut->Close();
}
