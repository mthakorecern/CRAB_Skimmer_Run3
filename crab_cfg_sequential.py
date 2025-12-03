#!/usr/bin/env python3

import argparse
import os
import time
from CRABClient.UserUtilities import config as crabConfig
from CRABAPI.RawCommand import crabCommand


def make_short_request_name(dataset, dtype):
    """
    dataset: full DAS dataset string, e.g.
      /JetMET0/Run2024C-MINIv6NANOv15-v1/NANOAOD
      /TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024.../NANOAODSIM

    dtype: "Data" or "MC"
    """

    parts = dataset.strip("/").split("/")
    # Expected:
    # parts[0] = primary dataset
    # parts[1] = processing string (Run2024C-MINIv6NANOv15-v1)
    # parts[2] = datatier (NANOAOD or NANOAODSIM)

    primary = parts[0]
    procstr = parts[1]
    tier    = parts[2]

    if dtype == "MC":
        # For MC you want ONLY:
        #   TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8
        #
        # That is exactly parts[0]
        return primary[:90]

    else:
        # DATA CASE
        #
        # Desired:
        #   JetMET0_Run2024C-MINIv6NANOv15-v1_NANOAOD
        #
        # Special rule: preserve processing string EXACTLY as-is,
        # including odd patterns like MINIv6NANOv15_v2-v1.
        #
        # Keep the tier unchanged.
        #
        return f"{primary}_{procstr}_{tier}"[:90]

parser = argparse.ArgumentParser(description='Generate CRAB configuration')

parser.add_argument('-f', '--datasetListFile', required=True, help='Text file containing list of datasets')
parser.add_argument('-w', '--workArea', required=True, help='CRAB workArea: e.g., HHbbtt/2024_MC')
parser.add_argument('-o', '--outputDir', required=True, help='relative output folder')
parser.add_argument('-t', '--type', choices=['Data','MC'], required=True)
parser.add_argument('-u', '--username', required=True)
parser.add_argument('-n', '--unitsperjob', type=int, default=1)
args = parser.parse_args()

with open(args.datasetListFile) as f:
    datasets = [
        d.strip() for d in f.readlines()
        if d.strip() and not d.startswith("#")
    ]

for dataset in datasets:
    print(f"\nSubmitting {dataset}")
    req = make_short_request_name(dataset, args.type)
    config = crabConfig()
    config.General.requestName = req
    config.General.transferLogs = True
    config.General.transferOutputs = True
    config.General.workArea = args.workArea

    config.JobType.pluginName = 'Analysis'
    config.JobType.psetName = 'PSet.py'
    config.JobType.scriptExe = 'crab_script.sh'
    config.JobType.inputFiles = ['crab_script.py', 'haddnano.py']
    config.JobType.maxMemoryMB = 2000
    config.JobType.maxJobRuntimeMin = 500
    config.JobType.disableAutomaticOutputCollection = True
    config.JobType.outputFiles = ['tree.root']

    config.Data.inputDataset = dataset
    config.Data.inputDBS = 'global'
    config.Data.splitting = 'FileBased'
    config.Data.unitsPerJob = args.unitsperjob
    config.Data.ignoreLocality = True
    config.Data.publication = False
    config.Data.outputDatasetTag = f"NanoPost_{args.type}_{req}"
    config.Data.outLFNDirBase = f"/store/user/{args.username}/{args.outputDir}"

    config.Site.storageSite = "T2_US_Wisconsin"
    config.Site.whitelist = []

    try:
        crabCommand("submit", config=config)
        print(f"Submitted: {req}")
    except Exception as e:
        print(f"ERROR submitting {dataset}")
        print(e)
        continue

print("\nAll datasets processed.\n")
