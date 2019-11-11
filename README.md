# Table of Contents
- [Setup](#user-content-setup)
- [Read temperature sensors](#user-content-read-temperature-sensors)
- [Move xy table](#user-content-move-xy-table)
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

# Read temperature sensors

Load firmware to arduino (only the first time):
```
arduino/temperature/temp_DS18B20/temp_DS18B20.ino
```
The default setup reads 6 temperature sensors (DS18B20).
The sensors are positioned in the following way in order:
- 1: Reference TOFPET board (on the metallic plate)   
- 2: Internal (air)
- 3: External (air)
- 4: Test TOFPET board (on the metallic plate) 
- 5: Reference SiPM (air)
- 6: Test SiPM (air)

Open a new terminal
```
cd Workspace/TOFPET/Timing-TOFPET/arduino/temperature
python3 read_temp.py -o temperature_tmp.txt -p /dev/tempmon_0 -r 9600
```

It will add (append) a line every 2 seconds (configurable from arduino firmware) in the output file "temperature_tmp.txt" with this format: "unix_time temp1 temp2 temp3 temp4 temp5 temp6". Temperatures are reported in Celsius degrees; unix epoch time in seconds (https://www.epochconverter.com).

Example:
```
[...]
1561125966 28.00 27.12 27.31 28.19 27.06 27.19
1561125968 28.00 27.12 27.31 28.12 27.06 27.19
1561125970 28.06 27.12 27.31 28.12 27.06 27.19
1561125972 28.00 27.12 27.31 28.12 27.06 27.19
[...]
```

# Move xy table

## Load firmware to arduino (only the first time)

* Download grbl code v0_8 from https://github.com/grbl/grbl/tree/v0_8 
* Edit config.h file (see https://github.com/grbl/grbl/issues/224) 
```
#define HOMING_SEARCH_CYCLE_0 ((1<<X_AXIS)|(1<<Y_AXIS))
#define HOMING_LOCATE_CYCLE   ((1<<X_AXIS)|(1<<Y_AXIS))
```
* Compile the code
```
make
```
* Upload the executable firmware grbl.hex on arduino using HexUploader (http://paulkaplan.me/HexUploader/)
NOTE: the current version of the firmware is available at 
```
Workspace/TOFPET/Timing-TOFPET/arduino/tablexy/grbl.hex
```

## Use the xy table

Open a new terminal and start the grbl server
```
cd Workspace/TOFPET/Timing-TOFPET/arduino/tablexy
```

To move the xytable of the test crystal
```
python3 grblServer.py --usb /dev/motor_0 -l /tmp/test.log
```
To move the xytable of the reference crystal
```
python3 grblServer.py --usb /dev/ttyACM2 -l /tmp/test.log
```
(At the moment the two xy tables cannot be used at the same time. To be fixed.)


Open a new terminal. 
```
cd Workspace/TOFPET/Timing-TOFPET/arduino/tablexy
```

Then you have different options:

### 1) Start the GUI (to move the xy table interactively)
NOTE: make the window size big enough (about 3/4 of the laptop screen) 
to see the "exit" and "apply" button at the bottom right of the GUI panel.
```
python xyShell.py
```

### 2) Move the table using a python script (test example)
```
python testXYMover.py
```

NOTE: when you finish to work, remember to kill the server python script from the first terminal.


# Connect TOFPET

Open a new terminal
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

# Run TOFPET DAQ

## Single run

Open a new terminal. 

Edit configuration file for pixels:
```
config_main.txt
```
or for pixel + bar:
```
config_main_bar.txt
```
Note: the temperature file should be the same specified in the previous step (i.e. arduino/temperature/temperature_tmp.txt). At the end of each run the recorded temperatures will be attached to the end of this file 
```
arduino/temperature/temperature_all.txt
```

Start data taking

Take all options from config_main.txt:
```
python run_TOFPET.py -c config_main.txt
```

Physics run (overwrite options from command line):
```
python run_TOFPET.py -c config_main.txt --runType PHYS -d my_acquire_sipm_data -t 10 -v 3 --ovref 3 -l NoSource_1 -g 15 -o output/ScanTest
```
Pedestal run (overwrite options from command line):
```
python run_TOFPET.py -c config_main.txt --runType PED -d acquire_pedestal_data -t 1 -v 3 --ovref 3 -l Ped_1 -g 15 -o output/ScanTest
```

### Notes
- The calibration (RUN_CALIB 1 in config file) should be re-run each time there is a new hardware configuration (e.g. different SiPMs, different hardware settings). It takes about 30-40 minutes to finish. 
- Once the calibration step is done, the following runs can be taken using the existing calibration files (RUN_CALIB 0 in config file) 
- Channel numbering in root file: Absolute channel ID (root file) = 64 x NCHIP + NCH  where NCHIP, NCH are reported in the config file.


## Run sequences

### BARS

### ARRAYS
Edit last part of "run_DAQ.py" ("Run daq sequence") to define the sequence.

Run DAQ:
```
python run_DAQ.py -c config_main_array.txt -o /data/TOFPET/LYSOARRAYS -n ARRAY000175_WS1_NW_NC
```

Create root files:
```
python process_runs.py -r 1,2,3 -d /data/TOFPET/LYSOARRAYS 
```
or
```
python process_runs.py -r 1-3 -d /data/TOFPET/LYSOARRAYS 
```
Note: put the comma-separated list of the runs you want to analyze.

Run analysis:
```
python analysis/analyze_run_array.py --run 2 --arrayCode 175 -i /data/TOFPET/LYSOARRAYS  -o /data/TOFPET/LYSOARRAYS/RESULTS
```
Note: the run number should be the "PHYS" one (the code will also process the previous and following pedestal runs, 1 and 3 in this example)


