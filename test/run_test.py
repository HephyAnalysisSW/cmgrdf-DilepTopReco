from CMGRDF import *
import ROOT
ROOT.EnableImplicitMT(4)
from CMGRDF.collectionUtils import *
AddHeader("toprecofunctions.h","${CMGRDF}/../TopReco")

useHists = True
if useHists:
    f_hists_path = "${CMGRDF}/../test/kinreco.root"
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
else:
    load_reco = '''
TTDilepReconstruction topreco = TTDilepReconstruction();
    '''
    ProcessLine(load_reco)


P = localOrEOS("2018", "/scratch/gpetrucc/NanoTrees_TTH_v6", "/eos/cms/store/cmst3/group/tthlep/peruzzi/NanoTrees_TTH_091019_v6pre")
#PD = localOrEOS("2018", "/scratch/gpetrucc/NanoTrees_TTH_v6", "/eos/cms/store/cmst3/group/tthlep/peruzzi/NanoTrees_TTH_090120_v6_triggerFix")
#P = '/groups/hephy/cms/ang.li/topreco/'

data = [
    #Process("TT", [MCSample("TTJets_DiLepton", P + "/{name}.root", xsec="xsec", normUncertainty=1.3)], label="t#bar{t}", fillColor=ROOT.kOrange + 3, signal=True),
    Process("TT", [MCSample("TTJets_DiLepton", P + "/{name}.root", normUncertainty=1.3, genWeightName=None, xsec=None, weight="weight")], label="t#bar{t}", fillColor=ROOT.kOrange + 3, signal=True),
    #Process("TT", [MCSample("TTJets_DiLepton", P + "/NANOAOD_ttdilep.root", normUncertainty=1.3, genWeightName=None, xsec=None, weight="weight")], label="t#bar{t}", fillColor=ROOT.kOrange + 3, signal=True),
]
cuts = Flow("dilep",
            Define("weight","1"),
            #DefinePerSample("year","2018"), # already in NTuple
            #Define("year","2018"),
            Define("Jet_good", "Jet_pt > 30 && abs(Jet_eta) < 2.4"),
            Define("Jet_bMedium", "Jet_good && Jet_btagDeepFlavB >= deepFlavB_WPMedium(year)"),
            Define("nJet30", "Sum(Jet_good)"),
            Define("nBJet30", "Sum(Jet_bMedium)"),
            Cut("2j", "nJet30 >= 2"),
            DefineSkimmedCollection("JetGood", "Jet", ("pt", "eta", "phi", "mass", "btagDeepFlavB", "bMedium"), cut="Jet_good"),
            DefineSkimmedCollection("ElectronGood", "Electron", ("pt", "eta", "phi", "mass", "charge", "pdgId"), cut="Electron_pt>10 && Electron_mvaFall17V2noIso_WP90 && abs(Electron_dxy)<0.5 && abs(Electron_dz)<0.1"),
            DefineSkimmedCollection("MuonGood", "Muon", ("pt", "eta", "phi", "mass", "charge", "pdgId"), cut="Muon_pt>10 && Muon_mediumId && abs(Muon_dxy)<0.5 && abs(Muon_dz)<0.1"),
            Define("LeptonGood_pt_raw", "ROOT::VecOps::Concatenate(ElectronGood_pt,MuonGood_pt)"),
            Define("LeptonGood_eta_raw", "ROOT::VecOps::Concatenate(ElectronGood_eta,MuonGood_eta)"),
            Define("LeptonGood_phi_raw", "ROOT::VecOps::Concatenate(ElectronGood_phi,MuonGood_phi)"),
            Define("LeptonGood_mass_raw", "ROOT::VecOps::Concatenate(ElectronGood_mass,MuonGood_mass)"),
            Define("LeptonGood_charge_raw","ROOT::VecOps::Concatenate(ElectronGood_charge,MuonGood_charge)"),
            Define("LeptonGood_pdgId_raw","ROOT::VecOps::Concatenate(ElectronGood_pdgId,MuonGood_pdgId)"),
            Define("LeptonGood_ptsort_idx", "ROOT::VecOps::Argsort(LeptonGood_pt_raw)"),
            Define("LeptonGood_pt", "ROOT::VecOps::Take(LeptonGood_pt_raw,LeptonGood_ptsort_idx)"),
            Define("LeptonGood_eta", "ROOT::VecOps::Take(LeptonGood_eta_raw,LeptonGood_ptsort_idx)"),
            Define("LeptonGood_phi", "ROOT::VecOps::Take(LeptonGood_phi_raw,LeptonGood_ptsort_idx)"),
            Define("LeptonGood_mass", "ROOT::VecOps::Take(LeptonGood_mass_raw,LeptonGood_ptsort_idx)"),
            Define("LeptonGood_charge","ROOT::VecOps::Take(LeptonGood_charge_raw,LeptonGood_ptsort_idx)"),
            Define("LeptonGood_pdgId","ROOT::VecOps::Take(LeptonGood_pdgId_raw,LeptonGood_ptsort_idx)"),
            Define("LeptonGood0_p4", "LeptonGood_charge[0]==-1 ? makeP4_PxPyPzE(LeptonGood_pt[0],LeptonGood_eta[0],LeptonGood_phi[0],LeptonGood_mass[0]) : makeP4_PxPyPzE(LeptonGood_pt[1],LeptonGood_eta[1],LeptonGood_phi[1],LeptonGood_mass[1])"),
            Define("LeptonGood1_p4", "LeptonGood_charge[1]==1 ? makeP4_PxPyPzE(LeptonGood_pt[1],LeptonGood_eta[1],LeptonGood_phi[1],LeptonGood_mass[1]) : makeP4_PxPyPzE(LeptonGood_pt[0],LeptonGood_eta[0],LeptonGood_phi[0],LeptonGood_mass[0])"),
            Define("JetGood_p4", "makeP4_PxPyPzE(JetGood_pt,JetGood_eta,JetGood_phi,JetGood_mass)"),
            Define("TopRecoSol", "topreco_solution(topreco, LeptonGood0_p4, LeptonGood1_p4, JetGood_p4, JetGood_bMedium,MET_pt,MET_phi)"),
            Define("Have_TopReco", "TopRecoSol.first.valid"),
            Define("Top_pt", "TopRecoSol.first.top.Pt()"),
            Define("Top_eta", "TopRecoSol.first.top.Eta()"),
            Define("Top_phi", "TopRecoSol.first.top.Phi()"),
            Define("Top_mass", "TopRecoSol.first.top.M()"),
            Define("Wp_pt", "TopRecoSol.first.Wp.Pt()"),
            Define("Wp_eta", "TopRecoSol.first.Wp.Eta()"),
            Define("Wp_phi", "TopRecoSol.first.Wp.Phi()"),
            Define("Wp_mass", "TopRecoSol.first.Wp.M()"),
            Define("b_pt", "TopRecoSol.first.b.Pt()"),
            Define("b_eta", "TopRecoSol.first.b.Eta()"),
            Define("b_phi", "TopRecoSol.first.b.Phi()"),
            Define("b_mass", "TopRecoSol.first.b.M()"),
            Define("antilep_pt", "TopRecoSol.first.antilep.Pt()"),
            Define("antilep_eta", "TopRecoSol.first.antilep.Eta()"),
            Define("antilep_phi", "TopRecoSol.first.antilep.Phi()"),
            Define("antilep_mass", "TopRecoSol.first.antilep.M()"),
            Define("nu_pt", "TopRecoSol.first.nu.Pt()"),
            Define("nu_eta", "TopRecoSol.first.nu.Eta()"),
            Define("nu_phi", "TopRecoSol.first.nu.Phi()"),
            Define("nu_mass", "TopRecoSol.first.nu.M()"),
            Define("AntiTop_pt", "TopRecoSol.first.antitop.Pt()"),
            Define("AntiTop_eta", "TopRecoSol.first.antitop.Eta()"),
            Define("AntiTop_phi", "TopRecoSol.first.antitop.Phi()"),
            Define("AntiTop_mass", "TopRecoSol.first.antitop.M()"),
            Define("Wm_pt", "TopRecoSol.first.Wm.Pt()"),
            Define("Wm_eta", "TopRecoSol.first.Wm.Eta()"),
            Define("Wm_phi", "TopRecoSol.first.Wm.Phi()"),
            Define("Wm_mass", "TopRecoSol.first.Wm.M()"),
            Define("antib_pt", "TopRecoSol.first.antib.Pt()"),
            Define("antib_eta", "TopRecoSol.first.antib.Eta()"),
            Define("antib_phi", "TopRecoSol.first.antib.Phi()"),
            Define("antib_mass", "TopRecoSol.first.antib.M()"),
            Define("lep_pt", "TopRecoSol.first.lep.Pt()"),
            Define("lep_eta", "TopRecoSol.first.lep.Eta()"),
            Define("lep_phi", "TopRecoSol.first.lep.Phi()"),
            Define("lep_mass", "TopRecoSol.first.lep.M()"),
            Define("antinu_pt", "TopRecoSol.first.antinu.Pt()"),
            Define("antinu_eta", "TopRecoSol.first.antinu.Eta()"),
            Define("antinu_phi", "TopRecoSol.first.antinu.Phi()"),
            Define("antinu_mass", "TopRecoSol.first.antinu.M()"),
            )

lumi = 59.

if __name__ == "__main__":
    from CMGRDF.cmdline import processorFromCommandLineArgs
    maker, args = processorFromCommandLineArgs()
    maker.book(data, lumi, cuts, Snapshot('./test.root', columnSel=['#old', '#new'], columnVeto=['TopRecoSol','JetGood_p4','LeptonGood*_raw','LeptonGood0_p4','LeptonGood1_p4']), withUncertainties=False)

    report = maker.runSnapshots()
    snapshotReport = ["Snapshoted at ./test.root"]
    for key, snap in report:
        snapshotReport.append("%-10s  %-20s : %10u entries  %9.3f GB   %s" % (key.process, key.sample, snap.entries, snap.size / (1024.**3), snap.fname))
    print("\n".join(snapshotReport))
    with open("./snapReport.txt", "w") as snapshotReportFile:
        snapshotReportFile.write("\n".join(snapshotReport))

