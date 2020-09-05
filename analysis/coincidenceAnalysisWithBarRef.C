#define coincidenceAnalysisWithBarRef_cxx
#include "coincidenceAnalysisWithBarRef.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>

#define N_BARS 16

void coincidenceAnalysisWithBarRef::LoadPedestals(TString pedestalFile)
{
  TFile* f=new TFile(pedestalFile);
  f->ls();
  pedMean = (TH1F*) f->Get("h1_pedTotMean");
  pedRms = (TH1F*) f->Get("h1_pedTotRms");
  
  if (!pedMean or !pedRms)
    std::cout << "Pedestal histograms not found in " << pedestalFile << std::endl;

  // return;
}

void coincidenceAnalysisWithBarRef::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L coincidenceAnalysisWithBarRef.C
//      Root > coincidenceAnalysisWithBarRef t
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
  channels[33]=35;
  //--------------
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

  TH1F* h1_temp_pixel;
  TH1F* h1_temp_bar;
  TH1F* h1_temp_int;

  TH1F* h1_energyTot_barRef;
  TH1F* h1_energy1_barRef;
  TH1F* h1_energy2_barRef;
  TH1F* h1_energyDiff_barRef;
  TH2F* h2_energy1VSenergy2_barRef;

  TH1F* h1_energyTot_bar[N_BARS];
  TH1F* h1_energy1_bar[N_BARS];
  TH1F* h1_energy2_bar[N_BARS];
  TH1F* h1_energyDiff_bar[N_BARS];
  TH2F* h2_energy1VSenergy2_bar[N_BARS];
  TH1F* h1_energyTot_bar_coinc[N_BARS];
  TH1F* h1_energy1_bar_coinc[N_BARS];
  TH1F* h1_energy2_bar_coinc[N_BARS];
  TH1F* h1_energyDiff_bar_coinc[N_BARS];
  TH2F* h2_energy1VSenergy2_bar_coinc[N_BARS];
  TH1F* h1_energy_barRef_coinc[N_BARS];
  TH2F* h2_energyBarRefVSenergyBar_coinc[N_BARS];

  /* // TEST
  TH1F* h1_deltaT12_barRef_coinc[N_BARS];
  TH1F* h1_deltaT12_bar_coinc[N_BARS];
  TH1F* h1_deltaTWithRef_bar_coinc[N_BARS];
  */

  std::vector<TObject*> objectsToStore;

  h1_temp_pixel=new TH1F("h1_temp_pixel", "", 1000, 15, 50);
  objectsToStore.push_back(h1_temp_pixel);
  h1_temp_bar=new TH1F("h1_temp_bar", "", 1000, 15, 50);
  objectsToStore.push_back(h1_temp_bar);
  h1_temp_int=new TH1F("h1_temp_int", "", 1000, 15, 50);
  objectsToStore.push_back(h1_temp_int);

  h1_energyTot_barRef=new TH1F("h1_energyTot_barRef", "", 250, 0, 250);
  objectsToStore.push_back(h1_energyTot_barRef); 
  h1_energy1_barRef=new TH1F("h1_energy1_barRef", "", 200, 0, 200);
  objectsToStore.push_back(h1_energy1_barRef); 
  h1_energy2_barRef=new TH1F("h1_energy2_barRef", "", 200, 0, 200);
  objectsToStore.push_back(h1_energy2_barRef); 
  h1_energyDiff_barRef=new TH1F("h1_energyDiff_barRef", "", 100, -50, 50);
  objectsToStore.push_back(h1_energyDiff_barRef); 
  h2_energy1VSenergy2_barRef=new TH2F("h2_energy1VSenergy2_barRef", "", 200, 0, 200, 200, 0, 200);
  objectsToStore.push_back(h2_energy1VSenergy2_barRef); 

  for (int ibar=0;ibar<16;++ibar)
    {
      h1_energyTot_bar[ibar]=new TH1F(Form("h1_energyTot_bar%d",ibar), "", 200, 0, 200);
      objectsToStore.push_back(h1_energyTot_bar[ibar]); 
      h1_energy1_bar[ibar]=new TH1F(Form("h1_energy1_bar%d",ibar), "", 200, 0, 200);
      objectsToStore.push_back(h1_energy1_bar[ibar]); 
      h1_energy2_bar[ibar]=new TH1F(Form("h1_energy2_bar%d",ibar), "", 200, 0, 200);
      objectsToStore.push_back(h1_energy2_bar[ibar]); 
      h1_energyDiff_bar[ibar]=new TH1F(Form("h1_energyDiff_bar%d",ibar), "", 100, -50, 50);
      objectsToStore.push_back(h1_energyDiff_bar[ibar]); 
      h2_energy1VSenergy2_bar[ibar]=new TH2F(Form("h2_energy1VSenergy2_bar%d",ibar), "", 200, 0, 200, 200, 0, 200);
      objectsToStore.push_back(h2_energy1VSenergy2_bar[ibar]); 
      h1_energyTot_bar_coinc[ibar]=new TH1F(Form("h1_energyTot_bar_coinc%d",ibar), "", 200, 0, 200);
      objectsToStore.push_back(h1_energyTot_bar_coinc[ibar]); 
      h1_energy1_bar_coinc[ibar]=new TH1F(Form("h1_energy1_bar_coinc%d",ibar), "", 200, 0, 200);
      objectsToStore.push_back(h1_energy1_bar_coinc[ibar]); 
      h1_energy2_bar_coinc[ibar]=new TH1F(Form("h1_energy2_bar_coinc%d",ibar), "", 200, 0, 200);
      objectsToStore.push_back(h1_energy2_bar_coinc[ibar]); 
      h1_energyDiff_bar_coinc[ibar]=new TH1F(Form("h1_energyDiff_bar_coinc%d",ibar), "", 100, -50, 50);
      objectsToStore.push_back(h1_energyDiff_bar_coinc[ibar]); 
      h1_energy_barRef_coinc[ibar]=new TH1F(Form("h1_energy_barRef_coinc%d",ibar), "", 250, 0, 250);
      objectsToStore.push_back(h1_energy_barRef_coinc[ibar]); 
      h2_energy1VSenergy2_bar_coinc[ibar]=new TH2F(Form("h2_energy1VSenergy2_bar_coinc%d",ibar), "", 200, 0, 200, 200, 0, 200);
      objectsToStore.push_back(h2_energy1VSenergy2_bar_coinc[ibar]); 
      h2_energyBarRefVSenergyBar_coinc[ibar]=new TH2F(Form("h2_energyBarRefVSenergyBar_coinc%d",ibar), "", 200, 0, 200, 200, 0, 200);
      objectsToStore.push_back(h2_energyBarRefVSenergyBar_coinc[ibar]); 

      /* //TEST
      h1_deltaT12_barRef_coinc[ibar]=new TH1F(Form("h1_deltaT12_barRef_coinc%d",ibar), "", 200, -2000, 2000);
      objectsToStore.push_back(h1_deltaT12_barRef_coinc[ibar]); 
      h1_deltaT12_bar_coinc[ibar]=new TH1F(Form("h1_deltaT12_bar_coinc%d",ibar), "", 200, -2000, 2000);
      objectsToStore.push_back(h1_deltaT12_bar_coinc[ibar]); 
      h1_deltaTWithRef_bar_coinc[ibar]=new TH1F(Form("h1_deltaTWithRef_bar_coinc%d",ibar), "", 200, -2000, 2000);
      objectsToStore.push_back(h1_deltaTWithRef_bar_coinc[ibar]); 
      */

    }

   if (fChain == 0) return;

   //FIXME
   Long64_t nentries = fChain->GetEntriesFast();
   //Long64_t nentries = 2000000;

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
     if (jentry % 100000 == 0) 
       std::cout << "Processing event " << jentry << std::endl;
     
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;

      h1_temp_pixel->Fill(tempSiPMRef);
      h1_temp_bar->Fill(tempSiPMTest);
      h1_temp_int->Fill(tempInt);

      float energyBarRef1 = energy[0]-pedMean->GetBinContent(channels[0]*4+tacID[0]+1);
      float energyBarRef2 = energy[33]-pedMean->GetBinContent(channels[33]*4+tacID[33]+1);
      float energyBarRef = energyBarRef1 + energyBarRef2;

      if( energy[0] != -9 && energy[33] != -9 )
	{	    
	  h1_energyTot_barRef->Fill(energyBarRef);
	  h1_energy1_barRef->Fill(energyBarRef1);
	  h1_energy2_barRef->Fill(energyBarRef2);
	  h1_energyDiff_barRef->Fill(energyBarRef1-energyBarRef2);
	  h2_energy1VSenergy2_barRef->Fill(energyBarRef1,energyBarRef2);
	}

      for (int ibar=0;ibar<16;++ibar)
	{
	  if( energy[ibar+1]==-9. || energy[ibar+17]==-9. )
	    continue;

	  float energy1 = energy[ibar+1]-pedMean->GetBinContent(channels[ibar+1]*4+tacID[ibar+1]+1);
	  float energy2 = energy[ibar+17]-pedMean->GetBinContent(channels[ibar+17]*4+tacID[ibar+17]+1);
	  float energyBar =  energy1 + energy2;

	  h1_energyTot_bar[ibar]->Fill(energyBar);
	  h1_energy1_bar[ibar]->Fill(energy1);
	  h1_energy2_bar[ibar]->Fill(energy2);
	  h1_energyDiff_bar[ibar]->Fill(energy1-energy2);
	  h2_energy1VSenergy2_bar[ibar]->Fill(energy1,energy2);

	  //if( energy[0] == -9 || energy[33] == -9 )
	  //  continue;
	  if (energyBarRef1 < 10. || energyBarRef2 < 10. )
	    continue;

	  h1_energyTot_bar_coinc[ibar]->Fill(energyBar);
	  h1_energy1_bar_coinc[ibar]->Fill(energy1);
	  h1_energy2_bar_coinc[ibar]->Fill(energy2);
	  h1_energyDiff_bar_coinc[ibar]->Fill(energy1-energy2);
	  h1_energy_barRef_coinc[ibar]->Fill(energyBarRef);
	  h2_energy1VSenergy2_bar_coinc[ibar]->Fill(energy1,energy2);
	  h2_energyBarRefVSenergyBar_coinc[ibar]->Fill(energyBar,energyBarRef);

	  /* // TEST
	  if ( 
	      energyBarRef > 80. && energyBarRef < 110. 
	      && energyBar >60. && energyBar < 70.)//bar1
	    //&& energyBar >55. && energyBar < 65.)//bar5
	    {

	      double time1 = time[ibar+1];
	      double time2 = time[ibar+17];
	      double timeAvg =  (time1 + time2) / 2.;

	      h1_deltaT12_bar_coinc[ibar]->Fill(time1-time2);	      

	      double time1Ref = time[0];
	      double time2Ref = time[33];
	      double timeAvgRef =  (time1Ref + time2Ref) / 2.;

	      h1_deltaTWithRef_bar_coinc[ibar]->Fill(timeAvg-timeAvgRef);	      

	      h1_deltaT12_barRef_coinc[ibar]->Fill(time1Ref-time2Ref);	      

	    }
	  */

	}
 }

   TFile *fOut=new TFile(outputFile,"RECREATE");
   fOut->cd();

   for ( auto &obj : objectsToStore)
     obj->Write();
   // fOut->Write();
   fOut->ls();
   fOut->Close();

}
