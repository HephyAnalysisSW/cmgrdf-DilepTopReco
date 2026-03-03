# Dileptonic top reconstruction 

The algorithm is based on [Sonnenschein’s paper](https://arxiv.org/abs/hep-ph/0603011) with the following features:
- The reconstruction works only for events with at least two leptons
- For each event, run the reconstruction 100 times and take the weighted average as the final result
- For each reconstruction, the energy and momenta direction of jets and leptons are smeared; the W and t masses are randomly sampled from the corresponding Breit-Wigner distributions

The implementation is adopted from the [pepper framework](https://gitlab.cern.ch/pepper/pepper/-/blob/master/pepper/kinreco_sonnenschein.py?ref_type=heads).

# How to use:

## Code structure:

- The main algorithm is implemented in [TopReco/TopReco.h](https://github.com/HephyAnalysisSW/cmgrdf-DilepTopReco/blob/main/TopReco/TopReco.h)
  - `class TopRecoSolution` is the object of the result of the top reconstruction
  - `class TTDilepReconstruction` is the object the performs the top reconstruction
- The algorithm can be used in function `topreco_solution` [TopReco/toprecofunctions.h](https://github.com/HephyAnalysisSW/cmgrdf-DilepTopReco/blob/main/TopReco/toprecofunctions.h)
- Input:
    - The object of `class TTDilepReconstruction`
    - 4 vectors (ROOT::Math::PxPyPzEVector) of leptons and jets
    - b taggings of jets (bool)
    - MET_pt and MET_phi
    - Masses and width of W+, W-, top, and antitop
- Output:
    - A `std::pair` that includes the reconstruction result (first) and jet indices used in the reconstruction (second)


## Example to run in RDataFrame

- Include the C++ helper functions [TopReco/toprecofunctions.h](https://github.com/HephyAnalysisSW/cmgrdf-DilepTopReco/blob/main/TopReco/toprecofunctions.h)
```
# include C++ helper functions
import ROOT
ROOT.gInterpreter.Declare('#include "/path/to/TopReco/toprecofunctions.h"')
```
- Initialize the reconstruction tools:
  - To run reconstructions multiple times with smearing:
```
# To run reco with smearings
f_hists_path = "/groups/hephy/cms/ang.li/topreco/kinreco.root"
f_hists = ROOT.TFile.Open(f_hists_path)

load_hists = '''
auto h_mlb = mlb; h_mlb->SetDirectory(0);
auto h_energyfj = energyfj; h_energyfj->SetDirectory(0);
auto h_alphafj = alphaj; h_alphafj->SetDirectory(0);
auto h_energyfl = energyfl; h_energyfl->SetDirectory(0);
auto h_alphafl = alphal; h_alphafl->SetDirectory(0);
'''

load_reco = '''
TTDilepReconstruction topreco = TTDilepReconstruction(100); # run reconstruction 100 times
topreco.SetH_MLB(h_mlb);
topreco.SetH_JetEnergy(h_energyfj);
topreco.SetH_JetAngle(h_alphafj);
topreco.SetH_LepEnergy(h_energyfl);
topreco.SetH_LepAngle(h_alphafl);
'''
ROOT.gInterpreter.ProcessLine(load_hists+load_reco)
f_hists.Close()
```
  - To run reconstruction only once without smearing:
```
load_reco = '''
TTDilepReconstruction topreco = TTDilepReconstruction();
'''
ROOT.gInterpreter.ProcessLine(load_reco)
```

- Define new columns with top reconstruction:
```
d = d.Define("TopRecoSol", "topreco_solution(topreco, LeptonGood0_p4, LeptonGood1_p4, JetGood_p4, JetGood_bMedium,MET_pt,MET_phi)"),
d = d.Define("Have_TopReco", "TopRecoSol.first.valid"),
d = d.Define("Top_pt", "TopRecoSol.first.top.Pt()"),
d = d.Define("Top_eta", "TopRecoSol.first.top.Eta()"),
d = d.Define("Top_phi", "TopRecoSol.first.top.Phi()"),
d = d.Define("Top_mass", "TopRecoSol.first.top.M()"),
d = d.Define("Wp_pt", "TopRecoSol.first.Wp.Pt()"),
d = d.Define("Wp_eta", "TopRecoSol.first.Wp.Eta()"),
d = d.Define("Wp_phi", "TopRecoSol.first.Wp.Phi()"),
d = d.Define("Wp_mass", "TopRecoSol.first.Wp.M()"),
d = d.Define("b_pt", "TopRecoSol.first.b.Pt()"),
d = d.Define("b_eta", "TopRecoSol.first.b.Eta()"),
d = d.Define("b_phi", "TopRecoSol.first.b.Phi()"),
d = d.Define("b_mass", "TopRecoSol.first.b.M()"),
d = d.Define("antilep_pt", "TopRecoSol.first.antilep.Pt()"),
d = d.Define("antilep_eta", "TopRecoSol.first.antilep.Eta()"),
d = d.Define("antilep_phi", "TopRecoSol.first.antilep.Phi()"),
d = d.Define("antilep_mass", "TopRecoSol.first.antilep.M()"),
d = d.Define("nu_pt", "TopRecoSol.first.nu.Pt()"),
d = d.Define("nu_eta", "TopRecoSol.first.nu.Eta()"),
d = d.Define("nu_phi", "TopRecoSol.first.nu.Phi()"),
d = d.Define("nu_mass", "TopRecoSol.first.nu.M()"),
d = d.Define("AntiTop_pt", "TopRecoSol.first.antitop.Pt()"),
d = d.Define("AntiTop_eta", "TopRecoSol.first.antitop.Eta()"),
d = d.Define("AntiTop_phi", "TopRecoSol.first.antitop.Phi()"),
d = d.Define("AntiTop_mass", "TopRecoSol.first.antitop.M()"),
d = d.Define("Wm_pt", "TopRecoSol.first.Wm.Pt()"),
d = d.Define("Wm_eta", "TopRecoSol.first.Wm.Eta()"),
d = d.Define("Wm_phi", "TopRecoSol.first.Wm.Phi()"),
d = d.Define("Wm_mass", "TopRecoSol.first.Wm.M()"),
d = d.Define("antib_pt", "TopRecoSol.first.antib.Pt()"),
d = d.Define("antib_eta", "TopRecoSol.first.antib.Eta()"),
d = d.Define("antib_phi", "TopRecoSol.first.antib.Phi()"),
d = d.Define("antib_mass", "TopRecoSol.first.antib.M()"),
d = d.Define("lep_pt", "TopRecoSol.first.lep.Pt()"),
d = d.Define("lep_eta", "TopRecoSol.first.lep.Eta()"),
d = d.Define("lep_phi", "TopRecoSol.first.lep.Phi()"),
d = d.Define("lep_mass", "TopRecoSol.first.lep.M()"),
d = d.Define("antinu_pt", "TopRecoSol.first.antinu.Pt()"),
d = d.Define("antinu_eta", "TopRecoSol.first.antinu.Eta()"),
d = d.Define("antinu_phi", "TopRecoSol.first.antinu.Phi()"),
d = d.Define("antinu_mass", "TopRecoSol.first.antinu.M()"),
```
- Make histograms (RDataFrame::Histos1D, ...) or save as a new ntuple (RDataFrame::Snapshot).

## Example to run in CMGRDF

Set up a EL9 container (e.g. if not running on LXPLUS) and link the necessary packages - needs to be done every time:
```
cmssw-el9
source /cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc14-opt/setup.sh
```
Install the package (to be done for only once):

- clone the package and all submodules recursively with `git clone --recursive git@github.com:HephyAnalysisSW/cmgrdf-DilepTopReco.git`
- follow the instructions in `cmgrdf-prototype/README.md`

Set the environment variables (needs to be done every time):
```
cd cmgrdf-DilepTopReco/cmgrdf-prototype
eval $(make env)
cd ..
```

### Analysis-level example with object selection and event scale factors, including systematics

`run_test_with_systs.py` is an example to produce MC and data ntuples similar to what one would use in an analysis.

It includes reasonable selections on physics objects mostly based on the ones from TOP-20-006.

A large set of systematics is included, following recommendations from the CMS Top Systematics TWiki <https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopSystematics>:
- muon ID and isolation SF
- electron SF
- jet PU ID SF
- pileup SF
- b-tagging SF
- JES + JER, applied to both jets and MET (from Type-1 corrections)
- Unclustered MET

Impact of JES and JER on jets and MET + unclustered MET variations propagated to Top reconstruction.
- Snapshot with Vary'ed quantities currently not working, so variations are propagated by hand using Define in `utils/top_reco_sequences.py`

To be added:
- DCTR reweighting for hdamp variations
- Top pt reweighting
- Muon SF uncertainty split into stat and syst components
- trigger SFs + uncertainties
- b-tagging efficiencies in dileptonic ttbar phase space (currently using efficiencies from ttZ events)

To run `run_test_with_systs.py` including RDataFrame event-based multi-threading (highly recommended) with e.g. 8 threads, run:
```
python run_test_with_systs.py -j 8
```

Systematics are included by default in this example (see the `maker.book(...)` call at the end). If you want to just have the nominal branches, remove `withUncertainties=True`. In this case, if you want to add systematics via a flag, run the script with `-u` at the end.