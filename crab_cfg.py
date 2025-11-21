#!/usr/bin/env python3

import argparse
import os

from CRABClient.UserUtilities import config as crabConfig
from CRABAPI.RawCommand import crabCommand


parser = argparse.ArgumentParser(description='Generate CRAB configuration')

parser.add_argument('-f','--datasetListFile', required=True, help='Text file containing list of datasets')
parser.add_argument('-w','--workArea', required=True, help='CRAB workArea: e.g., HHbbtt/2024_MC')
parser.add_argument('-o','--outputDir', required=True, help='relative output folder: e.g., HHbbtt/2024_MC')
parser.add_argument('-t','--type', choices=['Data','MC'], required=True, help='Whether Data or MC affects requestName')
parser.add_argument('-u','--username', required=True, help='Wisconsin T2 username')
parser.add_argument('-n','--unitsperjob', type=int, default=1, help='Files per job (FileBased splitting)')
args = parser.parse_args()

with open(args.datasetListFile) as f:
    datasets = [
        d.strip() for d in f.readlines()
        if d.strip() and not d.startswith("#")
    ]

for dataset in datasets:
    print(f"\nSubmitting dataset: {dataset}")
    if args.type == "MC":
        name = dataset.strip("/")
        name = name.removesuffix("NANOAODSIM")
        name = name.rstrip("/")
        name = name.replace("/", "_")
        req = name
    else:  
        parts = dataset.strip().split("/")
        primary = parts[1]
        secondary = parts[2]

        base = os.path.basename(secondary)
        if "_RunIII" in base:
            clean = base.split("_RunIII")[0]
        elif "_NANOAOD" in base:
            clean = base.split("_NANOAOD")[0] + "_NANOAOD"
        else:
            clean = base

        req = f"{primary}_{clean}"  
    
    # config.section_("General")
    # config.section_("JobType")
    # config.section_("Data")
    # config.section_("Site")

    config = crabConfig()
    config.General.requestName = req
    config.General.transferLogs = True
    config.General.workArea = args.workArea
    config.General.transferOutputs = True

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
    except Exception as e:
        print(f"Failed submitting {dataset}:")
        print(e)
        continue
