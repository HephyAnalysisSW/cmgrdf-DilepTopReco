
import ROOT

# utilities
import yaml  # stores triggers for each year
from CMGRDF import *
from CMGRDF.cms.EGammaSFs import ElectronSFDefine
from CMGRDF.cms.eras import *
from CMGRDF.cms.jmeUncertainties import *
from CMGRDF.cms.MuonSFs import *
from CMGRDF.cms.puReweighting import *
from CMGRDF.collectionUtils import *  # several very nice utility functions
from CMGRDF.skimFilters import TriggerBitFilter

from utils.jmeUncertainties import jme_sequences, jme_sequences_after
from utils.jet_selection_sequences import jet_selection_sequence_nominal, jet_selection_sequences_variations_MC

from utils.top_reco_sequences import p4_reconstruction_sequences, top_reconstruction_sequence_nominal, top_reconstruction_sequences_jme_variations

from utils.btagSF import btagsf_sequences

# to allow setting varied top reco calls
import sys
sys.setrecursionlimit(10**6)

import argparse as ap

import os

# Source.useDefinePerSample = False

with open("data/list_triggers.yaml", "r") as f:
    dict_triggers = yaml.safe_load(f)

# same triggers
dict_triggers['2016APV'] = dict_triggers['2016']

# putting here all of the triggers, to perform a first skimming of the events
trigger_sequences_data = [TriggerBitFilter(dict_triggers[era]["ee"] + dict_triggers[era]["mumu"] + dict_triggers[era]
                                           ["emu"], name=f"trigger_{era}", eras=[era], onData=True, onDataDriven=True, onMC=False) for era in run2eras]

# not removing MC events if they fired the trigger, adding instead a flag the OR of all triggers
trigger_OR_flag_sequences_MC = [Define("pass_trigger_OR_MC", " || ".join(dict_triggers[era]["ee"] + dict_triggers[era]["mumu"] +
                                                                         dict_triggers[era]["emu"]), eras=[era], onMC=True, onData=False, onDataDriven=False) for era in run2eras]


list_common_filters = ["goodVertices", "globalSuperTightHalo2016Filter", "HBHENoiseFilter", "HBHENoiseIsoFilter",
                       "EcalDeadCellTriggerPrimitiveFilter", "BadPFMuonFilter", "BadPFMuonDzFilter", "eeBadScFilter", "hfNoisyHitsFilter"]
list_filters_17_18 = ["ecalBadCalibFilter"]

# Top reconstruction
AddHeader("toprecofunctions.h", "./TopReco")
f_hists_path = "./TopReco/kinreco.root"

if not os.path.exists(f_hists_path):
    raise FileNotFoundError(f_hists_path)

f_hists = ROOT.TFile.Open(f_hists_path)
load_hists = '''
    auto h_mlb = mlb; h_mlb->SetDirectory(0);
    auto h_energyfj = energyfj; h_energyfj->SetDirectory(0);
    auto h_alphafj = alphaj; h_alphafj->SetDirectory(0);
    auto h_energyfl = energyfl; h_energyfl->SetDirectory(0);
    auto h_alphafl = alphal; h_alphafl->SetDirectory(0);
'''
load_reco = '''
    TTDilepReconstruction topreco = TTDilepReconstruction(100);
    topreco.SetH_MLB(h_mlb);
    topreco.SetH_JetEnergy(h_energyfj);
    topreco.SetH_JetAngle(h_alphafj);
    topreco.SetH_LepEnergy(h_energyfl);
    topreco.SetH_LepAngle(h_alphafl);
'''
ProcessLine(load_hists+load_reco)
f_hists.Close()


# pileup reweighting SF and uncertainties for all eras
pileuprw_SF_sequences = [PileupSFDefine(era=era, eras=[era]) for era in run2eras]

# muon SF sequences and uncertainties for all eras
muonSF_sequences = [MuonIDIsoSFDefine("Tight", "Tight", era, denId="TrackerMuons", denIso="TightIDandIPCut", eras=[era]) for era in run2eras]
# electron SF sequences and uncertainties for all eras
# electron ID already includes Isolation cuts
electronSF_sequences = [ElectronSFDefine("Tight", era, eras=[era]) for era in run2eras]

# object reconstruction and event selection
objreco_cuts = Flow("objreco_cuts",

                    # trigger_sequences_data,
                    # MET filters, see https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2#UL_data
                    # commented out until we test Cut again (crashing before)
                    # Cut("filters_common"," && ".join([f"Flag_{flagname}" for flagname in list_common_filters]), onData=True, onDataDriven=True, onMC=False),
                    # Cut("additional_filter_17_18", "Flag_ecalBadCalibFilter", eras=["2017","2018"], onData=True, onDataDriven=True, onMC=False),

                    trigger_OR_flag_sequences_MC,

                    # not changing the name of electron and muon SF variations in the cmgrdf-prototype code
                    # to not have to track too many changes there
                    # the renaming is done when building the Lepton_good collections

                    # Muon_tightID includes the criteria that muon is a PF candidate, pfIsoID==4 <-> Tight isolation
                    muonSF_sequences,
                    DefineSkimmedCollection("Muon_good", "Muon", cut="abs(Muon_eta) < 2.4 && Muon_pt > 20 && Muon_tightId && Muon_pfIsoId >= 4", members=[
                                            "pt", "eta", "phi", "mass", "charge", "pdgId", "SF_TightId_TightIso","SF_TightId_TightIso_CMS_eff_m_up","SF_TightId_TightIso_CMS_eff_m_down"]),



                    electronSF_sequences,
                    # Electron_cutBased==4 includes relative isolation cuts
                    DefineSkimmedCollection("Electron_good", "Electron", cut="!(abs(Electron_eta+Electron_deltaEtaSC)>1.442 && abs(Electron_eta+Electron_deltaEtaSC)<1.556) "
                                            "&& abs(Electron_eta)<2.4 && Electron_pt > 20 && Electron_cutBased==4 &&"
                                            "((Electron_eta+Electron_deltaEtaSC < 1.479 && abs(Electron_dz) < 0.10 && abs(Electron_dxy) < 0.05) || "
                                            " (Electron_eta+Electron_deltaEtaSC > 1.479 && abs(Electron_dz) < 0.20 && abs(Electron_dxy) < 0.10))", members=["pt", "eta", "phi", "mass", "charge", "pdgId", "SF_Tight","SF_Tight_CMS_eff_e_up","SF_Tight_CMS_eff_e_down"]),

                    # concatenating the branches for the leptons
                    Define("Lepton_good_pt_unsorted", "ROOT::VecOps::Concatenate(Muon_good_pt,Electron_good_pt)"),
                    Define("Lepton_good_eta_unsorted", "ROOT::VecOps::Concatenate(Muon_good_eta,Electron_good_eta)"),
                    Define("Lepton_good_phi_unsorted", "ROOT::VecOps::Concatenate(Muon_good_phi,Electron_good_phi)"),
                    Define("Lepton_good_mass_unsorted", "ROOT::VecOps::Concatenate(Muon_good_mass,Electron_good_mass)"),
                    Define("Lepton_good_charge_unsorted", "ROOT::VecOps::Concatenate(Muon_good_charge,Electron_good_charge)"),
                    Define("Lepton_good_pdgId_unsorted", "ROOT::VecOps::Concatenate(Muon_good_pdgId,Electron_good_pdgId)"),
                    Define("Lepton_good_SF_unsorted", "ROOT::VecOps::Concatenate(Muon_good_SF_TightId_TightIso,Electron_good_SF_Tight)"),
                    Define("Lepton_good_SFUp_unsorted", "ROOT::VecOps::Concatenate(Muon_good_SF_TightId_TightIso_CMS_eff_m_up,Electron_good_SF_Tight_CMS_eff_e_up)"),
                    Define("Lepton_good_SFDn_unsorted", "ROOT::VecOps::Concatenate(Muon_good_SF_TightId_TightIso_CMS_eff_m_down,Electron_good_SF_Tight_CMS_eff_e_down)"),

                    # ordering relevant lepton branches by pT - highest to lowest
                    Define("Lepton_good_pt_sortindex", "ROOT::VecOps::Reverse(ROOT::VecOps::Argsort(Lepton_good_pt_unsorted))"),
                    Define("Lepton_good_pt", "ROOT::VecOps::Take(Lepton_good_pt_unsorted,Lepton_good_pt_sortindex)"),
                    Define("Lepton_good_eta", "ROOT::VecOps::Take(Lepton_good_eta_unsorted,Lepton_good_pt_sortindex)"),
                    Define("Lepton_good_phi", "ROOT::VecOps::Take(Lepton_good_phi_unsorted,Lepton_good_pt_sortindex)"),
                    Define("Lepton_good_mass", "ROOT::VecOps::Take(Lepton_good_mass_unsorted,Lepton_good_pt_sortindex)"),
                    Define("Lepton_good_charge", "ROOT::VecOps::Take(Lepton_good_charge_unsorted,Lepton_good_pt_sortindex)"),
                    Define("Lepton_good_pdgId", "ROOT::VecOps::Take(Lepton_good_pdgId_unsorted,Lepton_good_pt_sortindex)"),
                    Define("Lepton_good_SF", "ROOT::VecOps::Take(Lepton_good_SF_unsorted,Lepton_good_pt_sortindex)"),
                    Define("Lepton_good_SFUp", "ROOT::VecOps::Take(Lepton_good_SFUp_unsorted,Lepton_good_pt_sortindex)"),
                    Define("Lepton_good_SFDn", "ROOT::VecOps::Take(Lepton_good_SFDn_unsorted,Lepton_good_pt_sortindex)"),

                    Define("nLepton_good", "Lepton_good_pt.size()"),
                    
                    # lepton quantities in flat format with the protection for variable-sized inputs
                    Define("lep0_pt", "( nLepton_good > 0 ) ? Lepton_good_pt.at(0) : std::nan(\"\") "),
                    Define("lep1_pt", "( nLepton_good > 1 ) ? Lepton_good_pt.at(1) : std::nan(\"\") "),

                    Define("lep0_eta", "( nLepton_good > 0 ) ? Lepton_good_eta.at(0) : std::nan(\"\") "),
                    Define("lep1_eta", "( nLepton_good > 1 ) ? Lepton_good_eta.at(1) : std::nan(\"\") "),

                    Define("lep0_phi", "( nLepton_good > 0 ) ? Lepton_good_phi.at(0) : std::nan(\"\") "),
                    Define("lep1_phi", "( nLepton_good > 1 ) ? Lepton_good_phi.at(1) : std::nan(\"\") "),

                    Define("lep0_mass", "( nLepton_good > 0 ) ? Lepton_good_mass.at(0) : std::nan(\"\") "),
                    Define("lep1_mass", "( nLepton_good > 1 ) ? Lepton_good_mass.at(1) : std::nan(\"\") "),

                    Define("lep0_charge", "( nLepton_good > 0 ) ? Lepton_good_charge.at(0) : std::nan(\"\") "),
                    Define("lep1_charge", "( nLepton_good > 1 ) ? Lepton_good_charge.at(1) : std::nan(\"\") "),

                    Define("lep0_pdgId", "( nLepton_good > 0 ) ? Lepton_good_pdgId.at(0) : std::nan(\"\") "),
                    Define("lep1_pdgId", "( nLepton_good > 1 ) ? Lepton_good_pdgId.at(1) : std::nan(\"\") "),

                    Define("lep0_SF", "( nLepton_good > 0 ) ? Lepton_good_SF.at(0) : std::nan(\"\") "),
                    Define("lep1_SF", "( nLepton_good > 1 ) ? Lepton_good_SF.at(1) : std::nan(\"\") "),

                    Define("lep0_SFUp", "( nLepton_good > 0 ) ? Lepton_good_SFUp.at(0) : std::nan(\"\") "),
                    Define("lep1_SFUp", "( nLepton_good > 1 ) ? Lepton_good_SFUp.at(1) : std::nan(\"\") "),

                    Define("lep0_SFDn", "( nLepton_good > 0 ) ? Lepton_good_SFDn.at(0) : std::nan(\"\") "),
                    Define("lep1_SFDn", "( nLepton_good > 1 ) ? Lepton_good_SFDn.at(1) : std::nan(\"\") "),

                    # to get negative lepton and positive antilepton
                    Define("Lepton_idx", "( nLepton_good >=2 ) ? (Lepton_good_charge[0] < 0 ? 0 : 1) : std::nan(\"\")"),
                    Define("Antilepton_idx", "( nLepton_good >=2 ) ? (Lepton_good_charge[0] > 0 ? 0 : 1) : std::nan(\"\")"),


                    DefineP4("Lepton_good"),
                    Define("Dilepton_good_p4", "( nLepton_good >= 2 ) ? Lepton_good_p4[0]+Lepton_good_p4[1] : ROOT::Math::PtEtaPhiMVector(std::nan(\"\"),std::nan(\"\"),std::nan(\"\"),std::nan(\"\"))"),

                    # no need to add test for nLepton_good >= 2
                    # since nan come for free from the test above
                    Define("dilep_pt", "Dilepton_good_p4.Pt()"),
                    Define("dilep_eta", "Dilepton_good_p4.Eta()"),
                    Define("dilep_phi", "Dilepton_good_p4.Phi()"),
                    Define("dilep_mass", "Dilepton_good_p4.M()"),

                    # Jet/MET corrections + uncertainties
                    jme_sequences,

                    # jet and b-jet selection
                    jet_selection_sequence_nominal,
                    jet_selection_sequences_variations_MC,

                    # PU ID jet weight
                    jme_sequences_after,

                    ############################ Top reconstruction #################################
                    
                    # reconstructing 4-vectors of selected jets for nominal and jet/MET variations
                    p4_reconstruction_sequences,

                    # sqrt(s), used for x reconstruction
                    Define("sqrts", "13000", eras=run2eras),
                    Define("sqrts", "13600", eras=run3eras),

                    # nominal and varied top reconstruction
                    top_reconstruction_sequence_nominal,
                    top_reconstruction_sequences_jme_variations,

                    # pileup reweighting
                    pileuprw_SF_sequences,

                    # b-tagging SF
                    btagsf_sequences,

                    )

if __name__ == "__main__":

    # get Processor object with some parameters already set from command line arguments
    # see CMGRDF.cmdline for a description of the arguments
    from CMGRDF.cmdline import processorFromCommandLineArgs
    maker, args = processorFromCommandLineArgs()


    # normalizes sample based on lumi for given era, cross-section
    # calculating and caching sum of gen weights based on given genWeightName
    # normalized weight is "mcSampleWeight"
    data = [Process(f"TTLep_pow", MCSample(f"TTLep_pow",
                                           f"/afs/cern.ch/work/r/rcoelhob/work/top_framework/TTLep_pow_2018_skimmed_NanoAODv9_120k.root",
                                           eras=["2018"], genWeightName = "Generator_weight", xsec = 831.76*((3*0.108)**2)),
                    signal=True)]

    target_snapshot = Snapshot("./test.root",
                               columnSel=['#new', 'Generator_.*', 'GenMET.*', 'GenPart.*', 'GenJet.*', 'LHE.*','PSWeight.*', "SelJet.*genJetIdx","L1PreFiringWeight.*","genWeight", "event", "run", "luminosityBlock"],
                               columnVeto=['ak4JetVars.*', 'MET_T1.*', 'TopRecoSol.*', '.*unsorted', ".*p4.*", "Muon.*", "Electron.*", "CorrT1METJet.*", "Rho.*", "SelJet__CMS.*__CMS.*"])

    maker.book(data, lumis, objreco_cuts, [target_snapshot], eras=["2018"],withUncertainties = True)
    
    snapshot_report = maker.runSnapshots()
    snapshotReport = [f"Snapshoted at {target_snapshot.filename}"]

    for key, snap in snapshot_report:
        snapshotReport.append("%-10s  %-20s : %10u entries  %9.3f GB   %s" % (key.process, key.sample, snap.entries, snap.size / (1024.**3), snap.fname))
    print("\n".join(snapshotReport))

    with open(f"./snapReport.txt", "w") as snapshotReportFile:
        snapshotReportFile.write("\n".join(snapshotReport))
