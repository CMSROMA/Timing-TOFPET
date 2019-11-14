//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Wed Nov 13 15:32:17 2019 by ROOT version 5.34/12
// from TTree data/Event List
// found on file: output/TestPaolo/Run000002_2019-11-10-12-07-16_ARRAY000175_POS5_X30.0_Y23.0_CH0-5-6-7-21-22-23_ETHR0-10-0-10-10-0-10_PHYS_qdc_Time300_Gate15_OvRef7_Ov7_singles.root
//////////////////////////////////////////////////////////

#ifndef addTemperature_h
#define addTemperature_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TString.h>
#include <map>
// Header file for the classes stored in the TTree if any.

// Fixed size dimensions of array or collections stored in the TTree if any.

std::map< long, float* > temperatures;


class addTemperature {
public :
long        unixtimeStart;
   TString        tempFile;

TFile* out;
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

   // Declaration of leaf types
   Float_t         step1;
   Float_t         step2;
   Long64_t        time;
   UShort_t        channelID;
   Float_t         tot;
   Float_t         energy;
   UShort_t        tacID;
   Int_t           xi;
   Int_t           yi;
   Float_t         x;
   Float_t         y;
   Float_t         z;
   Float_t         tqT;
   Float_t         tqE;
   Long64_t        unixTime;
   Double_t        tempInt;
   Double_t        tempExt;
   Double_t        tempBoardTest;
   Double_t        tempBoardRef;
   Double_t        tempSiPMTest;
   Double_t        tempSiPMRef;

   // List of branches
   TBranch        *b_step1;   //!
   TBranch        *b_step2;   //!
   TBranch        *b_time;   //!
   TBranch        *b_channelID;   //!
   TBranch        *b_tot;   //!
   TBranch        *b_energy;   //!
   TBranch        *b_tacID;   //!
   TBranch        *b_xi;   //!
   TBranch        *b_yi;   //!
   TBranch        *b_x;   //!
   TBranch        *b_y;   //!
   TBranch        *b_z;   //!
   TBranch        *b_tqT;   //!
   TBranch        *b_tqE;   //!

   std::vector<TBranch*> newBranches;

   addTemperature(TTree *tree=0);
   virtual ~addTemperature();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef addTemperature_cxx
addTemperature::addTemperature(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
TFile* f = new TFile("output/TestPaolo/Run000002_2019-11-10-12-07-16_ARRAY000175_POS5_X30.0_Y23.0_CH0-5-6-7-21-22-23_ETHR0-10-0-10-10-0-10_PHYS_qdc_Time300_Gate15_OvRef7_Ov7_singles.root","UPDATE");

      f->GetObject("data",tree);

   }
   Init(tree);
}

addTemperature::~addTemperature()
{
   /* if (!fChain) return; */
   /* delete fChain->GetCurrentFile(); */
  return;
}

Int_t addTemperature::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t addTemperature::LoadTree(Long64_t entry)
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

void addTemperature::Init(TTree *tree)
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

   fChain->SetBranchAddress("step1", &step1, &b_step1);
   fChain->SetBranchAddress("step2", &step2, &b_step2);
   fChain->SetBranchAddress("time", &time, &b_time);
   fChain->SetBranchAddress("channelID", &channelID, &b_channelID);
   fChain->SetBranchAddress("tot", &tot, &b_tot);
   fChain->SetBranchAddress("energy", &energy, &b_energy);
   fChain->SetBranchAddress("tacID", &tacID, &b_tacID);
   fChain->SetBranchAddress("xi", &xi, &b_xi);
   fChain->SetBranchAddress("yi", &yi, &b_yi);
   fChain->SetBranchAddress("x", &x, &b_x);
   fChain->SetBranchAddress("y", &y, &b_y);
   fChain->SetBranchAddress("z", &z, &b_z);
   fChain->SetBranchAddress("tqT", &tqT, &b_tqT);
   fChain->SetBranchAddress("tqE", &tqE, &b_tqE);
   newBranches.push_back(fChain->Branch("unixTime", &unixTime, "unixTime/L"));
   newBranches.push_back(fChain->Branch("tempInt", &tempInt, "tempInt/D"));
   newBranches.push_back(fChain->Branch("tempExt", &tempExt, "tempExt/D"));
   newBranches.push_back(fChain->Branch("tempBoardTest", &tempBoardTest, "tempBoardTest/D" ));
   newBranches.push_back(fChain->Branch("tempBoardRef", &tempBoardRef, "tempBoardRef/D" ));
   newBranches.push_back(fChain->Branch("tempSiPMTest", &tempSiPMTest, "tempSiPMTest/D" ));
   newBranches.push_back(fChain->Branch("tempSiPMRef", &tempSiPMRef, "tempSiPMRef/D" ));
   
   Notify();
}

Bool_t addTemperature::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void addTemperature::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t addTemperature::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef addTemperature_cxx
