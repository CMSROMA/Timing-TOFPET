//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Nov 12 19:11:04 2019 by ROOT version 5.34/12
// from TTree data/data
// found on file: ../output/TestArray_10_11_2019/Run000002_2019-11-10-12-07-16_ARRAY000175_POS5_X30.0_Y23.0_CH0-5-6-7-21-22-23_ETHR0-10-0-10-10-0-10_PHYS_qdc_Time300_Gate15_OvRef7_Ov7_coincidences.root
//////////////////////////////////////////////////////////

#ifndef ctrAnalysisWithBarRef_h
#define ctrAnalysisWithBarRef_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH1F.h>
#include <TString.h>

// Header file for the classes stored in the TTree if any.

// Fixed size dimensions of array or collections stored in the TTree if any.

class ctrAnalysisWithBarRef 
{
 public :
  int channels[34];
  
  TString         outputFile;
  TH1F*           pedMean;
  TH1F*           pedRms;
  
  float barRef_511Peak_mean;
  float barRef_511Peak_sigma;
  
  std::vector<float> alignedBar_511Peak_mean;
  std::vector<float> alignedBar_511Peak_sigma;
  
  TTree          *fChain;   //!pointer to the analyzed TTree or TChain
  Int_t           fCurrent; //!current Tree number in a TChain
  
  // Declaration of leaf types
  Int_t           nch;
  Int_t           ncoinc;
  Int_t           chId[34];   //[nch]
  Double_t        energy[34];   //[nch]
  Double_t        time[34];   //[nch]
  Int_t           tacID[34];   //[nch]
  Long64_t        unixTime;
  Double_t        tempInt;
  Double_t        tempExt;
  Double_t        tempBoardTest;
  Double_t        tempBoardRef;
  Double_t        tempSiPMTest;
  Double_t        tempSiPMRef;
  
  // List of branches
  TBranch        *b_nch;   //!
  TBranch        *b_ncoinc;   //!
  TBranch        *b_chId;   //!
  TBranch        *b_energy;   //!
  TBranch        *b_time;   //!
  TBranch        *b_tacID;   //!
  TBranch        *b_unixTime;   //!
  TBranch        *b_tempInt;   //!
  TBranch        *b_tempExt;   //!
  TBranch        *b_tmpBoardTest;   //!
  TBranch        *b_tempBoardRef;   //!
  TBranch        *b_tempSiPMTest;   //!
  TBranch        *b_tempSiPMRef;   //!
  
  ctrAnalysisWithBarRef(TTree *tree=0);
  virtual ~ctrAnalysisWithBarRef();
  virtual Int_t    Cut(Long64_t entry);
  virtual Int_t    GetEntry(Long64_t entry);
  virtual Long64_t LoadTree(Long64_t entry);
  virtual void     Init(TTree *tree);
  virtual void     Loop();
  virtual Bool_t   Notify();
  virtual void     Show(Long64_t entry = -1);
  virtual void     LoadPedestals(TString pedestalFile);
};

#endif

#ifdef ctrAnalysisWithBarRef_cxx
ctrAnalysisWithBarRef::ctrAnalysisWithBarRef(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("../output/TestArray_10_11_2019/Run000002_2019-11-10-12-07-16_ARRAY000175_POS5_X30.0_Y23.0_CH0-5-6-7-21-22-23_ETHR0-10-0-10-10-0-10_PHYS_qdc_Time300_Gate15_OvRef7_Ov7_coincidences.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../output/TestArray_10_11_2019/Run000002_2019-11-10-12-07-16_ARRAY000175_POS5_X30.0_Y23.0_CH0-5-6-7-21-22-23_ETHR0-10-0-10-10-0-10_PHYS_qdc_Time300_Gate15_OvRef7_Ov7_coincidences.root");
      }
      f->GetObject("data",tree);

   }
   Init(tree);
}

ctrAnalysisWithBarRef::~ctrAnalysisWithBarRef()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t ctrAnalysisWithBarRef::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t ctrAnalysisWithBarRef::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void ctrAnalysisWithBarRef::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("nch", &nch, &b_nch);
   fChain->SetBranchAddress("ncoinc", &ncoinc, &b_ncoinc);
   fChain->SetBranchAddress("chId", chId, &b_chId);
   fChain->SetBranchAddress("energy", energy, &b_energy);
   fChain->SetBranchAddress("time", time, &b_time);
   fChain->SetBranchAddress("tacID", tacID, &b_tacID);
   fChain->SetBranchAddress("unixTime", &unixTime, &b_unixTime);
   fChain->SetBranchAddress("tempInt", &tempInt, &b_tempInt);
   fChain->SetBranchAddress("tempExt", &tempExt, &b_tempExt);
   fChain->SetBranchAddress("tempBoardTest", &tempBoardTest, &b_tmpBoardTest);
   fChain->SetBranchAddress("tempBoardRef", &tempBoardRef, &b_tempBoardRef);
   fChain->SetBranchAddress("tempSiPMTest", &tempSiPMTest, &b_tempSiPMTest);
   fChain->SetBranchAddress("tempSiPMRef", &tempSiPMRef, &b_tempSiPMRef);
   Notify();
}

Bool_t ctrAnalysisWithBarRef::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void ctrAnalysisWithBarRef::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t ctrAnalysisWithBarRef::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef ctrAnalysisWithBarRef_cxx
