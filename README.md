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
- The output file contains a root tree (xxx_singles.root): 
  - the root tree contains one event for each channel passing the trigger selection  
- Channel numbering in root file: Absolute channel ID (root file) = 64 x NCHIP + NCH  where NCHIP, NCH are reported in the config file.

