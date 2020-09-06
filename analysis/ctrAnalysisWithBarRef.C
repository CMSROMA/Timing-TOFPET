#define ctrAnalysisWithBarRef_cxx
#include "ctrAnalysisWithBarRef.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>

#define N_BARS 16

void ctrAnalysisWithBarRef::LoadPedestals(TString pedestalFile)
{
  TFile* f=new TFile(pedestalFile);
  f->ls();
  pedMean = (TH1F*) f->Get("h1_pedTotMean");
  pedRms = (TH1F*) f->Get("h1_pedTotRms");
  
  if (!pedMean or !pedRms)
    std::cout << "Pedestal histograms not found in " << pedestalFile << std::endl;

  // return;
}

void ctrAnalysisWithBarRef::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L ctrAnalysisWithBarRef.C
//      Root > ctrAnalysisWithBarRef t
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

  std::vector<TObject*> objectsToStore;
  
  //time resolution
  TH1F* h1_deltaT12[N_BARS];
  TH1F* h1_CTR[N_BARS];
  TH1F* h1_deltaT12_barRef[N_BARS];

  //xtalk
  TH1F* h1_energy1Left_Xtalk[N_BARS];
  TH1F* h1_energy1Right_Xtalk[N_BARS];
  TH1F* h1_energy2Left_Xtalk[N_BARS];
  TH1F* h1_energy2Right_Xtalk[N_BARS];
  TH1F* h1_energyLeft_Xtalk[N_BARS];
  TH2F* h2_energyLeft_vs_energyBar_Xtalk[N_BARS];
  TH1F* h1_energyRight_Xtalk[N_BARS];
  TH2F* h2_energyRight_vs_energyBar_Xtalk[N_BARS];
  TH1F* h1_nhits_Xtalk[N_BARS];
  TH1F* h1_nbars_Xtalk[N_BARS];
  TH2F* h2_nbars_vs_nhits_Xtalk[N_BARS];
  TH1F* h1_energySum_Xtalk[N_BARS];
  TH2F* h2_energySum_vs_energyBar_Xtalk[N_BARS];

  for (int ibar=0;ibar<16;++ibar)
    {

      //time resolution
      h1_deltaT12[ibar] = new TH1F(Form("h1_deltaT12_bar%d",ibar), "", 400, -10000, 10000);
      objectsToStore.push_back(h1_deltaT12[ibar]);

      h1_CTR[ibar]  = new TH1F(Form("h1_CTR_bar%d",ibar), "", 400, -10000, 10000);
      objectsToStore.push_back(h1_CTR[ibar]);

      h1_deltaT12_barRef[ibar] = new TH1F(Form("h1_deltaT12_barRef_coincBar%d",ibar), "", 400, -10000, 10000);
      objectsToStore.push_back(h1_deltaT12_barRef[ibar]);

      //xtalk
      h1_energy1Left_Xtalk[ibar] = new TH1F(Form("h1_energy1Left_bar%d_Xtalk",ibar), "", 70, -20, 50);
      objectsToStore.push_back(h1_energy1Left_Xtalk[ibar]);

      h1_energy1Right_Xtalk[ibar] = new TH1F(Form("h1_energy1Right_bar%d_Xtalk",ibar), "", 70, -20, 50);
      objectsToStore.push_back(h1_energy1Right_Xtalk[ibar]);

      h1_energy2Left_Xtalk[ibar] = new TH1F(Form("h1_energy2Left_bar%d_Xtalk",ibar), "", 70, -20, 50);
      objectsToStore.push_back(h1_energy2Left_Xtalk[ibar]);

      h1_energy2Right_Xtalk[ibar] = new TH1F(Form("h1_energy2Right_bar%d_Xtalk",ibar), "", 70, -20, 50);
      objectsToStore.push_back(h1_energy2Right_Xtalk[ibar]);

      h1_energyLeft_Xtalk[ibar] = new TH1F(Form("h1_energyLeft_bar%d_Xtalk",ibar), "", 70, -20, 50);
      objectsToStore.push_back(h1_energyLeft_Xtalk[ibar]);

      h2_energyLeft_vs_energyBar_Xtalk[ibar] = new TH2F(Form("h2_energyLeft_vs_energyBar_bar%d_Xtalk",ibar), "", 250, -20, 230, 250, -20, 230);
      objectsToStore.push_back(h2_energyLeft_vs_energyBar_Xtalk[ibar]);

      h1_energyRight_Xtalk[ibar] = new TH1F(Form("h1_energyRight_bar%d_Xtalk",ibar), "", 70, -20, 50);
      objectsToStore.push_back(h1_energyRight_Xtalk[ibar]);

      h2_energyRight_vs_energyBar_Xtalk[ibar] = new TH2F(Form("h2_energyRight_vs_energyBar_bar%d_Xtalk",ibar), "", 250, -20, 230, 250, -20, 230);
      objectsToStore.push_back(h2_energyRight_vs_energyBar_Xtalk[ibar]);

      h1_nhits_Xtalk[ibar] = new TH1F(Form("h1_nhits_bar%d_Xtalk",ibar), "", 8, 0, 8);
      objectsToStore.push_back(h1_nhits_Xtalk[ibar]);

      h1_nbars_Xtalk[ibar] = new TH1F(Form("h1_nbars_bar%d_Xtalk",ibar), "", 4, 0, 4);
      objectsToStore.push_back(h1_nbars_Xtalk[ibar]);

      h2_nbars_vs_nhits_Xtalk[ibar] = new TH2F(Form("h2_nbars_vs_nhits_bar%d_Xtalk",ibar), "", 8, 0, 8, 4, 0, 4);
      objectsToStore.push_back(h2_nbars_vs_nhits_Xtalk[ibar]);

      h1_energySum_Xtalk[ibar] = new TH1F(Form("h1_energySum_bar%d_Xtalk",ibar), "", 70, -20, 50);
      objectsToStore.push_back(h1_energySum_Xtalk[ibar]);

      h2_energySum_vs_energyBar_Xtalk[ibar] = new TH2F(Form("h2_energySum_vs_energyBar_bar%d_Xtalk",ibar), "", 250, -20, 230, 250, -20, 230);
      objectsToStore.push_back(h2_energySum_vs_energyBar_Xtalk[ibar]);
    }

  Long64_t nentries = fChain->GetEntriesFast();
  //Long64_t nentries = 2000000;
  
  Long64_t nbytes = 0, nb = 0;
  for (Long64_t jentry=0; jentry<nentries;jentry++) {

    if (jentry % 100000 == 0) 
      std::cout << "Processing event " << jentry << std::endl;
    
    Long64_t ientry = LoadTree(jentry);
    if (ientry < 0) break;
    nb = fChain->GetEntry(jentry);   nbytes += nb;

    if( energy[0] == -9. || energy[33] == -9. )
      continue;
    
    float energyBarRef1 = energy[0]-pedMean->GetBinContent(channels[0]*4+tacID[0]+1);
    float energyBarRef2 = energy[33]-pedMean->GetBinContent(channels[33]*4+tacID[33]+1);
    float energyBarRef = energyBarRef1 + energyBarRef2;
    
    if (energyBarRef1 < 10. || energyBarRef2 < 10. )
      continue;

    for (int ibar=0;ibar<16;++ibar)
      {

	if (alignedBar_511Peak_mean[ibar]==-9. || alignedBar_511Peak_sigma[ibar]==-9.)
	  continue;

	if( energy[ibar+1]==-9. || energy[ibar+17]==-9. )
	  continue;
	
	float energy1 = energy[ibar+1]-pedMean->GetBinContent(channels[ibar+1]*4+tacID[ibar+1]+1);
	float energy2 = energy[ibar+17]-pedMean->GetBinContent(channels[ibar+17]*4+tacID[ibar+17]+1);
	float energyBar =  energy1 + energy2;

	
	/// === Time resolution ===

	float NsigmaCut = 1;
	//cout << "bar: " << ibar << " mean: " << alignedBar_511Peak_mean[ibar] << " sigma: " << alignedBar_511Peak_sigma[ibar] << endl;
	if( (fabs(energyBarRef-barRef_511Peak_mean)/barRef_511Peak_sigma)<NsigmaCut
	    &&  (fabs(energyBar - alignedBar_511Peak_mean[ibar])/alignedBar_511Peak_sigma[ibar])<NsigmaCut)
	  { 
	    //CTR of bar in array using bar only
	    double time1 = time[ibar+1];
	    double time2 = time[ibar+17];
	    double deltaT12 = time1 - time2; 
	    double timeAvg =  (time1 + time2) / 2.;	      
	    h1_deltaT12[ibar]->Fill(deltaT12);
	    
	    //CTR of bar in array using barRef 
	    double time1Ref = time[0];
	    double time2Ref = time[33];
	    double timeAvgRef =  (time1Ref + time2Ref) / 2.;
	    h1_CTR[ibar]->Fill(timeAvg-timeAvgRef);  
	    
	    //CTR of barRef using barRef only
	    double deltaT12Ref = time1Ref - time2Ref; 	  
	    h1_deltaT12_barRef[ibar]->Fill(deltaT12Ref);

	  }// cut for time resolution


	// === Cross-talk ===

	int nhits_xtalk = 0;
	int nbars_xtalk = 0;
	float energySum_xtalk = 0.;
	if( (fabs(energyBarRef-barRef_511Peak_mean)/barRef_511Peak_sigma)<NsigmaCut)
	  //	    &&  (fabs(energyBar - alignedBar_511Peak_mean[ibar])/alignedBar_511Peak_sigma[ibar])<NsigmaCut)
	  { 

	    int At511Peak = 0; 
	    if(	(fabs(energyBar - alignedBar_511Peak_mean[ibar])/alignedBar_511Peak_sigma[ibar])<NsigmaCut )
	      At511Peak = 1;

	      for (int idxbar=ibar-1;idxbar<ibar+2;++idxbar)
		{
		  if (idxbar<0 || idxbar>15)
		    continue; //edges

		  if (idxbar==ibar)
                    continue; //central bar

		  float energy1_xtalk=0;
		  float energy2_xtalk=0;

		  if( energy[idxbar+1]==-9. && energy[idxbar+17]==-9. )
		    continue;

		  nbars_xtalk++;

		  //energy 1
		  if( energy[idxbar+1]>-9. )
		    {
		      energy1_xtalk = energy[idxbar+1]-pedMean->GetBinContent(channels[idxbar+1]*4+tacID[idxbar+1]+1);

		      if(idxbar == ibar-1 && At511Peak)
			{
			  h1_energy1Left_Xtalk[ibar]->Fill(energy1_xtalk);
			}
		      if(idxbar == ibar+1 && At511Peak)
			{
			  h1_energy1Right_Xtalk[ibar]->Fill(energy1_xtalk);
			}

		      ++nhits_xtalk;
		    }

		  //energy 2
		  if( energy[idxbar+17]>-9. )
		    {
		      energy2_xtalk = energy[idxbar+17]-pedMean->GetBinContent(channels[idxbar+17]*4+tacID[idxbar+17]+1);

		      if(idxbar == ibar-1 && At511Peak)
			{
			  h1_energy2Left_Xtalk[ibar]->Fill(energy2_xtalk);
			}
		      if(idxbar == ibar+1 && At511Peak)
			{
			  h1_energy2Right_Xtalk[ibar]->Fill(energy2_xtalk);
			}

		      ++nhits_xtalk;
		    }
		  
		  float energyBar_xtalk =  energy1_xtalk + energy2_xtalk;

		  if(idxbar == ibar-1)
		    {
		      if(At511Peak)
			h1_energyLeft_Xtalk[ibar]->Fill(energyBar_xtalk);

		      h2_energyLeft_vs_energyBar_Xtalk[ibar]->Fill(energyBar,energyBar_xtalk);
		    }

		  if(idxbar == ibar+1)
		    {		     
		      if(At511Peak) 
			h1_energyRight_Xtalk[ibar]->Fill(energyBar_xtalk);

		      h2_energyRight_vs_energyBar_Xtalk[ibar]->Fill(energyBar,energyBar_xtalk);
		    }

		  energySum_xtalk += energyBar_xtalk;	

		}

	      if(At511Peak)
		{
		  h1_nhits_Xtalk[ibar]->Fill(nhits_xtalk);           
		  h1_nbars_Xtalk[ibar]->Fill(nbars_xtalk);           
		  h2_nbars_vs_nhits_Xtalk[ibar]->Fill(nhits_xtalk,nbars_xtalk);
		}	  

	      if(nhits_xtalk>0)
		{
		  if(At511Peak)
		    h1_energySum_Xtalk[ibar]->Fill(energySum_xtalk);

		  h2_energySum_vs_energyBar_Xtalk[ibar]->Fill(energyBar,energySum_xtalk);
		}
	  } //cut for xtalk

      }//loop over bars
 
  }//loop over events

  TFile *fOut=new TFile(outputFile,"UPDATE");
  fOut->cd();
  
  for ( auto &obj : objectsToStore)
    obj->Write();
  // fOut->Write();
  fOut->ls();
  fOut->Close();
  
}
