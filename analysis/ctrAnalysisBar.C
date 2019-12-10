#define ctrAnalysisBar_cxx
#include "ctrAnalysisBar.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>

void ctrAnalysisBar::LoadPedestals(TString pedestalFile)
{
  TFile* f=new TFile(pedestalFile);
  f->ls();
  pedMean = (TH1F*) f->Get("h1_pedTotMean");
  pedRms = (TH1F*) f->Get("h1_pedTotRms");
  
  if (!pedMean or !pedRms)
    std::cout << "Pedestal histograms not found in " << pedestalFile << std::endl;

  // return;
}

void ctrAnalysisBar::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L ctrAnalysisBar.C
//      Root > ctrAnalysisBar t
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
   if (fChain == 0) return;
  
   //channels[0]=59;
   //channels[1]=315;
   //channels[2]=291;
 
   cout << "channels: " << channels[0] << " , " << channels[1] << " , " << channels[2] << endl;

   std::vector<TObject*> objectsToStore;
   TH1F* h1_CTR = new TH1F("h1_CTR", "", 800, -10000, 10000);
   objectsToStore.push_back(h1_CTR);

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      if (jentry % 100000 == 0) 
       std::cout << "Processing event " << jentry << std::endl;

      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;

      if( energy[1]==-9. || energy[2]==-9. )
	continue;

      float energy1 = energy[1]-pedMean->GetBinContent(channels[1]*4+tacID[1]+1);
      float energy2 = energy[2]-pedMean->GetBinContent(channels[2]*4+tacID[2]+1);
      float energyBar =  energy1 + energy2;

      double timeBar = (time[1]+time[2])/2.;
      
      if (energy[0]>-9.)
	{
	  float energyPixel = energy[0]-pedMean->GetBinContent(channels[0]*4+tacID[0]+1);
	  double timePixel = time[0];
	  double deltaT = timeBar - timePixel;

	  ///CTR
	  float NsigmaCut = 1;
	  if( (fabs(energyPixel-pixel_511Peak_mean)/pixel_511Peak_sigma)<NsigmaCut
              &&  (fabs(energyBar - bar_511Peak_mean)/bar_511Peak_sigma)<NsigmaCut)
	    { 
	      h1_CTR->Fill(deltaT);  
	    }
	}
   }

   h1_CTR->Print();

   TFile *fOut=new TFile(outputFile,"UPDATE");
   fOut->cd();

   for ( auto &obj : objectsToStore)
     obj->Write();
   // fOut->Write();
   fOut->ls();
   fOut->Close();

}
