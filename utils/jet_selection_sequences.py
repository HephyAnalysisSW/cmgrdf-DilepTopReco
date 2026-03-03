from CMGRDF import Define, ReDefine
from CMGRDF.collectionUtils import DefineSkimmedCollection
from CMGRDF.cms.eras import run2eras, run3eras
from utils.jmeUncertainties import jme_variation_names

from utils.btagWPs import _btagWPs

jet_selection_sequence_nominal = [

    # PU jet ID - loose working point; NB: 2016 nanoAODs have the loose and tight PU jet ID flags switched
    # (001 <-> 1 vs 100 <-> 4), in this case only the 000 case is rejected
    Define("Jet_pass_PU_ID", "(Jet_pt < 50 && Jet_puId >= 1) || Jet_pt > 50", eras=[
           era for era in run2eras if era not in ["2016", "2016APV"]]),
    Define("Jet_pass_PU_ID", "(Jet_pt < 50 && Jet_puId > 0) || Jet_pt > 50", eras=["2016", "2016APV"]),

    # jet cleaning, i.e. jet-lepton overlap removal, based on selected leptons priority to leptons
    # + jet ID. jetID==6 <-> tightLepVeto (see https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVUL#nanoAOD_Flags)
    Define("Jet_isgood", "cleanByDR(Jet_eta, Jet_phi, Lepton_good_eta, Lepton_good_phi) && abs(Jet_eta)<=2.4 && Jet_pt>30 && Jet_jetId==6 && Jet_pass_PU_ID"),

    # genJetIdx is used for calculating PU jet SF
    DefineSkimmedCollection("SelJet", "Jet", mask="Jet_isgood", members=["pt", "eta", "phi", "mass", 'btagDeepFlavB'], optMembers=[
                            'hadronFlavour', 'partonFlavour', 'genJetIdx']),

    [Define( "bTagCut_loose" , "%f"%_btagWPs[f"DeepFlav_UL{era}_L"][1], eras=[era]) for era in run2eras + run3eras],
    [Define( "bTagCut_medium", "%f"%_btagWPs[f"DeepFlav_UL{era}_M"][1], eras=[era]) for era in run2eras + run3eras],
    
    Define("SelJet_bTagged", "SelJet_btagDeepFlavB >= bTagCut_medium"),
    # number of selected jets before b-tagging is Define'd
    # automatically when DefineSkimmedCollection is called
    # this is not the case for b-jets, so we do it below
    Define("nBJets", "Sum(SelJet_bTagged)"),

]

jet_selection_sequences_variations = []

# something smells fishy here with the era definition. TODO: double-check with Sergio
for era in run2eras:
    for var in jme_variation_names[era]:
        for direction in ["up", "down"]:
            
            variation = f"{var}_{direction}"

            if era in ["2016", "2016APV"]:
                jet_selection_sequences_variations += Define(f"Jet_pass_PU_ID__{variation}", f"(Jet_pt__{variation} < 50 && Jet_puId >= 1) || Jet_pt__{variation} > 50", eras=[era], onData=False, onDataDriven=False),

            else:
                jet_selection_sequences_variations += Define(f"Jet_pass_PU_ID__{variation}", f"(Jet_pt__{variation} < 50 && Jet_puId > 0) || Jet_pt__{variation} > 50", eras=[era], onData=False, onDataDriven=False),

            jet_selection_sequences_variations += [

                Define(f"Jet_isgood__{variation}", f"cleanByDR(Jet_eta, Jet_phi, Lepton_good_eta, Lepton_good_phi) && abs(Jet_eta)<=2.4 && Jet_pt__{variation}>30 && Jet_jetId==6 && Jet_pass_PU_ID__{variation}", onMC=True, eras=[era], onData=False, onDataDriven=False),

                DefineSkimmedCollection(f"SelJet__{variation}", "Jet", mask=f"Jet_isgood__{variation}", members=[f"pt__{variation}", "eta", "phi", "mass", 'btagDeepFlavB'], optMembers=[
                                        'hadronFlavour', 'partonFlavour', 'genJetIdx'], onMC=True, onData=False, onDataDriven=False, eras=[era]),

                # to fix the naming conventions as COLLECTION_pt, and avoid having double appending in PT
                ReDefine(f"SelJet__{variation}_pt", f"SelJet__{variation}_pt__{variation}", eras=[era], onData=False, onDataDriven=False, defineIfMissing=True),

                ReDefine(f"SelJet__{variation}_bTagged", f"SelJet__{variation}_btagDeepFlavB >= bTagCut_medium", defineIfMissing=True, onData=False, onDataDriven=False, eras=[era]),
                ReDefine(f"nBJet__{variation}", f"Sum(SelJet__{variation}_bTagged)", defineIfMissing=True, onData=False, onDataDriven=False, eras=[era]),

            ]