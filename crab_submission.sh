# cmsenv
# source /cvmfs/cms.cern.ch/common/crab-setup.sh
# voms-proxy-init --rfc --voms cms -valid 192:00

python3 crab_cfg.py \
    -f datasets.txt \
    -w JetMET0 \
    -o CRAB_skimmed_2024_data \
    -t Data   \
    -u mithakor \
    -n 5




