
import os
import ROOT
import pathlib
datadir = str(pathlib.Path(__file__).resolve().parent.parent / "data")
from CMGRDF.init import Declare
from CMGRDF.flow import Define
from CMGRDF.CorrectionlibFactory import CorrectionlibFactory
from CMGRDF.cms.eras import run2eras, run3eras
era_mapping = {
    "2022"   :  "2022_Summer22",
    "2022EE" :  "2022_Summer22EE",
    "2018"   :  "2018_UL",
    "2017"   :  "2017_UL",
    "2016"   :  "2016postVFP_UL",
    "2016APV":  "2016preVFP_UL",
}
lightSFperEra=dict( [ (era, 'light') for era in run3eras] + [ (era, 'incl') for era in run2eras] )
    
class BTagSFFixedWPDefine( Define ):
    def __init__(self, doSyst, jetCol="SelJet", disc="btagDeepFlavB", disc_json='deepJet',  **options):
        if len(options['eras']) != 1:
            raise RuntimeError("Can only use BTagSFFixedWPDefine for a single era")
        self.era=options['eras'][0]
        super().__init__( "btagSF_fixedWP_SF",
                          f"btagSF_fixedWP_<era>( {jetCol}_hadronFlavour, {jetCol}_pt, {jetCol}_eta, {jetCol}_{disc}, <syst>, <syst_flavor> )",
                          onData=False, onDataDriven=False, **options)
        self._fname = f"/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/{era_mapping[self.era]}/btagging.json.gz"
        self._fname_eff = f"{datadir}/btagging_eff_{self.era}.json.gz"
        self.disc_json=disc_json
        self.doSyst=doSyst
        self._init=False
    def init( self ):
        btagSF_heavy = CorrectionlibFactory.loadCorrector( self._fname    , f"{self.disc_json}_comb" , check=True)[0]
        btagSF_light = CorrectionlibFactory.loadCorrector( self._fname    , f"{self.disc_json}_{lightSFperEra[self.era]}", check=True)[0]
        btag_wps     = CorrectionlibFactory.loadCorrector( self._fname    , f"{self.disc_json}_wp_values", check=True)[0]
        eff_corr     = CorrectionlibFactory.loadCorrector( self._fname_eff, f"btageff", check=True)[0]
        # hardcoded to correct loose and medium. Can surely be done more general  
        to_declare='''float btagSF_fixedWP_<era>( const ROOT::RVec<int>& flavs, const ROOT::RVec<float>& pts, const ROOT::RVec<float>& etas, ROOT::RVec<float>& disc, std::string syst, std::string syst_flavor){
        float numerator=1.; float denominator=1.;
        vector<double> wp_s = { <CORRID_WP>->evaluate({"L"}),<CORRID_WP>->evaluate({"M"})};
        for (int ijet=0; ijet<flavs.size(); ++ijet){
            if (TMath::Abs( etas[ijet] ) > 2.4) continue;
            auto corr_set = (flavs[ijet] >= 4) ? <CORRID_H> : <CORRID_L>;
            std::string thesyst = syst;
            if (syst_flavor == "light" && flavs[ijet] >= 4) thesyst = "central";
            else if (syst_flavor == "heavy" && flavs[ijet] < 4) thesyst = "central";
            if (disc[ijet] < wp_s[0]){  // fails loose
                float sf_l = corr_set->evaluate({thesyst, "L", flavs[ijet], TMath::Abs( etas[ijet] ), pts[ijet]});
                float eff_l = <CORRID_EFF>->evaluate({"L", flavs[ijet], TMath::Abs(etas[ijet]), TMath::Min( float(999.), pts[ijet])});
                numerator  *= (1-eff_l*sf_l);
                denominator*= (1-eff_l);
            }
            else if ( disc[ijet] < wp_s[1]){ // passes loose but fails medium
                 float sf_l = corr_set->evaluate({thesyst, "L", flavs[ijet], TMath::Abs( etas[ijet] ), pts[ijet]});
                 float sf_m = corr_set->evaluate({thesyst, "M", flavs[ijet], TMath::Abs( etas[ijet] ), pts[ijet]});
                 float eff_l = <CORRID_EFF>->evaluate({"L", flavs[ijet], TMath::Abs(etas[ijet]), TMath::Min( float(999.), pts[ijet])});
                 float eff_m = <CORRID_EFF>->evaluate({"M", flavs[ijet], TMath::Abs(etas[ijet]), TMath::Min( float(999.), pts[ijet])});
                 numerator   *=(sf_l*eff_l - sf_m*eff_m);
                 denominator *=(eff_l - eff_m);
            }
            else{ // passes medium. dont correct for the tight here, but could be extended
                 float sf_m = corr_set->evaluate({thesyst, "M", flavs[ijet], TMath::Abs( etas[ijet] ), pts[ijet]});
                 float eff_m = <CORRID_EFF>->evaluate({"M", flavs[ijet], TMath::Abs(etas[ijet]), TMath::Min( float(999.), pts[ijet])});
                 numerator  *= eff_m*sf_m;
                 denominator*= eff_m;
            }
        }
        return numerator/denominator;
}'''.replace( "<CORRID_EFF>", eff_corr).replace( "<CORRID_WP>", btag_wps).replace( "<CORRID_H>", btagSF_heavy).replace( "<CORRID_L>", btagSF_light).replace("<era>", self.era)
        Declare(to_declare )
        Declare( '''ROOT::RVecF btagSF_fixedWP_<era>_syst( const ROOT::RVec<int>& flavs, const ROOT::RVec<float>& pts, const ROOT::RVec<float>& etas, ROOT::RVec<float>& disc, std::string syst, std::string syst_flavor){
        ROOT::RVecF ret={1.,1.};
        ret[0]=btagSF_fixedWP_<era>( flavs, pts, etas, disc, "up"   + syst, syst_flavor);
        ret[1]=btagSF_fixedWP_<era>( flavs, pts, etas, disc, "down" + syst, syst_flavor);
        return ret;
}'''.replace("<era>", self.era))
        
        self._init=True
    def _attach( self, rdf, withUncertainties):
        if not self._init:
            self.init()
        try:
            src = rdf
            rdf=rdf.Define(self.name, self.expr.replace("<syst>", '"central"').replace("<syst_flavor>", '""').replace("<era>", self.era))
            rdf._from = src
            if self.doSyst and withUncertainties:
                
                for flavor,systs in [ ('heavy', ['_correlated',"_uncorrelated"]), ( 'light', [ ""])]:
                    for syst in systs:
                        variationName=syst+( "_%s"%self.era if "uncorrelated" in syst else "")
                        src = rdf
                        # rdf=rdf.Vary( self.name,
                        #               self.expr.replace("<era>", f"{self.era}_syst").replace( "<syst_flavor>",f'"{flavor}"').replace("<syst>", f'"{syst}"'),
                        #               variationTags=['up', 'down'], variationName=f"CMS_eff_b{variationName}_{flavor}")
                        expr_syst = self.expr.replace("<era>", f"{self.era}_syst").replace( "<syst_flavor>",f'"{flavor}"').replace("<syst>", f'"{syst}"')
                        rdf = rdf.Define(f"{self.name}__CMS_eff_b{variationName}_{flavor}_SFUp", f"{expr_syst}[0]")
                        rdf = rdf.Define(f"{self.name}__CMS_eff_b{variationName}_{flavor}_SFDn", f"{expr_syst}[1]")
                        rdf._from = src
            return rdf
           
        
        except BaseException:
            print(f"ERROR attaching Define({self.name}, {self.expr}")
            raise
btagsf_sequences = [ BTagSFFixedWPDefine( True, eras=[era] ) for era in run2eras + run3eras]
