//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Wed Nov  6 19:13:44 2019 by ROOT version 5.34/12
// from TTree data/Event List
// found on file: ../output/TestArray_06_11_2019_final/Run000002_2019-11-06-17-43-11_ARRAY000175_POS5_PHYS_qdc_Time300_Gate15_OvRef7_Ov7_singles.root
//////////////////////////////////////////////////////////

#ifndef findCoincidences_h
#define findCoincidences_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <map>

// Header file for the classes stored in the TTree if any.

// Fixed size dimensions of array or collections stored in the TTree if any.

std::map<int,int> chMap;

class findCoincidences {
public :
  
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


   TString       configFile;
   TString       outputFile;

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
   TBranch        *b_unixTime;   //!
   TBranch        *b_tempInt;   //!
   TBranch        *b_tempExt;   //!
   TBranch        *b_tempBoardTest;   //!
   TBranch        *b_tempBoardRef;   //!
   TBranch        *b_tempSiPMTest;   //!
   TBranch        *b_tempSiPMRef;   //!

   findCoincidences(TTree *tree=0);
   virtual ~findCoincidences();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef findCoincidences_cxx
findCoincidences::findCoincidences(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("../output/TestArray_06_11_2019_final/Run000002_2019-11-06-17-43-11_ARRAY000175_POS5_PHYS_qdc_Time300_Gate15_OvRef7_Ov7_singles.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../output/TestArray_06_11_2019_final/Run000002_2019-11-06-17-43-11_ARRAY000175_POS5_PHYS_qdc_Time300_Gate15_OvRef7_Ov7_singles.root");
      }
      f->GetObject("data",tree);

   }
   Init(tree);
}

findCoincidences::~findCoincidences()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t findCoincidences::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t findCoincidences::LoadTree(Long64_t entry)
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

void findCoincidences::Init(TTree *tree)
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
   fChain->SetBranchAddress("unixTime", &unixTime, &b_unixTime);
   fChain->SetBranchAddress("tempInt", &tempInt, &b_tempInt);
   fChain->SetBranchAddress("tempExt", &tempExt, &b_tempExt);
   fChain->SetBranchAddress("tempBoardTest", &tempBoardTest, &b_tempBoardTest);
   fChain->SetBranchAddress("tempBoardRef", &tempBoardRef, &b_tempBoardRef);
   fChain->SetBranchAddress("tempSiPMTest", &tempSiPMTest, &b_tempSiPMTest);
   fChain->SetBranchAddress("tempSiPMRef", &tempSiPMRef, &b_tempSiPMRef);
   Notify();
}

Bool_t findCoincidences::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void findCoincidences::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t findCoincidences::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef findCoincidences_cxx
