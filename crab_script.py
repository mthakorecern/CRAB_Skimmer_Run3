#!/usr/bin/env python3
import os
import ROOT
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
        self.totalRawEntries = 0.0         
        self.sumGenWeights = 0.0
        self.cutCounters = [0.0] * len(self.cut_names)
        self.isMC = False


    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        branchNames = [b.GetName() for b in inputTree.GetListOfBranches()]
        self.isMC = ("genWeight" in branchNames)

        entries = inputTree.GetEntries()
        self.totalRawEntries += entries
        print("\n")
        print(f"Processing file: {inputFile.GetName()}")
        print(f"Entries in this file: {entries}")
        print(f"Accumulated total entries so far: {self.totalRawEntries}")  

        if not hasattr(self, "cutflow"):
            nCuts = len(self.cut_names)
            if self.isMC:
                nBins = nCuts + 2
                self.cutflow = ROOT.TH1F("cutflow", "cutflow", nBins, 0, nBins)
                self.cutflow.GetXaxis().SetBinLabel(1, "Sum of genWeights")
                self.cutflow.GetXaxis().SetBinLabel(2, "No Cuts")
                for i,n in enumerate(self.cut_names):
                    self.cutflow.GetXaxis().SetBinLabel(3+i, n)

            else:
                nBins = nCuts + 1
                self.cutflow = ROOT.TH1F("cutflow", "cutflow", nBins, 0, nBins)
                self.cutflow.GetXaxis().SetBinLabel(1, "No Cuts")
                for i,n in enumerate(self.cut_names):
                    self.cutflow.GetXaxis().SetBinLabel(2+i, n)



    def analyze(self, event):

        if self.isMC:
            try: w = float(event.genWeight)
            except: w = 1.0
            self.sumGenWeights += w
        else:
            w = 1.0

        for i, cut in enumerate(self.cut_functions):
            if not cut(event):
                return False
            self.cutCounters[i] += w
        return True


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print("\n")
        print("Finalizing job")
        print(f"Total raw entries across all files = {self.totalRawEntries}")
        print("Cutflow:")

        if self.isMC:
            print(f"Sum of genWeights = {self.sumGenWeights}")
            print(f"No Cuts (raw entries)= {self.totalRawEntries}")
        else:
            print(f"No Cuts (raw entries)= {self.totalRawEntries}")

        for i, name in enumerate(self.cut_names):
            print(f"After {name:35s} = {self.cutCounters[i]}")

        # Number of events written
        try:
            outtree = wrappedOutputTree.tree
            written = outtree.GetEntries()
        except:
            written = -1

        print(f"Events written to skimmed output = {written}")

        if self.isMC:
            self.cutflow.SetBinContent(1, self.sumGenWeights)
            self.cutflow.SetBinContent(2, self.totalRawEntries)
            for i,v in enumerate(self.cutCounters):
                self.cutflow.SetBinContent(3+i, v)
        else:
            self.cutflow.SetBinContent(1, self.totalRawEntries)
            for i,v in enumerate(self.cutCounters):
                self.cutflow.SetBinContent(2+i, v)

        outputFile.cd()
        self.cutflow.Write()



p = PostProcessor(".",
                  inputFiles(),
                  cut=None,
                  modules=[SimpleNanoModule()],
                  provenance=True,
                  fwkJobReport=True,
                  postfix="",
                  haddFileName="tree.root",
                  jsonInput=runsAndLumis())
p.run()

print("DONE")