from CMGRDF.flow import Define
from CMGRDF.collectionUtils import DefineP4
from CMGRDF.cms.eras import run2eras
from utils.jmeUncertainties import jme_variation_names_MC, met_variation_names_MC

p4_reconstruction_sequences = [
    # make 4-momenta of all the necessary objects
    DefineP4("SelJet"),
]

for era in run2eras:
    for var in jme_variation_names_MC[era]:
        for direction in ["up", "down"]:
            
            variation = f"{var}_{direction}"

            p4_reconstruction_sequences.append(DefineP4(f"SelJet__{variation}", eras=[era]))

top_reconstruction_sequence_nominal = [

    # not doing b-jets separately because Ang implemented top reconstruction using as input all of the jets and the column with the b-tagged bool
    # converting between the types of ROOT:Math::()Vector because cmgrdf and Ang's code use different implementations
    # and somehow there's no available conversion between the two ?
    # default TopRecoSolution is tr_isvalid = false and everything else set to C++ nan
    # Top reconstruction code requires an ordering to lepton and antilepton four-vectors
    Define("TopRecoSol", "(nLepton_good >= 2) ? topreco_solution(topreco, ROOT::Math::PxPyPzEVector(Lepton_good_p4[Lepton_idx]), ROOT::Math::PxPyPzEVector(Lepton_good_p4[Antilepton_idx]),"
           "SelJet_p4, SelJet_bTagged, MET_pt, MET_phi) : std::pair<TopRecoSolution,std::pair<size_t,size_t>> {TopRecoSolution(),{0,0}}"),

    # flag to know events where top reconstruction failed, instead of rejecting them outright
    Define("tr_isvalid", "TopRecoSol.first.valid"),

    # NB: there's no guarantee from Top reco code that Top_pt is really of the Top quark (and not the antitop)
    # one could enforce that in that code or do order them per pT - does it matter ?
    Define("tr_Top_pt", "TopRecoSol.first.top.Pt()"),
    Define("tr_Top_eta", "TopRecoSol.first.top.Eta()"),
    Define("tr_Top_phi", "TopRecoSol.first.top.Phi()"),
    Define("tr_Top_mass", "TopRecoSol.first.top.M()"),
    Define("tr_Wp_pt", "TopRecoSol.first.Wp.Pt()"),
    Define("tr_Wp_eta", "TopRecoSol.first.Wp.Eta()"),
    Define("tr_Wp_phi", "TopRecoSol.first.Wp.Phi()"),
    Define("tr_Wp_mass", "TopRecoSol.first.Wp.M()"),
    Define("tr_b_pt", "TopRecoSol.first.b.Pt()"),
    Define("tr_b_eta", "TopRecoSol.first.b.Eta()"),
    Define("tr_b_phi", "TopRecoSol.first.b.Phi()"),
    Define("tr_b_mass", "TopRecoSol.first.b.M()"),
    Define("tr_antilep_pt", "TopRecoSol.first.antilep.Pt()"),
    Define("tr_antilep_eta", "TopRecoSol.first.antilep.Eta()"),
    Define("tr_antilep_phi", "TopRecoSol.first.antilep.Phi()"),
    Define("tr_antilep_mass", "TopRecoSol.first.antilep.M()"),
    Define("tr_nu_pt", "TopRecoSol.first.nu.Pt()"),
    Define("tr_nu_eta", "TopRecoSol.first.nu.Eta()"),
    Define("tr_nu_phi", "TopRecoSol.first.nu.Phi()"),
    Define("tr_nu_mass", "TopRecoSol.first.nu.M()"),
    Define("tr_AntiTop_pt", "TopRecoSol.first.antitop.Pt()"),
    Define("tr_AntiTop_eta", "TopRecoSol.first.antitop.Eta()"),
    Define("tr_AntiTop_phi", "TopRecoSol.first.antitop.Phi()"),
    Define("tr_AntiTop_mass", "TopRecoSol.first.antitop.M()"),
    Define("tr_Wm_pt", "TopRecoSol.first.Wm.Pt()"),
    Define("tr_Wm_eta", "TopRecoSol.first.Wm.Eta()"),
    Define("tr_Wm_phi", "TopRecoSol.first.Wm.Phi()"),
    Define("tr_Wm_mass", "TopRecoSol.first.Wm.M()"),
    Define("tr_antib_pt", "TopRecoSol.first.antib.Pt()"),
    Define("tr_antib_eta", "TopRecoSol.first.antib.Eta()"),
    Define("tr_antib_phi", "TopRecoSol.first.antib.Phi()"),
    Define("tr_antib_mass", "TopRecoSol.first.antib.M()"),
    Define("tr_lep_pt", "TopRecoSol.first.lep.Pt()"),
    Define("tr_lep_eta", "TopRecoSol.first.lep.Eta()"),
    Define("tr_lep_phi", "TopRecoSol.first.lep.Phi()"),
    Define("tr_lep_mass", "TopRecoSol.first.lep.M()"),
    Define("tr_antinu_pt", "TopRecoSol.first.antinu.Pt()"),
    Define("tr_antinu_eta", "TopRecoSol.first.antinu.Eta()"),
    Define("tr_antinu_phi", "TopRecoSol.first.antinu.Phi()"),
    Define("tr_antinu_mass", "TopRecoSol.first.antinu.M()"),

    # aux functions defined in include/functions.h
    Define("tr_ttbar_p4", "ROOT::Math::PtEtaPhiMVector(tr_Top_pt, tr_Top_eta, tr_Top_phi, tr_Top_mass) +"
           "ROOT::Math::PtEtaPhiMVector(tr_AntiTop_pt, tr_AntiTop_eta, tr_AntiTop_phi, tr_AntiTop_mass)"),

    Define("tr_ttbar_pt", "tr_ttbar_p4.Pt()"),
    Define("tr_ttbar_eta", "tr_ttbar_p4.Eta()"),
    Define("tr_ttbar_phi", "tr_ttbar_p4.Phi()"),
    Define("tr_ttbar_mass", "tr_ttbar_p4.M()"),

]

# keeping it out to avoid issues with f-string formatting
default_top_reco_string = "std::pair<TopRecoSolution,std::pair<size_t,size_t>> {TopRecoSolution(),{0,0}}"

top_reconstruction_sequences_jme_variations = []

# warning for maximum recursion depth exceeded ?
for era in run2eras:
    for var in jme_variation_names_MC[era]:
        for direction in ["up", "down"]:
            
            variation = f"{var}_{direction}"

            top_reconstruction_sequences_jme_variations += [
                
                Define(f"TopRecoSol__{variation}", "(nLepton_good >= 2) ? topreco_solution(topreco, ROOT::Math::PxPyPzEVector(Lepton_good_p4[Lepton_idx]), ROOT::Math::PxPyPzEVector(Lepton_good_p4[Antilepton_idx]),"
                    f"SelJet__{variation}_p4, SelJet__{variation}_bTagged, MET_pt__{variation}, MET_phi__{variation}) : {default_top_reco_string}", eras=[era]),

                Define(f"tr_isvalid__{variation}", f"TopRecoSol__{variation}.first.valid", eras=[era]),

                Define(f"tr_Top_pt__{variation}", f"TopRecoSol__{variation}.first.top.Pt()", eras=[era]),
                Define(f"tr_Top_eta__{variation}", f"TopRecoSol__{variation}.first.top.Eta()", eras=[era]),
                Define(f"tr_Top_phi__{variation}", f"TopRecoSol__{variation}.first.top.Phi()", eras=[era]),
                Define(f"tr_Top_mass__{variation}", f"TopRecoSol__{variation}.first.top.M()", eras=[era]),
                Define(f"tr_Wp_pt__{variation}", f"TopRecoSol__{variation}.first.Wp.Pt()", eras=[era]),
                Define(f"tr_Wp_eta__{variation}", f"TopRecoSol__{variation}.first.Wp.Eta()", eras=[era]),
                Define(f"tr_Wp_phi__{variation}", f"TopRecoSol__{variation}.first.Wp.Phi()", eras=[era]),
                Define(f"tr_Wp_mass__{variation}", f"TopRecoSol__{variation}.first.Wp.M()", eras=[era]),
                Define(f"tr_b_pt__{variation}", f"TopRecoSol__{variation}.first.b.Pt()", eras=[era]),
                Define(f"tr_b_eta__{variation}", f"TopRecoSol__{variation}.first.b.Eta()", eras=[era]),
                Define(f"tr_b_phi__{variation}", f"TopRecoSol__{variation}.first.b.Phi()", eras=[era]),
                Define(f"tr_b_mass__{variation}", f"TopRecoSol__{variation}.first.b.M()", eras=[era]),
                Define(f"tr_antilep_pt__{variation}", f"TopRecoSol__{variation}.first.antilep.Pt()", eras=[era]),
                Define(f"tr_antilep_eta__{variation}", f"TopRecoSol__{variation}.first.antilep.Eta()", eras=[era]),
                Define(f"tr_antilep_phi__{variation}", f"TopRecoSol__{variation}.first.antilep.Phi()", eras=[era]),
                Define(f"tr_antilep_mass__{variation}", f"TopRecoSol__{variation}.first.antilep.M()", eras=[era]),
                Define(f"tr_nu_pt__{variation}", f"TopRecoSol__{variation}.first.nu.Pt()", eras=[era]),
                Define(f"tr_nu_eta__{variation}", f"TopRecoSol__{variation}.first.nu.Eta()", eras=[era]),
                Define(f"tr_nu_phi__{variation}", f"TopRecoSol__{variation}.first.nu.Phi()", eras=[era]),
                Define(f"tr_nu_mass__{variation}", f"TopRecoSol__{variation}.first.nu.M()", eras=[era]),
                Define(f"tr_AntiTop_pt__{variation}", f"TopRecoSol__{variation}.first.antitop.Pt()", eras=[era]),
                Define(f"tr_AntiTop_eta__{variation}", f"TopRecoSol__{variation}.first.antitop.Eta()", eras=[era]),
                Define(f"tr_AntiTop_phi__{variation}", f"TopRecoSol__{variation}.first.antitop.Phi()", eras=[era]),
                Define(f"tr_AntiTop_mass__{variation}", f"TopRecoSol__{variation}.first.antitop.M()", eras=[era]),
                Define(f"tr_Wm_pt__{variation}", f"TopRecoSol__{variation}.first.Wm.Pt()", eras=[era]),
                Define(f"tr_Wm_eta__{variation}", f"TopRecoSol__{variation}.first.Wm.Eta()", eras=[era]),
                Define(f"tr_Wm_phi__{variation}", f"TopRecoSol__{variation}.first.Wm.Phi()", eras=[era]),
                Define(f"tr_Wm_mass__{variation}", f"TopRecoSol__{variation}.first.Wm.M()", eras=[era]),
                Define(f"tr_antib_pt__{variation}", f"TopRecoSol__{variation}.first.antib.Pt()", eras=[era]),
                Define(f"tr_antib_eta__{variation}", f"TopRecoSol__{variation}.first.antib.Eta()", eras=[era]),
                Define(f"tr_antib_phi__{variation}", f"TopRecoSol__{variation}.first.antib.Phi()", eras=[era]),
                Define(f"tr_antib_mass__{variation}", f"TopRecoSol__{variation}.first.antib.M()", eras=[era]),
                Define(f"tr_lep_pt__{variation}", f"TopRecoSol__{variation}.first.lep.Pt()", eras=[era]),
                Define(f"tr_lep_eta__{variation}", f"TopRecoSol__{variation}.first.lep.Eta()", eras=[era]),
                Define(f"tr_lep_phi__{variation}", f"TopRecoSol__{variation}.first.lep.Phi()", eras=[era]),
                Define(f"tr_lep_mass__{variation}", f"TopRecoSol__{variation}.first.lep.M()", eras=[era]),
                Define(f"tr_antinu_pt__{variation}", f"TopRecoSol__{variation}.first.antinu.Pt()", eras=[era]),
                Define(f"tr_antinu_eta__{variation}", f"TopRecoSol__{variation}.first.antinu.Eta()", eras=[era]),
                Define(f"tr_antinu_phi__{variation}", f"TopRecoSol__{variation}.first.antinu.Phi()", eras=[era]),
                Define(f"tr_antinu_mass__{variation}", f"TopRecoSol__{variation}.first.antinu.M()", eras=[era]),

                Define(f"tr_ttbar_p4__{variation}", f"ROOT::Math::PtEtaPhiMVector(tr_Top_pt__{variation}, tr_Top_eta__{variation}, tr_Top_phi__{variation}, tr_Top_mass__{variation}) +"
                    f"ROOT::Math::PtEtaPhiMVector(tr_AntiTop_pt__{variation}, tr_AntiTop_eta__{variation}, tr_AntiTop_phi__{variation}, tr_AntiTop_mass__{variation})", eras=[era]),

                Define(f"tr_ttbar_pt__{variation}", f"tr_ttbar_p4__{variation}.Pt()", eras=[era]),
                Define(f"tr_ttbar_eta__{variation}", f"tr_ttbar_p4__{variation}.Eta()", eras=[era]),
                Define(f"tr_ttbar_phi__{variation}", f"tr_ttbar_p4__{variation}.Phi()", eras=[era]),
                Define(f"tr_ttbar_mass__{variation}", f"tr_ttbar_p4__{variation}.M()", eras=[era]),

            ]

for era in run2eras:
    # unclustered MET variations for now, can add more later
    for var in met_variation_names_MC[era]:
        for direction in ["up", "down"]:
            
            variation = f"{var}_{direction}"

            top_reconstruction_sequences_jme_variations += [
            
                Define(f"TopRecoSol__{variation}", "(nLepton_good >= 2) ? topreco_solution(topreco, ROOT::Math::PxPyPzEVector(Lepton_good_p4[Lepton_idx]), ROOT::Math::PxPyPzEVector(Lepton_good_p4[Antilepton_idx]),"
                    f"SelJet_p4, SelJet_bTagged, MET_pt__{variation}, MET_phi__{variation}) : {default_top_reco_string}", eras=[era]),

                Define(f"tr_isvalid__{variation}", f"TopRecoSol__{variation}.first.valid", eras=[era]),

                Define(f"tr_Top_pt__{variation}", f"TopRecoSol__{variation}.first.top.Pt()", eras=[era]),
                Define(f"tr_Top_eta__{variation}", f"TopRecoSol__{variation}.first.top.Eta()", eras=[era]),
                Define(f"tr_Top_phi__{variation}", f"TopRecoSol__{variation}.first.top.Phi()", eras=[era]),
                Define(f"tr_Top_mass__{variation}", f"TopRecoSol__{variation}.first.top.M()", eras=[era]),
                Define(f"tr_Wp_pt__{variation}", f"TopRecoSol__{variation}.first.Wp.Pt()", eras=[era]),
                Define(f"tr_Wp_eta__{variation}", f"TopRecoSol__{variation}.first.Wp.Eta()", eras=[era]),
                Define(f"tr_Wp_phi__{variation}", f"TopRecoSol__{variation}.first.Wp.Phi()", eras=[era]),
                Define(f"tr_Wp_mass__{variation}", f"TopRecoSol__{variation}.first.Wp.M()", eras=[era]),
                Define(f"tr_b_pt__{variation}", f"TopRecoSol__{variation}.first.b.Pt()", eras=[era]),
                Define(f"tr_b_eta__{variation}", f"TopRecoSol__{variation}.first.b.Eta()", eras=[era]),
                Define(f"tr_b_phi__{variation}", f"TopRecoSol__{variation}.first.b.Phi()", eras=[era]),
                Define(f"tr_b_mass__{variation}", f"TopRecoSol__{variation}.first.b.M()", eras=[era]),
                Define(f"tr_antilep_pt__{variation}", f"TopRecoSol__{variation}.first.antilep.Pt()", eras=[era]),
                Define(f"tr_antilep_eta__{variation}", f"TopRecoSol__{variation}.first.antilep.Eta()", eras=[era]),
                Define(f"tr_antilep_phi__{variation}", f"TopRecoSol__{variation}.first.antilep.Phi()", eras=[era]),
                Define(f"tr_antilep_mass__{variation}", f"TopRecoSol__{variation}.first.antilep.M()", eras=[era]),
                Define(f"tr_nu_pt__{variation}", f"TopRecoSol__{variation}.first.nu.Pt()", eras=[era]),
                Define(f"tr_nu_eta__{variation}", f"TopRecoSol__{variation}.first.nu.Eta()", eras=[era]),
                Define(f"tr_nu_phi__{variation}", f"TopRecoSol__{variation}.first.nu.Phi()", eras=[era]),
                Define(f"tr_nu_mass__{variation}", f"TopRecoSol__{variation}.first.nu.M()", eras=[era]),
                Define(f"tr_AntiTop_pt__{variation}", f"TopRecoSol__{variation}.first.antitop.Pt()", eras=[era]),
                Define(f"tr_AntiTop_eta__{variation}", f"TopRecoSol__{variation}.first.antitop.Eta()", eras=[era]),
                Define(f"tr_AntiTop_phi__{variation}", f"TopRecoSol__{variation}.first.antitop.Phi()", eras=[era]),
                Define(f"tr_AntiTop_mass__{variation}", f"TopRecoSol__{variation}.first.antitop.M()", eras=[era]),
                Define(f"tr_Wm_pt__{variation}", f"TopRecoSol__{variation}.first.Wm.Pt()", eras=[era]),
                Define(f"tr_Wm_eta__{variation}", f"TopRecoSol__{variation}.first.Wm.Eta()", eras=[era]),
                Define(f"tr_Wm_phi__{variation}", f"TopRecoSol__{variation}.first.Wm.Phi()", eras=[era]),
                Define(f"tr_Wm_mass__{variation}", f"TopRecoSol__{variation}.first.Wm.M()", eras=[era]),
                Define(f"tr_antib_pt__{variation}", f"TopRecoSol__{variation}.first.antib.Pt()", eras=[era]),
                Define(f"tr_antib_eta__{variation}", f"TopRecoSol__{variation}.first.antib.Eta()", eras=[era]),
                Define(f"tr_antib_phi__{variation}", f"TopRecoSol__{variation}.first.antib.Phi()", eras=[era]),
                Define(f"tr_antib_mass__{variation}", f"TopRecoSol__{variation}.first.antib.M()", eras=[era]),
                Define(f"tr_lep_pt__{variation}", f"TopRecoSol__{variation}.first.lep.Pt()", eras=[era]),
                Define(f"tr_lep_eta__{variation}", f"TopRecoSol__{variation}.first.lep.Eta()", eras=[era]),
                Define(f"tr_lep_phi__{variation}", f"TopRecoSol__{variation}.first.lep.Phi()", eras=[era]),
                Define(f"tr_lep_mass__{variation}", f"TopRecoSol__{variation}.first.lep.M()", eras=[era]),
                Define(f"tr_antinu_pt__{variation}", f"TopRecoSol__{variation}.first.antinu.Pt()", eras=[era]),
                Define(f"tr_antinu_eta__{variation}", f"TopRecoSol__{variation}.first.antinu.Eta()", eras=[era]),
                Define(f"tr_antinu_phi__{variation}", f"TopRecoSol__{variation}.first.antinu.Phi()", eras=[era]),
                Define(f"tr_antinu_mass__{variation}", f"TopRecoSol__{variation}.first.antinu.M()", eras=[era]),

                Define(f"tr_ttbar_p4__{variation}", f"ROOT::Math::PtEtaPhiMVector(tr_Top_pt__{variation}, tr_Top_eta__{variation}, tr_Top_phi__{variation}, tr_Top_mass__{variation}) +"
                    f"ROOT::Math::PtEtaPhiMVector(tr_AntiTop_pt__{variation}, tr_AntiTop_eta__{variation}, tr_AntiTop_phi__{variation}, tr_AntiTop_mass__{variation})", eras=[era]),

                Define(f"tr_ttbar_pt__{variation}", f"tr_ttbar_p4__{variation}.Pt()", eras=[era]),
                Define(f"tr_ttbar_eta__{variation}", f"tr_ttbar_p4__{variation}.Eta()", eras=[era]),
                Define(f"tr_ttbar_phi__{variation}", f"tr_ttbar_p4__{variation}.Phi()", eras=[era]),
                Define(f"tr_ttbar_mass__{variation}", f"tr_ttbar_p4__{variation}.M()", eras=[era]),

            ]            
