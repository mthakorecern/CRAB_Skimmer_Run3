#!/usr/bin/env python3
import os
import ROOT
ROOT.TH1.AddDirectory(False)
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
from PhysicsTools.NanoAODTools.postprocessing.utils.crabhelper import inputFiles, runsAndLumis
from PhysicsTools.NanoAODTools.postprocessing.examples.exampleModule import *
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class SimpleNanoModule(Module):

    def __init__(self):
        super().__init__()

        self.cut_functions = [
            lambda ev: ev.nFatJet > 0,
            lambda ev: ev.PuppiMET_pt >= 120,
            lambda ev: ev.Flag_goodVertices == 1,
            lambda ev: ev.Flag_globalSuperTightHalo2016Filter == 1,
            lambda ev: ev.Flag_EcalDeadCellTriggerPrimitiveFilter == 1,
            lambda ev: ev.Flag_BadPFMuonFilter == 1,
            lambda ev: ev.Flag_BadPFMuonDzFilter == 1,
            lambda ev: ev.Flag_hfNoisyHitsFilter == 1,
            lambda ev: ev.Flag_eeBadScFilter == 1,
            lambda ev: ev.Flag_ecalBadCalibFilter == 1,
            lambda ev: (ev.PV_ndof > 4)
                       and abs(ev.PV_z) < 24
                       and math.sqrt(ev.PV_x * ev.PV_x + ev.PV_y * ev.PV_y) < 2,
            lambda ev: (ev.nTau > 0) or (getattr(ev, "nboostedTau", 0) > 0),
        ]

        self.cut_names = [
            "FatJet Requirement",
            "PuppiMET_pt Threshold",
            "Flag_goodVertices",
            "Flag_globalSuperTightHalo2016Filter",
            "Flag_EcalDeadCellTriggerPrimitiveFilter",
            "Flag_BadPFMuonFilter",
            "Flag_BadPFMuonDzFilter",
            "Flag_hfNoisyHitsFilter",
            "Flag_eeBadScFilter",
            "Flag_ecalBadCalibFilter",
            "Good Primary Vertices",
            "Tau requirement",
        ]


    def beginJob(self):
        self.global_raw_events   = 0        
        self.global_genWeightSum = 0.0     
        self.global_cutCounts    = [0] * len(self.cut_names)
    
        self.file_raw_events   = 0
        self.file_genWeightSum = 0.0
        self.file_cutCounts    = [0] * len(self.cut_names)


        self.isMC = None

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):

        branches = [b.GetName() for b in inputTree.GetListOfBranches()]
        if self.isMC is None:
            self.isMC = ("genWeight" in branches)

        events = inputTree.GetEntries()

        # Reset per-file counters
        self.file_raw_events   = events
        self.file_genWeightSum = 0.0
        self.file_cutCounts    = [0] * len(self.cut_names)

        # Update global count of raw events (unweighted)
        self.global_raw_events += events

        print(f"\n[beginFile] File: {inputFile.GetName()}")
        print(f"Raw events: {events}")
        print(f"Accumulated raw events: {self.global_raw_events}")

    def analyze(self, event):
        w = 1.0

        if self.isMC:
            try:
                gw = float(event.genWeight)
            except:
                gw = 1.0
            self.file_genWeightSum   += gw
            self.global_genWeightSum += gw

        for i, cut in enumerate(self.cut_functions):
            if not cut(event):
                return False  # event fails here

            self.global_cutCounts[i] += 1
            self.file_cutCounts[i]   += 1

        return True


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print(f"[endFile] {inputFile.GetName()}")

        if outputFile is None:
            return

        print("[endFile] Writing per-file cutflow histogram...")

        nCuts = len(self.cut_names)

        # Histogram ranges
        if self.isMC:
            nBins = nCuts + 2   # SumGenW + NoCuts + cuts
        else:
            nBins = nCuts + 1   # NoCuts + cuts only

        # Create histogram
        h = ROOT.TH1F("cutflow", "cutflow", nBins, 0, nBins)

        # ❗ Attach histogram to output file BEFORE setting labels
        h.SetDirectory(outputFile)

        # Now assign bin labels
        if self.isMC:
            h.GetXaxis().SetBinLabel(1, "Sum of GenWeights")
            h.GetXaxis().SetBinLabel(2, "No Cuts")
            for i, name in enumerate(self.cut_names):
                h.GetXaxis().SetBinLabel(3+i, name)
        else:
            h.GetXaxis().SetBinLabel(1, "No Cuts")
            for i, name in enumerate(self.cut_names):
                h.GetXaxis().SetBinLabel(2+i, name)

        # Fill the cutflow
        if self.isMC:
            h.SetBinContent(1, self.file_genWeightSum)
            h.SetBinContent(2, self.file_raw_events)
            for i, v in enumerate(self.file_cutCounts):
                h.SetBinContent(3+i, v)
        else:
            h.SetBinContent(1, self.file_raw_events)
            for i, v in enumerate(self.file_cutCounts):
                h.SetBinContent(2+i, v)

        # Write
        outputFile.cd()
        h.Write()
        print("[endFile] Per-file cutflow written.")


    def endJob(self):
        print("\n================ GLOBAL SUMMARY ================")

        if self.isMC:
            print(f"Total raw events     : {self.global_raw_events}")
            print(f"Sum of genWeights    : {self.global_genWeightSum:.4f}")
        else:
            print(f"Total raw events     : {self.global_raw_events}")

        print("\nEvents passing each cut:")
        for i, name in enumerate(self.cut_names):
            print(f"  Cut {i+1:02d} ({name}): {self.global_cutCounts[i]}")

        pass



p = PostProcessor(".",
                  inputFiles(),
                  cut=None,
                  modules=[SimpleNanoModule()],
                  provenance=True,
                  fwkJobReport=True,
                  postfix="",
                  haddFileName=None,
                  jsonInput=runsAndLumis())
p.run()

print("DONE")