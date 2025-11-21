#!/usr/bin/env python3

import argparse
import os
import time
from CRABClient.UserUtilities import config as crabConfig
from CRABAPI.RawCommand import crabCommand


def make_short_request_name(dataset, dtype):
    parts = dataset.strip("/").split("/")

    if dtype == "MC":
        primary = parts[0]

        primary = primary.replace("TuneCP5", "")
        primary = primary.replace("13p6TeV", "")
        primary = primary.replace("pythia8", "")
        primary = primary.replace("amcatnloFXFX", "")
        primary = primary.replace("RunIII2024Summer24NanoAODv15", "")
        primary = primary.replace("150X_mcRun3_2024_realistic_v2", "")

        tokens = primary.split("_")
        short = "_".join(tokens[:3]) 
        return short[:90]

    else:  
        primary = parts[1]
        secondary = parts[2]

        sec = secondary.split("-")[0]
        sec = sec.replace("MINIv6NANOv15", "NANOv15")
        sec = sec.replace("Run", "")

        short = f"{primary}_{sec}"
        return short[:90]

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
    config.JobType.maxMemoryMB = 2500
    config.JobType.maxJobRuntimeMin = 1400
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
