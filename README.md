# Table of Contents
- [Setup](#user-content-setup)
- [Connect TOFPET](#user-content-connect-tofpet)
- [Run TOFPET](#user-content-run-tofpet)

# Setup

```
mkdir -p Workspace/TOFPET
cd Workspace/TOFPET
git clone https://github.com/CMSROMA/Timing-TOFPET.git
cd Timing-TOFPET
cmake .
make
```
# Connect TOFPET

From a terminal
```
cd Workspace/TOFPET/Timing-TOFPET
./connect_TOFPET.sh
```

It will display
```
cmsdaq@pccmsdaq01:~/Workspace/TOFPET/Timing-TOFPET$ ./connect_TOFPET.sh 
Size of frame is 16384
Got FPGA reply
FrameServer::startWorker called...
FrameServer::startWorker exiting...
UDPFrameServer::runWorker starting...
```

Always keep this process active during a run in this terminal.

# Run TOFPET

Open a new terminal. 

Edit configuration file:
```
config_main.txt
```

Start data taking
```
python run_TOFPET.py -c config_main.txt
```

## Notes
- The calibration (RUN_CALIB 1 in config file) should be re-run each time there is a new hardware configuration (e.g. different SiPMs, different hardware settings). It takes about 30-40 minutes to finish. 
- Once the calibration step is done, the following runs can be taken using the existing calibration files (RUN_CALIB 0 in config file) 
- Two output root files are produced: 
  - xxx_singles.root: the tree contains one event for each channel passing the trigger selection (1 event -> 1 channel, only channels above thresholds are stored)  
  - xxx_coincidences.root: the tree contains all the channel info. Only events in which there is at least one time coincidence between a pair of channels (default t2-t1<20 ns) are stored. The file is created by running a script on the xxx_singles.root file. If a signal doesn't pass the "singles" trigger selection, its values are set to "-9" in the root file and should be ignored. 
     - The content of the tree is:
```
"nch" = number of channels (as reported in the config_main.txt configuration file), same for all events in the tree
"ncoinc" = number of coincidences in the event
"chId[nch]" = array of dimension "nch" with the absolute channel id (e.g. chId[0] is the abs channel ID of the channel indicated as "CH 0" in the config file) 
"energy[nch]" = array of dimension "nch" with the energy value in ADC counts (e.g. energy[0] is the energy of the channel indicated as "CH 0" in the config file) 
"time[nch]" = array of dimension "nch" with the precise time value from TDC (e.g. time[0] is the energy of the channel indicated as "CH 0" in the config file) 

```
- Channel numbering in root file: Absolute channel ID (root file) = 64 x NCHIP + NCH  where NCHIP, NCH are reported in the config file.

