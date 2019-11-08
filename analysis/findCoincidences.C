#define findCoincidences_cxx
#include "findCoincidences.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TFile.h>
#include <TTree.h>
#include <iostream>
#include <TString.h>
#include <iostream>
#include <fstream>
#include <math.h>

#define MAX_EVENT_HITS 100

using namespace std ;

void parseConfig(std::ifstream *input)
{

  TString line;

  while(!input->eof()) {
    line.ReadLine(*input);

    if(line.BeginsWith("#")) continue;
    if(!line.BeginsWith("CH ")) continue;

    TObjArray* tokens=line.Tokenize(" ");
    if (tokens->GetEntries()!=15) continue;
    
    int chId= ((TObjString *)(tokens->At(1)))->String().Atoi();
    int iChip = ((TObjString *)(tokens->At(4)))->String().Atoi();
    int iChannel = ((TObjString *)(tokens->At(5)))->String().Atoi();
    int channelId = 64*iChip + iChannel;


    chMap[channelId]=chId;

    std::cout << "TOFPET Channel:" << channelId << "->CH" << chId << std::endl;
  }

  std::cout << "Found #" << chMap.size() << " channels in config" << std::endl;
}

// data format used as bridge between the high level structures and the root tree
struct treeStructData
{
  unsigned int n_channels;
  unsigned int n_coincidences;
  ULong64_t unixTime;
  
  double tempInt;
  double tempExt;
  double tempBoardTest;
  double tempBoardRef;
  double tempSiPMTest;
  double tempSiPMRef;

  unsigned int chID[MAX_EVENT_HITS];
  unsigned int tacID[MAX_EVENT_HITS];
  double  energy[MAX_EVENT_HITS];
  double  time[MAX_EVENT_HITS];
};

struct hit
{
  unsigned int chID;
  unsigned int tacID;
  double energy;
  double time;
} ;

struct eventProperties
{
  unsigned int nChannels;
  unsigned int nHits;
  
  ULong64_t unixTime;

  double tempInt;
  double tempExt;
  double tempBoardTest;
  double tempBoardRef;
  double tempSiPMTest;
  double tempSiPMRef;

  void clear()
  {
    nChannels=0;
    nHits=0;
    unixTime=0;
    tempInt=0;
    tempExt=0;
    tempBoardTest=0;
    tempSiPMTest=0;
    tempSiPMRef=0;
  };
} ;


struct Event
{
  Event (TFile * outFile, TTree * outTree) :
    outFile_ (outFile), 
    outTree_ (outTree) 
  { 
    createOutBranches (outTree_, thisTreeEvent_) ;   
  }

  ~Event () { }

  eventProperties id;
  std::vector<hit> hits;

  void clear () ;
  void Fill () ;

private :
  
  TFile * outFile_ ;
  TTree * outTree_ ;
  treeStructData thisTreeEvent_ ;

  void fillTreeData (treeStructData & treeData) ;
  void createOutBranches (TTree* tree,treeStructData& treeData) ;
} ;

void Event::createOutBranches (TTree* tree,treeStructData& treeData)
{
  tree->Branch( "nch", &treeData.n_channels, "nch/I" );
  tree->Branch( "ncoinc", &treeData.n_coincidences, "ncoinc/I" );
  tree->Branch( "chId", treeData.chID, "chId[nch]/I" );
  tree->Branch( "energy", treeData.energy, "energy[nch]/D" );
  tree->Branch( "time", treeData.time, "time[nch]/D" );
  tree->Branch( "tacID", treeData.tacID, "tacID[nch]/I" );
  tree->Branch( "unixTime", &treeData.unixTime, "unixTime/L" );
  tree->Branch( "tempInt", &treeData.tempInt, "tempInt/D" );
  tree->Branch( "tempExt", &treeData.tempExt, "tempExt/D" );
  tree->Branch( "tempBoardTest", &treeData.tempBoardTest, "tmpBoardTest/D" );
  tree->Branch( "tempBoardRef", &treeData.tempBoardRef, "tempBoardRef/D" );
  tree->Branch( "tempSiPMTest", &treeData.tempSiPMTest, "tempSiPMTest/D" );
  tree->Branch( "tempSiPMRef", &treeData.tempSiPMRef, "tempSiPMRef/D" );

  return ;
 } 

 void Event::fillTreeData (treeStructData & treeData)
 {
   treeData.n_channels = id.nChannels ;
   treeData.n_coincidences = id.nHits ;
   treeData.unixTime = id.unixTime ;

   treeData.tempInt = id.tempInt;
   treeData.tempExt = id.tempExt;
   treeData.tempBoardTest = id.tempBoardTest;
   treeData.tempBoardRef = id.tempBoardRef;
   treeData.tempSiPMTest = id.tempSiPMTest;
   treeData.tempSiPMRef = id.tempSiPMRef;

   for (unsigned int i = 0 ;i<fmin (MAX_EVENT_HITS, chMap.size()) ;++i)
     {
       treeData.chID[i] = -9;
       treeData.tacID[i] = -9;
       treeData.energy[i] = -9;
       treeData.time[i] = -9;
     }

   for (unsigned int i = 0 ;i<hits.size();++i)
     {
       treeData.chID[chMap[hits[i].chID]] = hits[i].chID;
       treeData.tacID[chMap[hits[i].chID]] = hits[i].tacID;
       treeData.energy[chMap[hits[i].chID]] = hits[i].energy;
       treeData.time[chMap[hits[i].chID]] = hits[i].time;
     }

   return ;
 }

 void Event::Fill ()
 {
   fillTreeData (thisTreeEvent_) ;
   outTree_->Fill () ;
   return ;
 }

 void Event::clear ()
 {
   id.clear () ;
   hits.clear () ; 
   return;
 }


void findCoincidences::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L findCoincidences.C
//      Root > findCoincidences t
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

   //   TString cfgFile="../config_main_array.txt";
   std::ifstream input(configFile);

   if(!input.is_open()) {
     std::cout << "Cannot open input file " << configFile << ".\n";
     return ;
   }

   parseConfig(&input);

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   Long64_t jentry=0;

   Long64_t goodEvents=0;

   TFile *outFile=new TFile(outputFile,"RECREATE");
   TTree *outTree=new TTree("data", "data");
   Event *event=new Event(outFile,outTree);

   while (jentry<nentries-1)
     {
       Long64_t tRef=0;
       Long64_t tDiff=0;
       int nHits=0;
  
       if (jentry%10000 == 0)
	 std::cout << "Processing hit " << jentry << std::endl;

       while ( abs(tDiff) < 20000 ) //50ns
	 {
	   ++jentry;
	   Long64_t ientry = LoadTree(jentry);
	   if (ientry < 0) break;
	   nb = fChain->GetEntry(jentry);   nbytes += nb;

	   if (nHits==0)
	     {
	       event->clear();
	       tRef = time;
	       event->id.nChannels = chMap.size();
	       event->id.unixTime = unixTime;
	       event->id.tempInt = tempInt;
	       event->id.tempExt = tempExt;
	       event->id.tempBoardTest = tempBoardTest;
	       event->id.tempBoardRef = tempBoardRef;
	       event->id.tempSiPMTest = tempSiPMTest;
	       event->id.tempSiPMRef = tempSiPMRef;
	     }
	   else
	       tDiff = time - tRef;

	   if (abs(tDiff) < 20000)
	     {
	       ++nHits;
	       event->id.nHits++;
	       hit aHit;
	       aHit.chID = channelID;
	       aHit.tacID = tacID;
	       aHit.energy = energy;
	       aHit.time = time;
	       event->hits.push_back(aHit);
	     }
 	 }

       if (nHits>1)
	 {
	   goodEvents++;
	   event->Fill();
	 }
       jentry-=1; //replay the last hit for next search window
     }

   outTree->Write();
   outFile->Close();
   std::cout << "Processed: " << nentries << " hits\nFound " << goodEvents << " events with coincidences" << std::endl;
}
