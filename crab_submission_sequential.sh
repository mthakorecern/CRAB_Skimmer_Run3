# cmsenv
# source /cvmfs/cms.cern.ch/common/crab-setup.sh
# voms-proxy-init --rfc --voms cms -valid 192:00

# python3 crab_cfg_sequential.py \
#     -f datasets_MC.txt \
#     -w MC \
#     -o CRAB_skimmed_2024_MC \
#     -t MC   \
#     -u mithakor \
#     -n 1


# python3 crab_cfg_sequential.py \
#     -f /afs/hep.wisc.edu/home/mithakor/Public/Skimmer_CRAB/CMSSW_15_0_2/src/Skimmer/datasets.txt \
#     -w JETMET \
#     -o CRAB_skimmed_2024_Data \
#     -t Data   \
#     -u mithakor \
#     -n 1

python3 crab_cfg_sequential.py \
    -f /afs/hep.wisc.edu/home/mithakor/Public/Skimmer_CRAB/CMSSW_15_0_2/src/Skimmer/datasets_MC.txt \
    -w MC \
    -o CRAB_skimmed_2024_MC \
    -t MC   \
    -u mithakor \
    -n 1

# python3 crab_cfg_sequential.py \
#     -f /afs/hep.wisc.edu/home/mithakor/Public/Skimmer_CRAB/CMSSW_15_0_2/src/Skimmer/datasets_jetbinned.txt \
#     -w MC \
#     -o CRAB_skimmed_2024_MC \
#     -t MC   \
#     -u mithakor \
#     -n 1