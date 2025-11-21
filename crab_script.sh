#!/bin/bash
set -euo pipefail

echo "========== CRAB Job Environment =========="
echo "Hostname    : $(hostname)"
echo "Start time  : $(date)"
echo "CMSSW_BASE  : $CMSSW_BASE"
echo "PWD         : $PWD"
echo "Python path : $PYTHONPATH"

echo ""
echo "========== Proxy Information ============="
voms-proxy-info -all || echo "WARNING: Could not display proxy info"

echo ""
echo "========== Running PostProcessor =========="
echo "Executing: python3 crab_script.py $1"
echo "-------------------------------------------"

# Run PostProcessor and capture exit code
python3 crab_script.py "$1"
