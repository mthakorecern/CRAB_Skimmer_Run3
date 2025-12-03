# cmsenv
# source /cvmfs/cms.cern.ch/common/crab-setup.sh
# voms-proxy-init --rfc --voms cms -valid 192:00

# python3 crab_cfg.py \
#     -f datasets.txt \
#     -w JetMET \
#     -o CRAB_skimmed_2024_data \
#     -t Data   \
#     -u mithakor \
#     -n 1

python3 crab_cfg.py \
    -f /afs/hep.wisc.edu/home/mithakor/Public/Skimmer_CRAB/CMSSW_15_0_2/src/Skimmer/Muon_datasets.txt \
    -w Muon \
    -o TriggerEfficiency_Skim \
    -t Data   \
    -u mithakor \
    -n 1





