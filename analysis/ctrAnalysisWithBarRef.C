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
  
  TH1F* h1_deltaT12[N_BARS];
  TH1F* h1_CTR[N_BARS];
  TH1F* h1_deltaT12_barRef[N_BARS];

  for (int ibar=0;ibar<16;++ibar)
    {

      h1_deltaT12[ibar] = new TH1F(Form("h1_deltaT12_bar%d",ibar), "", 800, -10000, 10000);
      objectsToStore.push_back(h1_deltaT12[ibar]);

      h1_CTR[ibar]  = new TH1F(Form("h1_CTR_bar%d",ibar), "", 800, -10000, 10000);
      objectsToStore.push_back(h1_CTR[ibar]);

      h1_deltaT12_barRef[ibar] = new TH1F(Form("h1_deltaT12_barRef_coincBar%d",ibar), "", 800, -10000, 10000);
      objectsToStore.push_back(h1_deltaT12_barRef[ibar]);
    }

  Long64_t nentries = fChain->GetEntriesFast();
  
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
	
	///Time resolution
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
	  }

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
