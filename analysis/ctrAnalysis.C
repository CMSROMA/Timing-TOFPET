#define ctrAnalysis_cxx
#include "ctrAnalysis.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>

#define N_BARS 16

void ctrAnalysis::LoadPedestals(TString pedestalFile)
{
  TFile* f=new TFile(pedestalFile);
  f->ls();
  pedMean = (TH1F*) f->Get("h1_pedTotMean");
  pedRms = (TH1F*) f->Get("h1_pedTotRms");
  
  if (!pedMean or !pedRms)
    std::cout << "Pedestal histograms not found in " << pedestalFile << std::endl;

  // return;
}

void ctrAnalysis::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L ctrAnalysis.C
//      Root > ctrAnalysis t
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

   channels[0]=59;
   channels[1]=282;
   channels[2]=272;
   channels[3]=270;
   channels[4]=262;
   channels[5]=267;
   channels[6]=257;
   channels[7]=265;
   channels[8]=260;
   channels[9]=286;
   channels[10]=285;
   channels[11]=271;
   channels[12]=279;
   channels[13]=273;
   channels[14]=284;
   channels[15]=274;
   channels[16]=281;
   channels[17]=307;
   channels[18]=289;
   channels[19]=300;
   channels[20]=290;
   channels[21]=292;
   channels[22]=304;
   channels[23]=302;
   channels[24]=310;
   channels[25]=317;
   channels[26]=319;
   channels[27]=318;
   channels[28]=316;
   channels[29]=295;
   channels[30]=297;
   channels[31]=301;
   channels[32]=311;   
   
  std::vector<TObject*> objectsToStore;
  TH1F* h1_CTR = new TH1F("h1_CTR", "", 800, -10000, 10000);
  objectsToStore.push_back(h1_CTR);
  TH1F* h1_nhits_Xtalk = new TH1F("h1_nhits_Xtalk", "", 8, 0, 8);
  objectsToStore.push_back(h1_nhits_Xtalk);
  TH1F* h1_nbars_Xtalk = new TH1F("h1_nbars_Xtalk", "", 17, 0, 17);
  objectsToStore.push_back(h1_nbars_Xtalk);
  TH2F* h2_nbars_vs_nhits_Xtalk = new TH2F("h2_nbars_vs_nhits_Xtalk", "", 8, 0, 8, 17, 0, 17);
  objectsToStore.push_back(h2_nbars_vs_nhits_Xtalk);
  TH1F* h1_energySum_Xtalk = new TH1F("h1_energySum_Xtalk", "", 220, -20, 200);
  objectsToStore.push_back(h1_energySum_Xtalk);
  TH2F* h2_energySum_vs_energyBar_Xtalk = new TH2F("h2_energySum_vs_energyBar_Xtalk", "", 220, -20, 200, 220, -20, 200);
  objectsToStore.push_back(h2_energySum_vs_energyBar_Xtalk);

  TH1F* h1_energyTot_bar_Xtalk[N_BARS];
  TH1F* h1_energy1_bar_Xtalk[N_BARS];
  TH1F* h1_energy2_bar_Xtalk[N_BARS];

  for (int ibar=0;ibar<16;++ibar)
    {
      h1_energyTot_bar_Xtalk[ibar]= new TH1F(Form("h1_energyTot_bar_Xtalk%d",ibar), "", 220, -20, 200);
      objectsToStore.push_back(h1_energyTot_bar_Xtalk[ibar]);
      h1_energy1_bar_Xtalk[ibar]= new TH1F(Form("h1_energy1_bar_Xtalk%d",ibar), "", 220, -20, 200);
      objectsToStore.push_back(h1_energy1_bar_Xtalk[ibar]);
      h1_energy2_bar_Xtalk[ibar]= new TH1F(Form("h1_energy2_bar_Xtalk%d",ibar), "", 220, -20, 200);
      objectsToStore.push_back(h1_energy2_bar_Xtalk[ibar]);
    }

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      if (jentry % 100000 == 0) 
       std::cout << "Processing event " << jentry << std::endl;

      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;

      if( energy[alignedBar+1]==-9. || energy[alignedBar+17]==-9. )
	continue;

      float energy1 = energy[alignedBar+1]-pedMean->GetBinContent(channels[alignedBar+1]*4+tacID[alignedBar+1]+1);
      float energy2 = energy[alignedBar+17]-pedMean->GetBinContent(channels[alignedBar+17]*4+tacID[alignedBar+17]+1);
      float energyBar =  energy1 + energy2;

      double timeBar = (time[alignedBar+1]+time[alignedBar+17])/2.;
      
      if (energy[0]>-9.)
	{
	  float energyPixel = energy[0]-pedMean->GetBinContent(channels[0]*4+tacID[0]+1);
	  double timePixel = time[0];
	  double deltaT = timeBar - timePixel;
	  

	  ///CTR
	  float NsigmaCut = 1;
	  if( (fabs(energyPixel-pixel_511Peak_mean)/pixel_511Peak_sigma)<NsigmaCut
              &&  (fabs(energyBar - alignedBar_511Peak_mean)/alignedBar_511Peak_sigma)<NsigmaCut)
	    { 
	      h1_CTR->Fill(deltaT);  
	    }

	  //Cross-talk
	  NsigmaCut = 2;
	  int nhits_xtalk = 0;
	  int nbars_xtalk = 0;
	  float energySum_xtalk = 0.;
	  if( (fabs(energyPixel-pixel_511Peak_mean)/pixel_511Peak_sigma)<NsigmaCut
               &&  (fabs(energyBar - alignedBar_511Peak_mean)/alignedBar_511Peak_sigma)<NsigmaCut)
	     {      
	      for (int ibar=alignedBar-1;ibar<alignedBar+2;++ibar)
		{
		  if (ibar<0 || ibar>15)
		    continue; //edges

		  if (ibar==alignedBar)
                    continue;

		  float energy1_xtalk=0;
		  float energy2_xtalk=0;

		  if( energy[ibar+1]==-9. && energy[ibar+17]==-9. )
		    continue;

		  nbars_xtalk++;

		  if( energy[ibar+1]>-9. )
		    {
		      energy1_xtalk = energy[ibar+1]-pedMean->GetBinContent(channels[ibar+1]*4+tacID[ibar+1]+1);
		      h1_energy1_bar_Xtalk[ibar]->Fill(energy1_xtalk);
		      ++nhits_xtalk;
		    }

		  if( energy[ibar+17]>-9. )
		    {
		      energy2_xtalk = energy[ibar+17]-pedMean->GetBinContent(channels[ibar+17]*4+tacID[ibar+17]+1);
		      h1_energy2_bar_Xtalk[ibar]->Fill(energy2_xtalk); 
		      ++nhits_xtalk;
		    }
		  
		  float energyBar_xtalk =  energy1_xtalk + energy2_xtalk;
		  energySum_xtalk += energyBar_xtalk;
		  h1_energyTot_bar_Xtalk[ibar]->Fill(energyBar_xtalk);

		}                

	      h1_nhits_Xtalk->Fill(nhits_xtalk);           
	      h1_nbars_Xtalk->Fill(nbars_xtalk);           
	      h2_nbars_vs_nhits_Xtalk->Fill(nhits_xtalk,nbars_xtalk);

	      if(nhits_xtalk>0)
		{
		  h1_energySum_Xtalk->Fill(energySum_xtalk);
		  h2_energySum_vs_energyBar_Xtalk->Fill(energySum_xtalk,energyBar);
		}
	     } //cut for xtalk
	}
   }

   TFile *fOut=new TFile(outputFile,"UPDATE");
   fOut->cd();

   for ( auto &obj : objectsToStore)
     obj->Write();
   // fOut->Write();
   fOut->ls();
   fOut->Close();

}
