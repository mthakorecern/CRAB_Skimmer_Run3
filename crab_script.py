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
            # lambda ev: ev.PuppiMET_pt >= 120,
            lambda ev: ev.PuppiMET_pt > 80,
            lambda ev: ev.Flag_goodVertices == 1,
            lambda ev: ev.Flag_globalSuperTightHalo2016Filter == 1,
            lambda ev: ev.Flag_EcalDeadCellTriggerPrimitiveFilter == 1,
            lambda ev: ev.Flag_BadPFMuonFilter == 1,
            lambda ev: ev.Flag_BadPFMuonDzFilter == 1,
            lambda ev: ev.Flag_hfNoisyHitsFilter == 1,
            lambda ev: ev.Flag_eeBadScFilter == 1,
            lambda ev: ev.Flag_ecalBadCalibFilter == 1,
            lambda ev: (ev.PV_ndof > 4) and abs(ev.PV_z) < 24 and math.sqrt(ev.PV_x*ev.PV_x + ev.PV_y*ev.PV_y) < 2,
            # lambda ev: (ev.nTau > 0) or (ev.nboostedTau > 0),
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
            # "Tau requirement",
        ]

        self.isMC = None


    def beginJob(self):
        pass


    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):

        branches = [b.GetName() for b in inputTree.GetListOfBranches()]
        self.isMC = ("genWeight" in branches)
        
        ## Total Event entries
        self.file_raw_events = inputTree.GetEntries()
        self.file_cutCounts = [0] * len(self.cut_names)
        
        ## Collecting sumofGenWeights event by event as well as from the Runs Tree
        self.file_eventGenWeightSum = 0.0
        self.file_runsGenWeightSum  = 0.0

        ## Turns out NanoAODTools goes through all the events and may get rid of events which might be corrupted
        self.file_corrupt_events = 0
        self.file_corrupt_reasons = {}

        if self.isMC:
            runsTree = inputFile.Get("Runs")
            if runsTree:
                for r in runsTree:
                    if hasattr(r, "genEventSumw"):
                        self.file_runsGenWeightSum += r.genEventSumw

        print(f"\n Processing {inputFile.GetName()}")
        print(f"Raw events in file: {self.file_raw_events}")
        if self.isMC:
            print(f"RunsTree genEventSumw: {self.file_runsGenWeightSum}")


    def _markCorrupt(self, reason):
        self.file_corrupt_events += 1
        self.file_corrupt_reasons[reason] = (self.file_corrupt_reasons.get(reason, 0) + 1)


    def analyze(self, event):

        if self.isMC:
            try:
                gw = float(event.genWeight)
                self.file_eventGenWeightSum += gw
            except Exception:
                self._markCorrupt("Missing genWeight")
                return False

        try:
            for i, cut in enumerate(self.cut_functions):
                if not cut(event):
                    return False
                self.file_cutCounts[i] += 1
        except Exception as err:
            self._markCorrupt(str(err))
            return False

        return True


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):

        print(f"\n Finalizing {inputFile.GetName()}")
        print(f"Corrupt events in this file: {self.file_corrupt_events}")
        if self.file_corrupt_reasons:
            print("Corrupt for Reasons:")
            for r, n in self.file_corrupt_reasons.items():
                print(f"{n} x {r}")

        if outputFile is None:
            return

        nCuts = len(self.cut_names)

        if self.isMC:
            nBins = nCuts + 4
            h = ROOT.TH1F("cutflow", "cutflow", nBins, 0, nBins)
            h.SetDirectory(outputFile)

            h.GetXaxis().SetBinLabel(1, "Event-level sum of genWeight")
            h.GetXaxis().SetBinLabel(2, "RunsTree genEventSumw")
            h.GetXaxis().SetBinLabel(3, "No Cuts")

            for i, name in enumerate(self.cut_names):
                h.GetXaxis().SetBinLabel(4+i, name)

            corrupt_bin = nCuts + 4
            h.GetXaxis().SetBinLabel(corrupt_bin, "Corrupt Events")

            h.SetBinContent(1, self.file_eventGenWeightSum)
            h.SetBinContent(2, self.file_runsGenWeightSum)
            h.SetBinContent(3, self.file_raw_events)

            for i, v in enumerate(self.file_cutCounts):
                h.SetBinContent(4+i, v)

            h.SetBinContent(corrupt_bin, self.file_corrupt_events)

        else:
            nBins = nCuts + 2
            h = ROOT.TH1F("cutflow", "cutflow", nBins, 0, nBins)
            h.SetDirectory(outputFile)

            h.GetXaxis().SetBinLabel(1, "No Cuts")
            for i, name in enumerate(self.cut_names):
                h.GetXaxis().SetBinLabel(2+i, name)

            corrupt_bin = nCuts + 2
            h.GetXaxis().SetBinLabel(corrupt_bin, "Corrupt Events")

            h.SetBinContent(1, self.file_raw_events)
            for i, v in enumerate(self.file_cutCounts):
                h.SetBinContent(2+i, v)
            h.SetBinContent(corrupt_bin, self.file_corrupt_events)

        outputFile.cd()
        h.Write()
        print("cutflow written.")


    def endJob(self):
        print("\n cutflow information")

        if self.isMC:
            print(f"Event-Level Sum of genWeights : {self.file_eventGenWeightSum}")
            print(f"RunsTree genEventSumw       : {self.file_runsGenWeightSum}")

        print(f"Corrupt events in file      : {self.file_corrupt_events}")
        if self.file_corrupt_reasons:
            print("Corrupt event reasons:")
            for r, n in self.file_corrupt_reasons.items():
                print(f"  {n} x {r}")
        
        print(f"Raw events in file          : {self.file_raw_events}")
        
        print("\nEvents passing each cut:")
        for i, name in enumerate(self.cut_names):
            print(f"  {name}: {self.file_cutCounts[i]}")

        pass



p = PostProcessor(".",
                  inputFiles(),
                  cut=None,
                  modules=[SimpleNanoModule()],
                  provenance=True,
                  fwkJobReport=True,
                  postfix="",
                  haddFileName=None)
                  #jsonInput=runsAndLumis())
p.run()

print("DONE")