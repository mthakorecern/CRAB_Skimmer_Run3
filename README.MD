# Skimmer using CRAB3
NanoAODTools based Skimmer for Run3 2024 Data+MC that also stores cutflow histograms for all the cuts applied

## Setup the environment/required dependencies:
```
cmsrel CMSSW_15_0_2
cd CMSSW_15_0_2/src/
cmsenv
```
### Obtain Grid proxy
```
voms-proxy-init -voms cms -out /tmp/x509up_u10196 -valid 192:00
```
### Setup CRAB environment
```
source /cvmfs/cms.cern.ch/common/crab-setup.sh
```
## Setting up the code
```
git clone https://github.com/mthakorecern/CRAB_Skimmer_Run3.git

cd CRAB_Skimmer_Run3
git switch fixedcutflow
```
Enter the name of a dataset in the datasets.txt file. Only one dataset name should be there in the file at all time. All other names should precede with a pound(#) sign.

For eg: ```/JetMET0/Run2024C-MINIv6NANOv15-v1/NANOAOD```

Then to submit the Skimming jobs, do 

```
python3 crab_cfg.py \
    -f datasets.txt \
    -w JetMET \
    -o CRAB_skimmed_2024_data \
    -t Data   \
    -u mithakor \
    -n 1
```
The output will be stored in your hdfs area under the CRAB_skimmed_2024_data directory. 


The Skimmer code has several scripts out of which the main ones are:
 
```crab_script.py```: This is the main Skimming code that performs the task of Skimming and filling the cutflow histogram. It applies all the cuts event by event and checks if the events satisfy all the conditions.
 
```PSet.py```: This is a dummy file which is required by CRAB. This should not be touched. 

```Datasets.txt```: This file should be populated with dataset names with only one dataset name uncommented.
 
```haddnano.py```: This file is required for running NanoAOD Tools on CRAB nodes. Can be ignored

```crab_cfg.py```: This file is the important code used for configuring CRAB jobs and submitting them. It’s already configured to submit one dataset at a time and store the output in T2_US_Wisconsin HDFS Area
