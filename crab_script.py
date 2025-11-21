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
        self.sumGenWeights = 0.0    
        self.cutCounters = [0.0] * len(self.cut_names)
        self.rawEntries = 0
        self.isMC = False


    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.rawEntries = inputTree.GetEntries()
        branchNames = [b.GetName() for b in inputTree.GetListOfBranches()]
        self.isMC = ("genWeight" in branchNames)

        nCuts = len(self.cut_names)

        if self.isMC:
            print("Skimming MC")
            nBins = nCuts + 2
            self.cutflow = ROOT.TH1F("cutflow", "cutflow", nBins, 0, nBins)

            self.cutflow.GetXaxis().SetBinLabel(1, "Sum of genWeights")
            self.cutflow.GetXaxis().SetBinLabel(2, "No Cuts")
            for i, name in enumerate(self.cut_names):
                self.cutflow.GetXaxis().SetBinLabel(3 + i, name)
        else:
            print("Skimming Data")
            nBins = nCuts + 1
            self.cutflow = ROOT.TH1F("cutflow", "cutflow", nBins, 0, nBins)

            self.cutflow.GetXaxis().SetBinLabel(1, "No Cuts")
            for i, name in enumerate(self.cut_names):
                self.cutflow.GetXaxis().SetBinLabel(2 + i, name)


    def analyze(self, event):

        if self.isMC:
            try:
                genw = float(event.genWeight)
            except Exception:
                genw = 1.0
            self.sumGenWeights += genw

        event_count_weight = 1.0

        for i, cut in enumerate(self.cut_functions):
            if not cut(event):
                return False
            self.cutCounters[i] += event_count_weight

        return True


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print("Skimming is completed. Now filling cutflow histogram bins")

        if self.isMC:
            self.cutflow.SetBinContent(1, self.sumGenWeights)
            self.cutflow.SetBinContent(2, float(self.rawEntries))

            for i, v in enumerate(self.cutCounters):
                self.cutflow.SetBinContent(3 + i, v)
        else:
            self.cutflow.SetBinContent(1, float(self.rawEntries))
            for i, v in enumerate(self.cutCounters):
                self.cutflow.SetBinContent(2 + i, v)

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