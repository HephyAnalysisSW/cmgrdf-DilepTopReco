# JetVetoMapDefine.py
# implements JetVetoMapCut but as a flag (Define)

from CMGRDF.CorrectionlibFactory import CorrectionlibFactory
from CMGRDF.flow import Define
from CMGRDF.init import Declare
from CMSJMECalculators import loadJMESystematicsCalculators  # type: ignore

loadJMESystematicsCalculators()

# from CMGRDF.cms.jmeUncertainties import jetVetoTags, jsonMap

JME_corrections_folder = '/cvmfs/cms-griddata.cern.ch/cat/metadata/JME/'

jsonMap = {
    "2022EE": "Run3-22EFGSep23-Summer22EE-NanoAODv12",
    "2022": "Run3-22CDSep23-Summer22-NanoAODv12",
    "2018": "Run2-2018-UL-NanoAODv9",
    "2017": "Run2-2017-UL-NanoAODv9",
    "2016": "Run2-2016postVFP-UL-NanoAODv9",
    "2016APV": "Run2-2016preVFP-UL-NanoAODv9"

}


jetVetoTags = {
    "2016APV": "Summer19UL16_V1",
    "2016": "Summer19UL16_V1",  # same for APV and non-APV eras (see https://cms-jerc.web.cern.ch/Recommendations/#run-2_2)
    "2017": "Summer19UL17_V1",
    "2018": "Summer19UL18_V1",
    "2022": "Summer22_23Sep2023_RunCD_V1",
    "2022EE": "Summer22EE_23Sep2023_RunEFG_V1",
}


class JetVetoMapDefine(Define):
    def __init__(self, cutName, **options):
        if len(options['eras']) != 1:
            raise RuntimeError("You can only call JetVetoMapDefine for one era")
        self.era = options['eras'][0]

        super().__init__(
            cutName, f"passesJetVetoMap_{self.era}(Jet_pt, Jet_eta, Jet_phi, Jet_jetId, Jet_neEmEF, Jet_neHEF, Muon_eta, Muon_phi, Muon_isPFcand)", **options)

        self._fname = f"{JME_corrections_folder}/{jsonMap[self.era]}/latest/jetvetomaps.json.gz"
        self._corrName = jetVetoTags[self.era]
        self._init = False

    def init(self):
        vetoMapId = CorrectionlibFactory.loadCorrector(self._fname, self._corrName, check=True)[0]
        Declare('''bool passesJetVetoMap_<era>(const ROOT::RVec<float> & Jet_pt, const ROOT::RVec<float> & Jet_eta,
                                                    const ROOT::RVec<float> & Jet_phi, const ROOT::RVec<int> & Jet_jetId,
                                                    const ROOT::RVec<float> & Jet_neEmEF, const ROOT::RVec<float> & Jet_neHEF,
                                                    const ROOT::RVec<float> & Muon_eta, const ROOT::RVec<float> & Muon_phi, const ROOT::RVec<int> & Muon_isPFcand) {
        bool ret=true;
        for (int ijet=0; ijet<Jet_pt.size(); ++ijet){
             if (<correctionname>->evaluate({"jetvetomap", TMath::Max( -5.0f, TMath::Min(5.0f, Jet_eta.at(ijet))), TMath::Max( -3.14f, TMath::Min(3.14f, Jet_phi.at(ijet)))}) == 0) continue;
             if (Jet_pt.at(ijet) < 15.) continue;
             if (Jet_jetId.at(ijet) < 2) continue;
             if (Jet_neEmEF.at(ijet)+Jet_neHEF.at(ijet) > 0.9) continue;
             bool overlaps=false;
             for (int imuo=0; imuo<Muon_eta.size(); ++imuo){ // see if it overlaps with a PF muon
                 if ( deltaR2(Muon_eta.at(imuo), Muon_phi.at(imuo), Jet_eta.at(ijet), Jet_phi.at(ijet)) > 0.04) continue;
                 if ( !Muon_isPFcand.at(imuo) ) continue;
                 overlaps=true;
                 break;
             }
             if (!overlaps) ret=false;
             if (!ret) break;
        }
        return ret;
}'''.replace("<era>", self.era).replace("<correctionname>", vetoMapId))
        self._init = True

    def _attach(self, rdf, withUncertainties):
        if not self._init:
            self.init()
        return super()._attach(rdf, withUncertainties)
