#!/bin/bash
set -euo pipefail

echo "CRAB Environment configurations"
echo "Hostname    : $(hostname)"
echo "Start time  : $(date)"
echo "CMSSW_BASE  : $CMSSW_BASE"
echo "PWD         : $PWD"
echo "Python path : $PYTHONPATH"

echo ""
echo "proxy information"
voms-proxy-info -all || echo "WARNING: Could not display proxy info"

echo ""
echo "Running PostProcessor"
echo "Executing: python3 crab_script.py $1"

python3 crab_script.py "$1"
## The argument $1 is needed but not used anywhere in the python script. This argument is added by CRAB by default. One cannot do anything about it.