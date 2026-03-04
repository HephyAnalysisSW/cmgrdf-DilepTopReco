from CMGRDF.flow import Define
from CMGRDF.collectionUtils import DefineP4
from CMGRDF.cms.eras import run2eras
from utils.jmeUncertainties import jme_variation_names, met_variation_names

p4_reconstruction_sequence_nominal = [
    # make 4-momenta of all the necessary objects
    DefineP4("SelJet"),
]

p4_reconstruction_sequences_variations = []

for era in run2eras:
    for var in jme_variation_names[era]:
        for direction in ["up", "down"]:
            
            variation = f"{var}_{direction}"

            p4_reconstruction_sequences_variations.append(DefineP4(f"SelJet__{variation}", eras=[era], onData=False, onDataDriven=False))

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

    # sqrts defined in the main body
    Define("x1_norecoil", "(tr_ttbar_p4.E() + tr_ttbar_p4.Pz()) / (sqrts)"),
    Define("x2_norecoil", "(tr_ttbar_p4.E() - tr_ttbar_p4.Pz()) / (sqrts)"),

    # reconstructing extra jets to improve x1 and x2 reconstruction
    # from TOP-20-006: "requirements on pT and isolation of extra jets eliminate the expected contributions from
    #  gluons radiated off b quarks produced in the top quark decays"
    Define("SelJet_isExtra", "SelJet_pt > 40 && "
           "cleanByDR(SelJet_eta, SelJet_phi, ROOT::RVecD({tr_b_eta}), ROOT::RVecD({tr_b_phi}), 0.8) && "
           "cleanByDR(SelJet_eta, SelJet_phi, ROOT::RVecD({tr_antib_eta}), ROOT::RVecD({tr_antib_phi}), 0.8)"),    
    
    Define("ExtraJet_p4", "SelJet_p4[SelJet_isExtra]"),

    # initializing sum explicitly because automatic type inference is failing in this case
    Define("recoil_p4", "Sum<ROOT::Math::PtEtaPhiMVector>(ExtraJet_p4,ROOT::Math::PtEtaPhiMVector(0.0,0.0,0.0,0.0))"),

    Define("x1_withrecoil", "(tr_ttbar_p4.E() + recoil_p4.E() + (tr_ttbar_p4.Pz() + recoil_p4.Pz()) ) / (sqrts)"),
    Define("x2_withrecoil", "(tr_ttbar_p4.E() + recoil_p4.E() - (tr_ttbar_p4.Pz() + recoil_p4.Pz()) ) / (sqrts)"),

]

# keeping it out to avoid issues with f-string formatting
default_top_reco_string = "std::pair<TopRecoSolution,std::pair<size_t,size_t>> {TopRecoSolution(),{0,0}}"

top_reconstruction_sequences_jme_variations = []

# warning for maximum recursion depth exceeded ?
for era in run2eras:
    for var in jme_variation_names[era]:
        for direction in ["up", "down"]:
            
            variation = f"{var}_{direction}"

            top_reconstruction_sequences_jme_variations += [
                
                Define(f"TopRecoSol__{variation}", "(nLepton_good >= 2) ? topreco_solution(topreco, ROOT::Math::PxPyPzEVector(Lepton_good_p4[Lepton_idx]), ROOT::Math::PxPyPzEVector(Lepton_good_p4[Antilepton_idx]),"
                    f"SelJet__{variation}_p4, SelJet__{variation}_bTagged, MET_pt__{variation}, MET_phi__{variation}) : {default_top_reco_string}", eras=[era], onData=False, onDataDriven=False),

                Define(f"tr_isvalid__{variation}", f"TopRecoSol__{variation}.first.valid", eras=[era], onData=False, onDataDriven=False),

                Define(f"tr_Top_pt__{variation}", f"TopRecoSol__{variation}.first.top.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Top_eta__{variation}", f"TopRecoSol__{variation}.first.top.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Top_phi__{variation}", f"TopRecoSol__{variation}.first.top.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Top_mass__{variation}", f"TopRecoSol__{variation}.first.top.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wp_pt__{variation}", f"TopRecoSol__{variation}.first.Wp.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wp_eta__{variation}", f"TopRecoSol__{variation}.first.Wp.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wp_phi__{variation}", f"TopRecoSol__{variation}.first.Wp.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wp_mass__{variation}", f"TopRecoSol__{variation}.first.Wp.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_b_pt__{variation}", f"TopRecoSol__{variation}.first.b.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_b_eta__{variation}", f"TopRecoSol__{variation}.first.b.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_b_phi__{variation}", f"TopRecoSol__{variation}.first.b.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_b_mass__{variation}", f"TopRecoSol__{variation}.first.b.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antilep_pt__{variation}", f"TopRecoSol__{variation}.first.antilep.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antilep_eta__{variation}", f"TopRecoSol__{variation}.first.antilep.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antilep_phi__{variation}", f"TopRecoSol__{variation}.first.antilep.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antilep_mass__{variation}", f"TopRecoSol__{variation}.first.antilep.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_nu_pt__{variation}", f"TopRecoSol__{variation}.first.nu.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_nu_eta__{variation}", f"TopRecoSol__{variation}.first.nu.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_nu_phi__{variation}", f"TopRecoSol__{variation}.first.nu.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_nu_mass__{variation}", f"TopRecoSol__{variation}.first.nu.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_AntiTop_pt__{variation}", f"TopRecoSol__{variation}.first.antitop.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_AntiTop_eta__{variation}", f"TopRecoSol__{variation}.first.antitop.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_AntiTop_phi__{variation}", f"TopRecoSol__{variation}.first.antitop.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_AntiTop_mass__{variation}", f"TopRecoSol__{variation}.first.antitop.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wm_pt__{variation}", f"TopRecoSol__{variation}.first.Wm.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wm_eta__{variation}", f"TopRecoSol__{variation}.first.Wm.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wm_phi__{variation}", f"TopRecoSol__{variation}.first.Wm.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wm_mass__{variation}", f"TopRecoSol__{variation}.first.Wm.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antib_pt__{variation}", f"TopRecoSol__{variation}.first.antib.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antib_eta__{variation}", f"TopRecoSol__{variation}.first.antib.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antib_phi__{variation}", f"TopRecoSol__{variation}.first.antib.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antib_mass__{variation}", f"TopRecoSol__{variation}.first.antib.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_lep_pt__{variation}", f"TopRecoSol__{variation}.first.lep.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_lep_eta__{variation}", f"TopRecoSol__{variation}.first.lep.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_lep_phi__{variation}", f"TopRecoSol__{variation}.first.lep.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_lep_mass__{variation}", f"TopRecoSol__{variation}.first.lep.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antinu_pt__{variation}", f"TopRecoSol__{variation}.first.antinu.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antinu_eta__{variation}", f"TopRecoSol__{variation}.first.antinu.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antinu_phi__{variation}", f"TopRecoSol__{variation}.first.antinu.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antinu_mass__{variation}", f"TopRecoSol__{variation}.first.antinu.M()", eras=[era], onData=False, onDataDriven=False),

                Define(f"tr_ttbar_p4__{variation}", f"ROOT::Math::PtEtaPhiMVector(tr_Top_pt__{variation}, tr_Top_eta__{variation}, tr_Top_phi__{variation}, tr_Top_mass__{variation}) +"
                    f"ROOT::Math::PtEtaPhiMVector(tr_AntiTop_pt__{variation}, tr_AntiTop_eta__{variation}, tr_AntiTop_phi__{variation}, tr_AntiTop_mass__{variation})", eras=[era], onData=False, onDataDriven=False),

                Define(f"tr_ttbar_pt__{variation}", f"tr_ttbar_p4__{variation}.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_ttbar_eta__{variation}", f"tr_ttbar_p4__{variation}.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_ttbar_phi__{variation}", f"tr_ttbar_p4__{variation}.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_ttbar_mass__{variation}", f"tr_ttbar_p4__{variation}.M()", eras=[era], onData=False, onDataDriven=False),

                Define(f"x1_norecoil__{variation}", f"(tr_ttbar_p4__{variation}.E() + tr_ttbar_p4__{variation}.Pz()) / (sqrts)", eras=[era], onData=False, onDataDriven=False),
                Define(f"x2_norecoil__{variation}", f"(tr_ttbar_p4__{variation}.E() - tr_ttbar_p4__{variation}.Pz()) / (sqrts)", eras=[era], onData=False, onDataDriven=False),

                # reconstructing extra jets to improve x1 and x2 reconstruction
                # from TOP-20-006: "requirements on pT and isolation of extra jets eliminate the expected contributions from
                #  gluons radiated off b quarks produced in the top quark decays"
                Define(f"SelJet__{variation}_isExtra", f"SelJet__{variation}_pt > 40 && "
                    f"cleanByDR(SelJet__{variation}_eta, SelJet__{variation}_phi, ROOT::RVecD({{tr_b_eta__{variation}}}), ROOT::RVecD({{tr_b_phi__{variation}}}), 0.8) && "
                    f"cleanByDR(SelJet__{variation}_eta, SelJet__{variation}_phi, ROOT::RVecD({{tr_antib_eta__{variation}}}), ROOT::RVecD({{tr_antib_phi__{variation}}}), 0.8)", eras=[era], onData=False, onDataDriven=False),    

                Define(f"ExtraJet__{variation}_p4", f"SelJet__{variation}_p4[SelJet__{variation}_isExtra]", eras=[era], onData=False, onDataDriven=False),

                # # initializing sum explicitly because automatic type inference is failing in this case
                Define(f"recoil__{variation}_p4", f"Sum<ROOT::Math::PtEtaPhiMVector>(ExtraJet__{variation}_p4,ROOT::Math::PtEtaPhiMVector(0.0,0.0,0.0,0.0))", eras=[era], onData=False, onDataDriven=False),

                Define(f"x1_withrecoil__{variation}", f"(tr_ttbar_p4__{variation}.E() + recoil__{variation}_p4.E() + (tr_ttbar_p4__{variation}.Pz() + recoil_p4.Pz()) ) / (sqrts)", eras=[era], onData=False, onDataDriven=False),
                Define(f"x2_withrecoil__{variation}", f"(tr_ttbar_p4__{variation}.E() + recoil__{variation}_p4.E() - (tr_ttbar_p4__{variation}.Pz() + recoil__{variation}_p4.Pz()) ) / (sqrts)", eras=[era], onData=False, onDataDriven=False),

            ]

for era in run2eras:
    # unclustered MET variations for now, can add more later
    for var in met_variation_names[era]:
        for direction in ["up", "down"]:
            
            variation = f"{var}_{direction}"

            top_reconstruction_sequences_jme_variations += [
            
                Define(f"TopRecoSol__{variation}", "(nLepton_good >= 2) ? topreco_solution(topreco, ROOT::Math::PxPyPzEVector(Lepton_good_p4[Lepton_idx]), ROOT::Math::PxPyPzEVector(Lepton_good_p4[Antilepton_idx]),"
                    f"SelJet_p4, SelJet_bTagged, MET_pt__{variation}, MET_phi__{variation}) : {default_top_reco_string}", eras=[era], onData=False, onDataDriven=False),

                Define(f"tr_isvalid__{variation}", f"TopRecoSol__{variation}.first.valid", eras=[era], onData=False, onDataDriven=False),

                Define(f"tr_Top_pt__{variation}", f"TopRecoSol__{variation}.first.top.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Top_eta__{variation}", f"TopRecoSol__{variation}.first.top.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Top_phi__{variation}", f"TopRecoSol__{variation}.first.top.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Top_mass__{variation}", f"TopRecoSol__{variation}.first.top.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wp_pt__{variation}", f"TopRecoSol__{variation}.first.Wp.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wp_eta__{variation}", f"TopRecoSol__{variation}.first.Wp.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wp_phi__{variation}", f"TopRecoSol__{variation}.first.Wp.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wp_mass__{variation}", f"TopRecoSol__{variation}.first.Wp.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_b_pt__{variation}", f"TopRecoSol__{variation}.first.b.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_b_eta__{variation}", f"TopRecoSol__{variation}.first.b.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_b_phi__{variation}", f"TopRecoSol__{variation}.first.b.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_b_mass__{variation}", f"TopRecoSol__{variation}.first.b.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antilep_pt__{variation}", f"TopRecoSol__{variation}.first.antilep.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antilep_eta__{variation}", f"TopRecoSol__{variation}.first.antilep.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antilep_phi__{variation}", f"TopRecoSol__{variation}.first.antilep.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antilep_mass__{variation}", f"TopRecoSol__{variation}.first.antilep.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_nu_pt__{variation}", f"TopRecoSol__{variation}.first.nu.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_nu_eta__{variation}", f"TopRecoSol__{variation}.first.nu.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_nu_phi__{variation}", f"TopRecoSol__{variation}.first.nu.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_nu_mass__{variation}", f"TopRecoSol__{variation}.first.nu.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_AntiTop_pt__{variation}", f"TopRecoSol__{variation}.first.antitop.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_AntiTop_eta__{variation}", f"TopRecoSol__{variation}.first.antitop.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_AntiTop_phi__{variation}", f"TopRecoSol__{variation}.first.antitop.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_AntiTop_mass__{variation}", f"TopRecoSol__{variation}.first.antitop.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wm_pt__{variation}", f"TopRecoSol__{variation}.first.Wm.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wm_eta__{variation}", f"TopRecoSol__{variation}.first.Wm.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wm_phi__{variation}", f"TopRecoSol__{variation}.first.Wm.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_Wm_mass__{variation}", f"TopRecoSol__{variation}.first.Wm.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antib_pt__{variation}", f"TopRecoSol__{variation}.first.antib.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antib_eta__{variation}", f"TopRecoSol__{variation}.first.antib.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antib_phi__{variation}", f"TopRecoSol__{variation}.first.antib.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antib_mass__{variation}", f"TopRecoSol__{variation}.first.antib.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_lep_pt__{variation}", f"TopRecoSol__{variation}.first.lep.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_lep_eta__{variation}", f"TopRecoSol__{variation}.first.lep.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_lep_phi__{variation}", f"TopRecoSol__{variation}.first.lep.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_lep_mass__{variation}", f"TopRecoSol__{variation}.first.lep.M()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antinu_pt__{variation}", f"TopRecoSol__{variation}.first.antinu.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antinu_eta__{variation}", f"TopRecoSol__{variation}.first.antinu.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antinu_phi__{variation}", f"TopRecoSol__{variation}.first.antinu.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_antinu_mass__{variation}", f"TopRecoSol__{variation}.first.antinu.M()", eras=[era], onData=False, onDataDriven=False),

                Define(f"tr_ttbar_p4__{variation}", f"ROOT::Math::PtEtaPhiMVector(tr_Top_pt__{variation}, tr_Top_eta__{variation}, tr_Top_phi__{variation}, tr_Top_mass__{variation}) +"
                    f"ROOT::Math::PtEtaPhiMVector(tr_AntiTop_pt__{variation}, tr_AntiTop_eta__{variation}, tr_AntiTop_phi__{variation}, tr_AntiTop_mass__{variation})", eras=[era], onData=False, onDataDriven=False),

                Define(f"tr_ttbar_pt__{variation}", f"tr_ttbar_p4__{variation}.Pt()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_ttbar_eta__{variation}", f"tr_ttbar_p4__{variation}.Eta()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_ttbar_phi__{variation}", f"tr_ttbar_p4__{variation}.Phi()", eras=[era], onData=False, onDataDriven=False),
                Define(f"tr_ttbar_mass__{variation}", f"tr_ttbar_p4__{variation}.M()", eras=[era], onData=False, onDataDriven=False),

                Define(f"x1_norecoil__{variation}", f"(tr_ttbar_p4__{variation}.E() + tr_ttbar_p4__{variation}.Pz()) / (sqrts)", eras=[era], onData=False, onDataDriven=False),
                Define(f"x2_norecoil__{variation}", f"(tr_ttbar_p4__{variation}.E() - tr_ttbar_p4__{variation}.Pz()) / (sqrts)", eras=[era], onData=False, onDataDriven=False),

                # Using nominal selected jets since these are not changed by MET variations
                Define(f"SelJet__{variation}_isExtra", f"SelJet_pt > 40 && "
                    f"cleanByDR(SelJet_eta, SelJet_phi, ROOT::RVecD({{tr_b_eta__{variation}}}), ROOT::RVecD({{tr_b_phi__{variation}}}), 0.8) && "
                    f"cleanByDR(SelJet_eta, SelJet_phi, ROOT::RVecD({{tr_antib_eta__{variation}}}), ROOT::RVecD({{tr_antib_phi__{variation}}}), 0.8)", eras=[era], onData=False, onDataDriven=False),    

                Define(f"ExtraJet__{variation}_p4", f"SelJet_p4[SelJet__{variation}_isExtra]", eras=[era], onData=False, onDataDriven=False),

                # initializing sum explicitly because automatic type inference is failing in this case
                Define(f"recoil__{variation}_p4", f"Sum<ROOT::Math::PtEtaPhiMVector>(ExtraJet__{variation}_p4,ROOT::Math::PtEtaPhiMVector(0.0,0.0,0.0,0.0))", eras=[era], onData=False, onDataDriven=False),

                Define(f"x1_withrecoil__{variation}", f"(tr_ttbar_p4__{variation}.E() + recoil__{variation}_p4.E() + (tr_ttbar_p4__{variation}.Pz() + recoil_p4.Pz()) ) / (sqrts)", eras=[era], onData=False, onDataDriven=False),
                Define(f"x2_withrecoil__{variation}", f"(tr_ttbar_p4__{variation}.E() + recoil__{variation}_p4.E() - (tr_ttbar_p4__{variation}.Pz() + recoil__{variation}_p4.Pz()) ) / (sqrts)", eras=[era], onData=False, onDataDriven=False),
            ]            
