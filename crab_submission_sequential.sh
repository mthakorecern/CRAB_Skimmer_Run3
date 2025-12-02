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


python3 crab_cfg_sequential.py \
    -f datasets_jetbinned.txt \
    -w MC \
    -o CRAB_skimmed_2024_MC \
    -t MC   \
    -u mithakor \
    -n 1

